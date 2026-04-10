from models.base import BaseModel, db

class TipoTicket(BaseModel):
    __tablename__ = 'tipos_ticket'
    
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    icono = db.Column(db.String(50))
    color = db.Column(db.String(20))
    
    # Configuración
    requiere_aprobacion = db.Column(db.Boolean, default=False)
    permite_reabrir = db.Column(db.Boolean, default=True)
    activo = db.Column(db.Boolean, default=True)
    
    # Campos requeridos específicos
    campos_requeridos = db.Column(db.Text)  # JSON con campos adicionales
    
    @classmethod
    def get_activos(cls):
        return cls.query.filter_by(activo=True).order_by(cls.nombre).all()
    
    @classmethod
    def get_by_codigo(cls, codigo):
        return cls.query.filter_by(codigo=codigo, activo=True).first()


# Datos iniciales ITIL
TIPOS_TICKET_ITIL = [
    {
        'codigo': 'INCIDENTE',
        'nombre': 'Incidente',
        'descripcion': 'Interrupción no planificada o reducción de calidad de un servicio',
        'icono': 'fa-exclamation-triangle',
        'color': '#ef4444',
        'requiere_aprobacion': False,
        'permite_reabrir': True
    },
    {
        'codigo': 'REQUERIMIENTO',
        'nombre': 'Requerimiento de Servicio',
        'descripcion': 'Solicitud de un usuario para información, asesoría o servicio estándar',
        'icono': 'fa-hand-paper',
        'color': '#3b82f6',
        'requiere_aprobacion': False,
        'permite_reabrir': True
    },
    {
        'codigo': 'CAMBIO',
        'nombre': 'Cambio',
        'descripcion': 'Adición, modificación o eliminación de algo que podría afectar servicios',
        'icono': 'fa-exchange-alt',
        'color': '#f59e0b',
        'requiere_aprobacion': True,
        'permite_reabrir': False
    },
    {
        'codigo': 'PROBLEMA',
        'nombre': 'Problema',
        'descripcion': 'Causa raíz de uno o más incidentes',
        'icono': 'fa-search',
        'color': '#8b5cf6',
        'requiere_aprobacion': False,
        'permite_reabrir': True
    },
    {
        'codigo': 'TAREA',
        'nombre': 'Tarea Interna',
        'descripcion': 'Actividad interna del equipo de soporte',
        'icono': 'fa-tasks',
        'color': '#10b981',
        'requiere_aprobacion': False,
        'permite_reabrir': True
    }
]
