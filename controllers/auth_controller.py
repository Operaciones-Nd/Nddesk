from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from models import Usuario, db
from utils.validators import PasswordValidator, ValidationError, InputSanitizer
from utils.security import SecurityHelper
from utils.helpers import get_client_ip
from datetime import datetime
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login_get():
    return render_template('auth/login.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        # Sanitizar entradas
        username = InputSanitizer.sanitize_string(request.form.get('username', ''), max_length=100)
        password = request.form.get('password', '')
        ip = get_client_ip(request)
        
        # Validar campos no vacíos
        if not username or not password:
            flash('Usuario y contraseña son requeridos', 'danger')
            return render_template('auth/login.html')
        
        # Verificar intentos de login
        puede_intentar, bloqueado_hasta = SecurityHelper.check_login_attempts(
            username, 
            current_app.config['MAX_LOGIN_ATTEMPTS'],
            current_app.config['LOGIN_BLOCK_TIME']
        )
        
        if not puede_intentar:
            current_app.logger.warning(f'Intento de login bloqueado: {username} desde {ip}')
            flash(f'Usuario bloqueado hasta {bloqueado_hasta.strftime("%H:%M")}', 'danger')
            return render_template('auth/login.html')
        
        user = Usuario.get_by_username(username)
        
        if not user:
            SecurityHelper.register_login_attempt(username, False, ip, current_app.config['LOGIN_BLOCK_TIME'])
            current_app.logger.warning(f'Login fallido - usuario no existe: {InputSanitizer.sanitize_string(username)} desde {ip}')
            flash('Credenciales inválidas', 'danger')
            return render_template('auth/login.html')
        
        if user and user.activo and user.check_password(password):
            try:
                SecurityHelper.register_login_attempt(username, True, ip)
                
                # Regenerar session ID para prevenir session fixation
                session.clear()
                session.permanent = True
                session['user_id'] = user.id
                session['username'] = user.username
                session['nombre'] = user.nombre
                session['rol'] = user.rol
                session['csrf_token'] = secrets.token_hex(32)
                session['fondo_preferido'] = user.fondo_preferido or 'waves'
                
                user.ultimo_acceso = datetime.now()
                db.session.commit()
                
                current_app.logger.info(f'Login exitoso: {username} desde {ip}')
                
                if user.requiere_cambio_password:
                    return redirect(url_for('auth.cambiar_password'))
                
                # Redirigir a la página solicitada o al index
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('solicitudes.index'))
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f'Error en login: {str(e)}')
                flash('Error al iniciar sesión, intenta de nuevo', 'danger')
                return render_template('auth/login.html')
        
        SecurityHelper.register_login_attempt(username, False, ip, current_app.config['LOGIN_BLOCK_TIME'])
        current_app.logger.warning(f'Login fallido desde {ip}')
        flash('Credenciales inválidas', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    username = session.get('username', 'unknown')
    session.clear()
    current_app.logger.info(f'Logout: {username}')
    flash('Sesión cerrada', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/cambiar-password', methods=['GET', 'POST'])
def cambiar_password():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password_actual = request.form.get('password_actual', '')
        password_nueva = request.form.get('password_nueva', '')
        password_confirmar = request.form.get('password_confirmar', '')
        
        # Validar campos no vacíos
        if not all([password_actual, password_nueva, password_confirmar]):
            flash('Todos los campos son requeridos', 'danger')
            return render_template('auth/cambiar_password.html')
        
        user = Usuario.query.get(session['user_id'])
        if not user:
            session.clear()
            return redirect(url_for('auth.login'))
        
        if not user.check_password(password_actual):
            current_app.logger.warning(f'Intento de cambio de contraseña fallido: {user.username}')
            flash('Contraseña actual incorrecta', 'danger')
            return render_template('auth/cambiar_password.html')
        
        if password_nueva != password_confirmar:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('auth/cambiar_password.html')
        
        try:
            PasswordValidator.validate(password_nueva, current_app.config)
            user.set_password(password_nueva)
            user.requiere_cambio_password = False
            db.session.commit()
            current_app.logger.info(f'Contraseña cambiada: {user.username}')
            flash('Contraseña actualizada', 'success')
            return redirect(url_for('solicitudes.index'))
        except ValidationError as e:
            flash(str(e), 'danger')
    
    return render_template('auth/cambiar_password.html')

@auth_bp.route('/cambiar-fondo', methods=['POST'])
def cambiar_fondo():
    if 'user_id' not in session:
        return {'error': 'No autorizado'}, 401
    
    fondo = InputSanitizer.sanitize_string(request.form.get('fondo', 'waves'), max_length=50)
    user = Usuario.query.get(session['user_id'])
    if not user:
        return {'error': 'Usuario no encontrado'}, 404
    
    user.fondo_preferido = fondo
    db.session.commit()
    session['fondo_preferido'] = fondo
    current_app.logger.info(f'Fondo cambiado por usuario ID: {user.id}')
    
    return {'success': True}, 200
