from models import Usuario, db
import re
import os

class ComandoIASimple:
    
    @staticmethod
    def crear_usuario(prompt, admin):
        # Extraer: "llamado NOMBRE como ROL"
        match = re.search(r'llamado\s+([\w.]+)\s+como\s+(\w+)', prompt, re.IGNORECASE)
        if not match:
            return {'error': 'Formato: crea un usuario llamado [nombre] como [rol]'}
        
        nombre = match.group(1)
        rol = match.group(2).lower()
        
        # Mapear roles
        if rol in ['admin', 'administrador']:
            rol = 'admin'
        elif rol in ['coordinador']:
            rol = 'coordinador'
        elif rol in ['resolutor', 'reclutador']:
            rol = 'resolutor'
        else:
            rol = 'solicitante'
        
        # Extraer departamento
        match_depto = re.search(r'departamento\s+(\w+)', prompt, re.IGNORECASE)
        departamento = match_depto.group(1) if match_depto else 'General'
        
        # Extraer password
        match_pass = re.search(r'contraseña\s+(\S+)', prompt, re.IGNORECASE)
        if match_pass:
            password = match_pass.group(1)
        else:
            password = os.environ.get('DEFAULT_USER_PASSWORD')
            if not password:
                raise ValueError('DEFAULT_USER_PASSWORD debe estar definida en variables de entorno')
        
        username = nombre.lower()
        
        # Verificar si existe
        if Usuario.query.filter_by(username=username).first():
            return {'error': f'Usuario {username} ya existe'}
        
        # Crear
        usuario = Usuario(
            nombre=nombre.replace('.', ' ').title(),
            username=username,
            rol=rol,
            departamento=departamento,
            requiere_cambio_password=True
        )
        usuario.set_password(password)
        
        db.session.add(usuario)
        db.session.commit()
        
        return {
            'success': True,
            'mensaje': f'Usuario {username} creado',
            'datos': {
                'username': username,
                'rol': rol,
                'departamento': departamento,
                'password': password
            }
        }
