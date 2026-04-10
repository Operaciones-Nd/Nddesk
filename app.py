from flask import Flask, redirect, url_for
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from models import db
from controllers import auth_bp, solicitudes_bp, usuarios_bp, turnos_bp
from controllers.solicitudes_datatable_controller import solicitudes_dt_bp
from controllers.sla_controller import sla_bp
from controllers.escalamiento_controller import escalamiento_bp
from controllers.kb_controller import kb_bp
from controllers.flujo_controller import flujo_bp
from controllers.cambios_ia_controller import cambios_ia_bp
from controllers.chat_controller import chat_bp
from controllers.workflow_controller import workflow_bp
from controllers.secciones_controller import secciones_bp
from controllers.departamentos_controller import departamentos_bp
from controllers.servicios_controller import servicios_bp
from controllers.subcategorias_controller import subcategorias_bp
from controllers.reports_controller import reports_bp
from config_app import get_config
from sqlalchemy.exc import OperationalError
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

def create_app(config_name=None):
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(get_config())
    
    # CSRF Protection
    csrf = CSRFProtect(app)
    app.config['WTF_CSRF_ENABLED'] = False  # Desactivado
    csrf.exempt(solicitudes_dt_bp)
    csrf.exempt(chat_bp)
    
    # Logging seguro
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Handler principal
        file_handler = RotatingFileHandler(
            'logs/tickets.log', 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=30
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Handler de errores
        error_handler = RotatingFileHandler(
            'logs/errors.log',
            maxBytes=10*1024*1024,
            backupCount=10
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s'
        ))
        app.logger.addHandler(error_handler)
        
        # Handler de seguridad
        security_handler = RotatingFileHandler(
            'logs/security.log',
            maxBytes=10*1024*1024,
            backupCount=50
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s [SECURITY] [%(filename)s:%(lineno)d] - %(message)s'
        ))
        app.logger.addHandler(security_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Sistema de tickets iniciado')
    
    # Encabezados de seguridad
    if config_name == 'production':
        csp = {
            'default-src': "'self'",
            'script-src': ["'self'", "'unsafe-inline'", 'cdn.jsdelivr.net', 'cdn.datatables.net'],
            'style-src': ["'self'", "'unsafe-inline'", 'fonts.googleapis.com', 'cdn.datatables.net'],
            'font-src': ["'self'", 'fonts.gstatic.com'],
            'img-src': ["'self'", 'data:'],
        }
        Talisman(app, 
                 content_security_policy=csp,
                 force_https=True,
                 strict_transport_security=True,
                 session_cookie_secure=True)
    
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        if config_name == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        return response
    
    # Manejo de errores seguro
    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning(f'404 error: {error}')
        return redirect(url_for('solicitudes.index'))
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Error interno: {error}')
        db.session.rollback()
        return "Error interno del servidor", 500
    
    @app.errorhandler(OperationalError)
    def handle_db_lock(error):
        app.logger.error(f'Error de BD: {error}')
        db.session.rollback()
        if 'database is locked' in str(error).lower():
            return "La base de datos está ocupada, intenta de nuevo", 503
        return "Error de base de datos", 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return "Archivo demasiado grande", 413
    
    db.init_app(app)
    
    # Validar timeout de sesión
    @app.before_request
    def check_session_timeout():
        from datetime import datetime, timedelta
        from flask import session, redirect, url_for, flash, request
        
        # Excluir rutas públicas
        if request.endpoint in ['auth.login', 'auth.login_get', 'static']:
            return
        
        if 'user_id' in session:
            last_activity = session.get('last_activity')
            if last_activity:
                if isinstance(last_activity, str):
                    last_activity = datetime.fromisoformat(last_activity)
                if datetime.now() - last_activity > timedelta(hours=2):
                    session.clear()
                    flash('Sesión expirada por inactividad', 'warning')
                    return redirect(url_for('auth.login'))
            session['last_activity'] = datetime.now().isoformat()
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(solicitudes_bp, url_prefix='/solicitudes')
    app.register_blueprint(solicitudes_dt_bp)  # API para DataTables
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(turnos_bp, url_prefix='/turnos')
    app.register_blueprint(sla_bp)
    app.register_blueprint(escalamiento_bp)
    app.register_blueprint(kb_bp)
    app.register_blueprint(flujo_bp)
    app.register_blueprint(cambios_ia_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(workflow_bp)
    app.register_blueprint(secciones_bp, url_prefix='/secciones')
    app.register_blueprint(departamentos_bp, url_prefix='/departamentos')
    app.register_blueprint(servicios_bp, url_prefix='/servicios')
    app.register_blueprint(subcategorias_bp, url_prefix='/subcategorias')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    @app.context_processor
    def inject_cambios_activos():
        from models import Usuario
        from services.notification_service import NotificationService
        from flask import session
        
        if session.get('user_id'):
            user = Usuario.query.get(session['user_id'])
            cambios_no_validados = NotificationService.obtener_cambios_no_validados()
            notificaciones = NotificationService.generar_notificaciones(user)
            
            return {
                'cambios_no_validados': cambios_no_validados,
                'notificaciones': notificaciones,
                'notificaciones_count': len(notificaciones)
            }
        
        return {
            'cambios_no_validados': 0,
            'notificaciones': [],
            'notificaciones_count': 0
        }
    
    @app.route('/')
    def index():
        return redirect(url_for('solicitudes.index'))
    
    @app.route('/health')
    def health_check():
        """Endpoint de health check para monitoreo"""
        try:
            # Verificar conexión a base de datos
            db.session.execute(db.text('SELECT 1'))
            return {
                'status': 'healthy',
                'database': 'ok',
                'timestamp': datetime.now().isoformat()
            }, 200
        except Exception as e:
            app.logger.error(f'Health check failed: {e}')
            return {
                'status': 'unhealthy',
                'database': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, 503
    
    @app.route('/guardar-tema', methods=['POST'])
    def guardar_tema():
        """Guardar preferencia de tema del usuario"""
        from flask import session, request, jsonify
        if 'user_id' in session:
            dark_mode = request.form.get('darkMode') == 'true'
            session['dark_mode'] = dark_mode
            return jsonify({'success': True})
        return jsonify({'success': False}), 401
    
    with app.app_context():
        max_retries = 3
        for attempt in range(max_retries):
            try:
                db.create_all()
                from services.init_data_service import InitDataService
                InitDataService.inicializar()
                break
            except OperationalError as e:
                if attempt < max_retries - 1 and 'database is locked' in str(e).lower():
                    import time
                    time.sleep(1)
                    continue
                raise
    
    return app

if __name__ == '__main__':
    env = os.environ.get('FLASK_ENV', 'development')
    app = create_app(env)
    
    # NUNCA usar debug=True en producción
    app.run(debug=False, host='127.0.0.1', port=5005)
