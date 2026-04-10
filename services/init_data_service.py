"""
Servicio de Inicialización de Datos
Carga datos iniciales del sistema
"""
from models import Usuario, TipoTicket, SLAConfig, db
from models.seccion import Seccion
from models.departamento import Departamento
from models.servicio import Servicio
from models.tipo_ticket import TIPOS_TICKET_ITIL
import os

class InitDataService:
    
    @staticmethod
    def inicializar():
        """Inicializa todos los datos del sistema"""
        InitDataService._crear_usuarios()
        InitDataService._crear_tipos_ticket()
        InitDataService._crear_slas()
        InitDataService._crear_secciones()
        InitDataService._crear_departamentos()
        InitDataService._crear_servicios()
        InitDataService._crear_subcategorias()
    
    @staticmethod
    def _crear_usuarios():
        """Crea usuarios iniciales si no existen"""
        if Usuario.query.count() > 0:
            return
        
        usuarios_data = [
            {'username': 'admin', 'nombre': 'Administrador', 'rol': 'admin'},
            {'username': 'leo.morales', 'nombre': 'Leo Morales', 'rol': 'coordinador'},
            {'username': 'mercadeo', 'nombre': 'Mercadeo ND', 'rol': 'solicitante'},
            {'username': 'ventas', 'nombre': 'Ventas ND', 'rol': 'solicitante'},
            {'username': 'jennyfer.hernandez', 'nombre': 'Jennyfer Hernández', 'rol': 'resolutor'},
            {'username': 'beverly.morales', 'nombre': 'Beverly Morales', 'rol': 'resolutor'},
            {'username': 'edwin.pineda', 'nombre': 'Edwin Pineda', 'rol': 'resolutor'},
            {'username': 'pedro.mijangos', 'nombre': 'Pedro Pablo Mijangos', 'rol': 'resolutor'},
            {'username': 'melvin.pineda', 'nombre': 'Melvin Pineda', 'rol': 'resolutor'},
            {'username': 'claudia.argueta', 'nombre': 'Claudia Argueta', 'rol': 'resolutor'},
            {'username': 'priscila.leon', 'nombre': 'Priscila León', 'rol': 'resolutor'},
            {'username': 'yadira.montes', 'nombre': 'Yadira Montes', 'rol': 'resolutor'},
            {'username': 'jose.davila', 'nombre': 'Jose Dávila', 'rol': 'resolutor'},
            {'username': 'eugenia.hernandez', 'nombre': 'Eugenia Hernández', 'rol': 'resolutor'},
            {'username': 'byron.garcia', 'nombre': 'Byron García', 'rol': 'resolutor'},
            {'username': 'karen.meza', 'nombre': 'Karen Meza', 'rol': 'resolutor'},
            {'username': 'orlenda.garrido', 'nombre': 'Orlenda Garrido', 'rol': 'resolutor'},
            {'username': 'jorge.garcia', 'nombre': 'Jorge Mario García', 'rol': 'resolutor'},
            {'username': 'mayra.rosal', 'nombre': 'Mayra Rosal', 'rol': 'resolutor'},
            {'username': 'alexis.batres', 'nombre': 'Alexis Batres', 'rol': 'resolutor'},
            {'username': 'jessica.osorio', 'nombre': 'Jessica Osorio', 'rol': 'resolutor'},
            {'username': 'sara.bran', 'nombre': 'Sara Bran', 'rol': 'resolutor'},
            {'username': 'fredy.hernandez', 'nombre': 'Fredy Hernández', 'rol': 'resolutor'},
            {'username': 'jessica.gonzalez', 'nombre': 'Jessica González', 'rol': 'resolutor'},
            {'username': 'veronica.gamboa', 'nombre': 'Verónica Gamboa', 'rol': 'resolutor'}
        ]
        
        default_password = os.environ.get('DEFAULT_USER_PASSWORD')
        if not default_password:
            raise ValueError('DEFAULT_USER_PASSWORD debe estar definida en variables de entorno')
        
        usuarios = []
        for data in usuarios_data:
            usuario = Usuario(
                username=data['username'],
                nombre=data['nombre'],
                rol=data['rol'],
                requiere_cambio_password=True
            )
            usuario.set_password(default_password)
            usuarios.append(usuario)
        
        db.session.add_all(usuarios)
        db.session.commit()
    
    @staticmethod
    def _crear_tipos_ticket():
        """Crea tipos de ticket ITIL si no existen"""
        if TipoTicket.query.count() > 0:
            return
        
        for tipo_data in TIPOS_TICKET_ITIL:
            tipo = TipoTicket(**tipo_data)
            db.session.add(tipo)
        
        db.session.commit()
    
    @staticmethod
    def _crear_slas():
        """Crea configuraciones SLA si no existen"""
        if SLAConfig.query.count() > 0:
            return
        
        slas = [
            SLAConfig(nombre='Incidente Alta', tipo_ticket='INCIDENTE', prioridad='Alta', tiempo_primera_respuesta=30, tiempo_resolucion=240),
            SLAConfig(nombre='Incidente Media', tipo_ticket='INCIDENTE', prioridad='Media', tiempo_primera_respuesta=120, tiempo_resolucion=1440),
            SLAConfig(nombre='Incidente Baja', tipo_ticket='INCIDENTE', prioridad='Baja', tiempo_primera_respuesta=480, tiempo_resolucion=4320),
            SLAConfig(nombre='Requerimiento Alta', tipo_ticket='REQUERIMIENTO', prioridad='Alta', tiempo_primera_respuesta=60, tiempo_resolucion=480),
            SLAConfig(nombre='Requerimiento Media', tipo_ticket='REQUERIMIENTO', prioridad='Media', tiempo_primera_respuesta=240, tiempo_resolucion=2880),
            SLAConfig(nombre='Requerimiento Baja', tipo_ticket='REQUERIMIENTO', prioridad='Baja', tiempo_primera_respuesta=720, tiempo_resolucion=7200),
        ]
        
        db.session.add_all(slas)
        db.session.commit()
    
    @staticmethod
    def _crear_secciones():
        """Crea secciones con emails de notificación"""
        if Seccion.query.count() > 0:
            return
        
        secciones = [
            Seccion(nombre='Digital', medio='Nuestro Diario', email_notificacion='digital.tickets@nuestrodiario.com.gt', activo=True),
            Seccion(nombre='Deportes', medio='Nuestro Diario', email_notificacion='deportes.tickets@nuestrodiario.com.gt', activo=True),
            Seccion(nombre='Soft News', medio='Nuestro Diario', email_notificacion='softnews.tickets@nuestrodiario.com.gt', activo=True),
            Seccion(nombre='Content Marketing', medio='Nuestro Diario', email_notificacion='marketing.tickets@nuestrodiario.com.gt', activo=True),
            Seccion(nombre='Regionales', medio='Nuestro Diario', email_notificacion='regionales.tickets@nuestrodiario.com.gt', activo=True),
            Seccion(nombre='Metro', medio='Nuestro Diario', email_notificacion='metro.tickets@nuestrodiario.com.gt', activo=True),
            Seccion(nombre='Soy502', medio='Nuestro Diario', email_notificacion='s502.tickets@soy502.com', activo=True)
        ]
        
        db.session.add_all(secciones)
        db.session.commit()
    
    @staticmethod
    def _crear_departamentos():
        """Crea departamentos solicitantes"""
        if Departamento.query.count() > 0:
            return
        
        departamentos = [
            Departamento(nombre='Mercadeo ND', descripcion='Departamento de Mercadeo Nuestro Diario', activo=True),
            Departamento(nombre='Ventas ND', descripcion='Departamento de Ventas Nuestro Diario', activo=True),
            Departamento(nombre='Mercadeo Soy502', descripcion='Departamento de Mercadeo Soy502', activo=True)
        ]
        
        db.session.add_all(departamentos)
        db.session.commit()
    
    @staticmethod
    def _crear_servicios():
        """Crea servicios"""
        if Servicio.query.count() > 0:
            return
        
        servicios = [
            Servicio(nombre='Digital', descripcion='Contenido digital y web', activo=True),
            Servicio(nombre='Impreso', descripcion='impreso', activo=True)
        ]
        
        db.session.add_all(servicios)
        db.session.commit()
    
    @staticmethod
    def _crear_subcategorias():
        """Crea subcategorías"""
        from models.subcategoria import Subcategoria
        
        if Subcategoria.query.count() > 0:
            return
        
        # Obtener servicios
        digital = Servicio.query.filter_by(nombre='Digital').first()
        impreso = Servicio.query.filter_by(nombre='Impreso').first()
        
        if not digital or not impreso:
            return
        
        subcategorias = [
            Subcategoria(nombre='Contenido Digital', servicio_id=digital.id, activo=True),
            Subcategoria(nombre='Doble página', servicio_id=impreso.id, activo=True),
            Subcategoria(nombre='Nota', servicio_id=impreso.id, activo=True),
            Subcategoria(nombre='Página', servicio_id=impreso.id, activo=True),
            Subcategoria(nombre='Suplemento', servicio_id=impreso.id, activo=True)
        ]
        
        db.session.add_all(subcategorias)
        db.session.commit()
