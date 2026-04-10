from functools import wraps
from flask import session, redirect, url_for, flash, request, current_app, jsonify
import secrets
import os

# Importar magic de forma opcional
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Si es una petición AJAX/API, devolver JSON
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'No autenticado'}), 401
            # Guardar solo el path (sin dominio) para redirigir después del login
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debes iniciar sesión', 'warning')
                return redirect(url_for('auth.login'))
            if session.get('rol') not in roles:
                current_app.logger.warning(f"Acceso denegado: {session.get('username')} intentó acceder a {request.path}")
                flash('No tienes permisos para acceder', 'danger')
                return redirect(url_for('solicitudes.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_file_upload(file, allowed_extensions=None, max_size=None):
    """Valida archivos subidos de forma segura"""
    if not file or file.filename == '':
        raise ValueError('No se seleccionó archivo')
    
    # Validar extensión
    if allowed_extensions is None:
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        raise ValueError(f'Extensión no permitida. Permitidas: {", ".join(allowed_extensions)}')
    
    # Validar tamaño
    if max_size is None:
        max_size = current_app.config['MAX_CONTENT_LENGTH']
    
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > max_size:
        raise ValueError(f'Archivo demasiado grande. Máximo: {max_size // (1024*1024)}MB')
    
    # Validar MIME type con python-magic (si está disponible)
    if MAGIC_AVAILABLE:
        try:
            mime = magic.from_buffer(file.read(2048), mime=True)
            file.seek(0)
            
            if mime not in current_app.config['ALLOWED_MIMETYPES']:
                raise ValueError(f'Tipo de archivo no permitido: {mime}')
        except Exception as e:
            current_app.logger.error(f'Error validando MIME type: {e}')
            raise ValueError('Error validando tipo de archivo')
    else:
        current_app.logger.warning('Validación MIME omitida - python-magic no disponible')
    
    # Generar nombre seguro
    secure_name = f"{secrets.token_hex(16)}.{ext}"
    mime = 'application/octet-stream'  # Default si magic no está disponible
    
    return secure_name, size, mime
