from models import Usuario, Solicitud, Flujo, ReglaAutomatizacion, SLAConfig, db
from services.flujo_generator_service import FlujoGeneratorService
import re
import os

class ComandoIAService:
    
    @staticmethod
    def ejecutar_comando(prompt, usuario_admin):
        """Ejecuta comandos desde lenguaje natural"""
        prompt_lower = prompt.lower()
        
        # Detectar tipo de comando - MAS FLEXIBLE
        if 'usuario' in prompt_lower and ('crear' in prompt_lower or 'nuevo' in prompt_lower or 'crea' in prompt_lower):
            return ComandoIAService._crear_usuario(prompt, usuario_admin)
        
        elif 'flujo' in prompt_lower and ('crear' in prompt_lower or 'nuevo' in prompt_lower or 'crea' in prompt_lower):
            return ComandoIAService._crear_flujo(prompt, usuario_admin)
        
        elif 'regla' in prompt_lower and ('crear' in prompt_lower or 'nuevo' in prompt_lower or 'crea' in prompt_lower):
            return ComandoIAService._crear_regla(prompt, usuario_admin)
        
        elif 'ticket' in prompt_lower and ('crear' in prompt_lower or 'nuevo' in prompt_lower or 'crea' in prompt_lower):
            return ComandoIAService._crear_ticket(prompt, usuario_admin)
        
        elif 'listar' in prompt_lower or 'mostrar' in prompt_lower or 'lista' in prompt_lower:
            return ComandoIAService._listar(prompt)
        
        elif 'cambiar' in prompt_lower or 'modificar' in prompt_lower or 'actualizar' in prompt_lower:
            return ComandoIAService._modificar(prompt)
        
        else:
            return {'error': f'No entiendo "{prompt}". Intenta: "crea un usuario llamado Juan", "listar usuarios", etc.'}
    
    @staticmethod
    def _crear_usuario(prompt, admin):
        """Crea usuario desde prompt"""
        # Extraer datos del prompt
        nombre = ComandoIAService._extraer_valor(prompt, ['llamado', 'nombre'])
        username = ComandoIAService._extraer_valor(prompt, ['username', 'user'])
        rol = ComandoIAService._extraer_rol(prompt)
        departamento = ComandoIAService._extraer_valor(prompt, ['de', 'departamento', 'area'])
        password = ComandoIAService._extraer_password(prompt)
        
        # Valores por defecto
        if not username:
            username = nombre.lower() if nombre else None
        
        if not nombre or not username:
            return {'error': 'No pude detectar el nombre. Usa: "crea un usuario llamado [nombre]"'}
        
        if not departamento:
            departamento = 'General'
        
        if not password:
            password = os.environ.get('DEFAULT_USER_PASSWORD')
            if not password:
                raise ValueError('DEFAULT_USER_PASSWORD debe estar definida en variables de entorno')
        
        # Verificar si existe
        existe = Usuario.query.filter_by(username=username).first()
        if existe:
            return {'error': f'El usuario {username} ya existe'}
        
        # Crear usuario
        usuario = Usuario(
            nombre=nombre,
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
            'mensaje': f'Usuario {username} creado exitosamente',
            'datos': {
                'nombre': nombre,
                'username': username,
                'rol': rol,
                'departamento': departamento,
                'password_temporal': password,
                'debe_cambiar_password': True
            }
        }
    
    @staticmethod
    def _crear_flujo(prompt, admin):
        """Crea flujo desde prompt"""
        tipo_ticket = ComandoIAService._extraer_tipo_ticket(prompt)
        flujo = FlujoGeneratorService.generar_desde_texto(prompt, tipo_ticket)
        
        return {
            'success': True,
            'mensaje': f'Flujo "{flujo.nombre}" creado',
            'datos': {
                'id': flujo.id,
                'nombre': flujo.nombre,
                'tipo': flujo.tipo_ticket,
                'transiciones': len(flujo.transiciones)
            }
        }
    
    @staticmethod
    def _crear_ticket(prompt, admin):
        """Crea ticket desde prompt"""
        from datetime import datetime, timedelta
        
        descripcion = ComandoIAService._extraer_valor(prompt, ['descripcion', 'sobre', 'para'])
        prioridad = ComandoIAService._extraer_prioridad(prompt)
        
        if not descripcion:
            descripcion = prompt
        
        ticket = Solicitud(
            usuario_id=admin.id,
            fecha_publicacion=(datetime.now() + timedelta(days=1)).date(),
            medio='Web',
            departamento=admin.departamento,
            seccion='General',
            familia_servicios='Soporte',
            servicio='General',
            grupo_resuelve='Soporte',
            email_notificacion=f'{admin.username}@nuestrodiario.com',
            tipo_contenido='Texto',
            descripcion=descripcion,
            prioridad=prioridad
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        return {
            'success': True,
            'mensaje': f'Ticket #{ticket.id} creado',
            'datos': {
                'id': ticket.id,
                'descripcion': descripcion,
                'prioridad': prioridad
            }
        }
    
    @staticmethod
    def _listar(prompt):
        """Lista elementos"""
        if 'usuario' in prompt.lower():
            usuarios = Usuario.query.filter_by(deleted_at=None).all()
            return {
                'success': True,
                'tipo': 'usuarios',
                'total': len(usuarios),
                'datos': [{'id': u.id, 'nombre': u.nombre, 'username': u.username, 'rol': u.rol} for u in usuarios[:10]]
            }
        
        elif 'ticket' in prompt.lower():
            tickets = Solicitud.query.filter_by(deleted_at=None).order_by(Solicitud.created_at.desc()).limit(10).all()
            return {
                'success': True,
                'tipo': 'tickets',
                'total': len(tickets),
                'datos': [{'id': t.id, 'descripcion': t.descripcion[:50], 'estado': t.estado} for t in tickets]
            }
        
        elif 'flujo' in prompt.lower():
            flujos = Flujo.query.all()
            return {
                'success': True,
                'tipo': 'flujos',
                'total': len(flujos),
                'datos': [{'id': f.id, 'nombre': f.nombre, 'tipo': f.tipo_ticket, 'activo': f.activo} for f in flujos]
            }
        
        return {'error': 'No sé qué listar. Intenta: listar usuarios, listar tickets, listar flujos'}
    
    @staticmethod
    def _modificar(prompt):
        """Modifica elementos"""
        # Extraer ID
        match = re.search(r'#?(\d+)', prompt)
        if not match:
            return {'error': 'Necesito un ID. Ejemplo: "cambiar estado del ticket #123"'}
        
        id_elemento = int(match.group(1))
        
        if 'ticket' in prompt.lower():
            ticket = Solicitud.query.get(id_elemento)
            if not ticket:
                return {'error': f'Ticket #{id_elemento} no encontrado'}
            
            if 'estado' in prompt.lower():
                nuevo_estado = ComandoIAService._extraer_estado(prompt)
                ticket.estado = nuevo_estado
                db.session.commit()
                return {'success': True, 'mensaje': f'Ticket #{id_elemento} cambiado a {nuevo_estado}'}
        
        return {'error': 'No pude modificar. Sé más específico'}
    
    # Funciones auxiliares
    @staticmethod
    def _extraer_valor(texto, palabras_clave):
        import re
        for palabra in palabras_clave:
            if palabra in texto.lower():
                # Buscar después de la palabra clave hasta la siguiente palabra clave común
                pattern = rf'{palabra}[:\s]+([w.]+)'
                match = re.search(pattern, texto, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        return None
    
    @staticmethod
    def _extraer_rol(texto):
        texto_lower = texto.lower()
        if 'admin' in texto_lower or 'administrador' in texto_lower:
            return 'admin'
        elif 'coordinador' in texto_lower:
            return 'coordinador'
        elif 'resolutor' in texto_lower or 'reclutador' in texto_lower:
            return 'resolutor'
        return 'solicitante'
    
    @staticmethod
    def _extraer_tipo_ticket(texto):
        if 'incidente' in texto.lower():
            return 'INCIDENTE'
        elif 'cambio' in texto.lower():
            return 'CAMBIO'
        elif 'problema' in texto.lower():
            return 'PROBLEMA'
        return 'REQUERIMIENTO'
    
    @staticmethod
    def _extraer_prioridad(texto):
        if 'alta' in texto.lower() or 'urgente' in texto.lower():
            return 'Alta'
        elif 'baja' in texto.lower():
            return 'Baja'
        return 'Media'
    
    @staticmethod
    def _extraer_estado(texto):
        if 'planificado' in texto.lower():
            return 'Planificado'
        elif 'solucionado' in texto.lower():
            return 'Solucionado'
        elif 'cerrado' in texto.lower():
            return 'Cerrado'
        return 'Pendiente'

    
    @staticmethod
    def _extraer_password(texto):
        """Extrae password del texto"""
        import re
        # Buscar password después de "contraseña", "password", "pass"
        match = re.search(r'(?:contraseña|password|pass)[:\s]+([^\s]+)', texto, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
