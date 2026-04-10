import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    # Seguridad: SECRET_KEY obligatoria desde entorno
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError('SECRET_KEY debe estar definida en variables de entorno')
    
    # Cookies seguras
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_NAME = '__Host-session' if os.environ.get('FLASK_ENV') == 'production' else 'session'
    
    # Base de datos
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise ValueError('DATABASE_URL debe estar definida en variables de entorno')
    
    # Convertir ruta relativa a absoluta para SQLite
    if db_url.startswith('sqlite:///'):
        db_path = db_url.replace('sqlite:///', '')
        if not db_path.startswith('/'):
            import os as os_module
            base_dir = os_module.path.abspath(os_module.path.dirname(__file__))
            db_path = os_module.path.join(base_dir, db_path)
            db_url = f'sqlite:///{db_path}'
    
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'connect_args': {
            'check_same_thread': False,
            'timeout': 30
        } if db_url.startswith('sqlite') else {}
    }
    
    # Archivos
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')  # Fuera de static
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'docx', 'xlsx'}
    ALLOWED_MIMETYPES = {
        'image/jpeg', 'image/png', 'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
    
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    MAX_LOGIN_ATTEMPTS = 10
    LOGIN_BLOCK_TIME = timedelta(minutes=3)
    
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '465'))
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'True') == 'True'
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Seguridad avanzada
    REQUIRE_REQUEST_SIGNATURE = False  # Activar en producción si necesario
    
    # Content Security Policy
    CONTENT_SECURITY_POLICY = {
        'default-src': ["'self'"],
        'script-src': ["'self'", "'unsafe-inline'"],
        'style-src': ["'self'", "'unsafe-inline'", 'fonts.googleapis.com'],
        'font-src': ["'self'", 'fonts.gstatic.com'],
        'img-src': ["'self'", 'data:'],
    }

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    REQUIRE_REQUEST_SIGNATURE = True
    
    # Rate limiting con Redis
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'redis://localhost:6379/0'
    
    # Logging avanzado
    LOG_LEVEL = 'INFO'
    LOG_TO_STDOUT = False
    
class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
