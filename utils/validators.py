import re
import bleach
from markupsafe import escape

class ValidationError(Exception):
    pass

class InputSanitizer:
    """Sanitiza entradas para prevenir XSS e inyecciones"""
    
    ALLOWED_TAGS = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
    ALLOWED_ATTRIBUTES = {}
    MAX_TEXT_LENGTH = 5000
    VALID_PRIORITIES = ['Alta', 'Media', 'Baja', 'Urgente']
    VALID_ESTADOS = ['Pendiente', 'Planificado', 'Escalado', 'Solucionado', 'Cerrado']
    
    # Pre-compilar regex para mejor rendimiento
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    FILENAME_PATTERN = re.compile(r'[^a-zA-Z0-9._-]')
    
    @staticmethod
    def sanitize_html(text):
        """Limpia HTML peligroso"""
        if not text:
            return text
        return bleach.clean(text, tags=InputSanitizer.ALLOWED_TAGS, 
                          attributes=InputSanitizer.ALLOWED_ATTRIBUTES, strip=True)
    
    @staticmethod
    def sanitize_string(text, max_length=None):
        """Limpia string general"""
        if not text:
            return ""
        if max_length:
            text = text[:max_length]
        text = escape(text).strip()
        return text
    
    @staticmethod
    def sanitize_email(email):
        """Valida y limpia email"""
        if not email:
            return None
        email = email.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError('Email inválido')
        return email
    
    @staticmethod
    def sanitize_filename(filename):
        """Limpia nombre de archivo"""
        if not filename:
            return None
        # Remover caracteres peligrosos
        filename = InputSanitizer.FILENAME_PATTERN.sub('_', filename)
        # Prevenir path traversal - remover todos los ..
        while '..' in filename:
            filename = filename.replace('..', '')
        return filename[:255]

class TicketValidator:
    @staticmethod
    def validate_create(data):
        errors = []
        
        # Validar campos requeridos
        if not data.get('descripcion', '').strip():
            errors.append('La descripción es requerida')
        elif len(data['descripcion']) > 5000:
            errors.append('La descripción no puede exceder 5000 caracteres')
            
        if not data.get('fecha_publicacion'):
            errors.append('La fecha de publicación es requerida')
            
        if not data.get('grupo_resuelve'):
            errors.append('El grupo que resuelve es requerido')
        
        # Validar email si existe
        if data.get('email_notificacion'):
            try:
                InputSanitizer.sanitize_email(data['email_notificacion'])
            except ValidationError as e:
                errors.append(str(e))
        
        # Validar prioridad
        if data.get('prioridad') and data['prioridad'] not in InputSanitizer.VALID_PRIORITIES:
            errors.append('Prioridad inválida')
        
        if errors:
            raise ValidationError('; '.join(errors))
        return True
    
    @staticmethod
    def validate_update(data):
        errors = []
        
        # Validar estado
        if data.get('estado') and data['estado'] not in ['Pendiente', 'Planificado', 'Escalado', 'Solucionado', 'Cerrado']:
            errors.append('Estado inválido')
        
        # Validar prioridad
        if data.get('prioridad') and data['prioridad'] not in InputSanitizer.VALID_PRIORITIES:
            errors.append('Prioridad inválida')
        
        # Validar longitud de campos
        if data.get('solucion') and len(data['solucion']) > 5000:
            errors.append('La solución no puede exceder 5000 caracteres')
        
        if data.get('bitacora_publica') and len(data['bitacora_publica']) > 5000:
            errors.append('La bitácora pública no puede exceder 5000 caracteres')
        
        if data.get('bitacora_oculta') and len(data['bitacora_oculta']) > 5000:
            errors.append('La bitácora interna no puede exceder 5000 caracteres')
        
        if errors:
            raise ValidationError('; '.join(errors))
        return True

class PasswordValidator:
    # Pre-compilar regex
    UPPER_PATTERN = re.compile(r'[A-Z]')
    LOWER_PATTERN = re.compile(r'[a-z]')
    DIGIT_PATTERN = re.compile(r'\d')
    SPECIAL_PATTERN = re.compile(r'[!@#$%^&*(),.?":{}|<>]')
    
    @staticmethod
    def validate(password, config):
        if not password:
            raise ValidationError('La contraseña es requerida')
        
        errors = []
        min_length = getattr(config, 'PASSWORD_MIN_LENGTH', 8)
        require_upper = getattr(config, 'PASSWORD_REQUIRE_UPPERCASE', True)
        require_lower = getattr(config, 'PASSWORD_REQUIRE_LOWERCASE', True)
        require_digit = getattr(config, 'PASSWORD_REQUIRE_DIGIT', True)
        require_special = getattr(config, 'PASSWORD_REQUIRE_SPECIAL', True)
        
        if len(password) < min_length:
            errors.append(f'Mínimo {min_length} caracteres')
        if require_upper and not PasswordValidator.UPPER_PATTERN.search(password):
            errors.append('Debe contener mayúsculas')
        if require_lower and not PasswordValidator.LOWER_PATTERN.search(password):
            errors.append('Debe contener minúsculas')
        if require_digit and not PasswordValidator.DIGIT_PATTERN.search(password):
            errors.append('Debe contener números')
        if require_special and not PasswordValidator.SPECIAL_PATTERN.search(password):
            errors.append('Debe contener caracteres especiales')
        if errors:
            raise ValidationError('; '.join(errors))
        return True
