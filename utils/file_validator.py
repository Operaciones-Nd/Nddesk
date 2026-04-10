"""
Validación segura de archivos subidos
"""
import os
from PIL import Image
from werkzeug.utils import secure_filename
from utils.validators import ValidationError

# Intentar importar magic, si falla usar validación básica
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

class FileValidator:
    """Validador de archivos con verificación de contenido real"""
    
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx', 'txt'}
    
    ALLOWED_MIMETYPES = {
        'application/pdf',
        'image/jpeg',
        'image/png',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/plain'
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def validate_file(file, max_size=None):
        """
        Valida un archivo de forma exhaustiva
        
        Args:
            file: FileStorage object de Flask
            max_size: Tamaño máximo en bytes (opcional)
            
        Returns:
            tuple: (filename_seguro, mime_type)
            
        Raises:
            ValidationError: Si el archivo no es válido
        """
        if not file or not file.filename:
            raise ValidationError('No se seleccionó ningún archivo')
        
        # 1. Validar nombre de archivo
        filename = secure_filename(file.filename)
        if not filename:
            raise ValidationError('Nombre de archivo inválido')
        
        # 2. Validar extensión
        if '.' not in filename:
            raise ValidationError('Archivo sin extensión')
        
        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in FileValidator.ALLOWED_EXTENSIONS:
            raise ValidationError(f'Extensión no permitida: .{ext}')
        
        # 3. Validar tamaño
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        max_allowed = max_size or FileValidator.MAX_FILE_SIZE
        if size > max_allowed:
            size_mb = size / (1024 * 1024)
            max_mb = max_allowed / (1024 * 1024)
            raise ValidationError(f'Archivo demasiado grande: {size_mb:.1f}MB (máximo {max_mb:.1f}MB)')
        
        if size == 0:
            raise ValidationError('El archivo está vacío')
        
        # 4. Validar tipo MIME real del contenido (si magic está disponible)
        if MAGIC_AVAILABLE:
            try:
                mime = magic.from_buffer(file.read(2048), mime=True)
                file.seek(0)
            except Exception as e:
                raise ValidationError(f'Error al detectar tipo de archivo: {str(e)}')
            
            if mime not in FileValidator.ALLOWED_MIMETYPES:
                raise ValidationError(f'Tipo de archivo no permitido: {mime}')
        else:
            # Validación básica por extensión si magic no está disponible
            mime = FileValidator._guess_mime_from_extension(ext)
        
        # 5. Validaciones específicas por tipo
        if mime.startswith('image/'):
            FileValidator._validate_image(file)
        
        return filename, mime
    
    @staticmethod
    def _guess_mime_from_extension(ext):
        """Adivina MIME type desde extensión (fallback)"""
        mime_map = {
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'txt': 'text/plain'
        }
        return mime_map.get(ext, 'application/octet-stream')
    
    @staticmethod
    def _validate_image(file):
        """Valida que una imagen sea realmente una imagen válida"""
        try:
            img = Image.open(file)
            img.verify()
            file.seek(0)
            
            # Validar dimensiones razonables
            if img.size[0] > 10000 or img.size[1] > 10000:
                raise ValidationError('Imagen demasiado grande (dimensiones)')
            
        except Exception as e:
            raise ValidationError(f'Archivo de imagen corrupto o inválido: {str(e)}')
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitiza un nombre de archivo de forma segura"""
        # Remover caracteres peligrosos
        filename = secure_filename(filename)
        
        # Limitar longitud
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext
        
        return filename
