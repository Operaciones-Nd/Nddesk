from datetime import datetime, timedelta
from models.base import BaseModel, db

class Solicitud(BaseModel):
    __tablename__ = 'solicitudes'
    
    # Índices compuestos para optimizar queries frecuentes
    __table_args__ = (
        db.Index('idx_solicitud_estado_deleted', 'estado', 'deleted_at'),
        db.Index('idx_solicitud_resolutor_estado', 'resuelto_por', 'estado'),
        db.Index('idx_solicitud_created_estado', 'created_at', 'estado'),
        db.Index('idx_solicitud_fecha_pub', 'fecha_publicacion'),
    )
    
    fecha_solicitud = db.Column(db.DateTime, default=datetime.now, nullable=False)
    fecha_publicacion = db.Column(db.Date, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    medio = db.Column(db.String(100), nullable=False)
    departamento = db.Column(db.String(100), nullable=False)
    seccion = db.Column(db.String(100), nullable=False, index=True)
    familia_servicios = db.Column(db.String(100), nullable=False)
    servicio = db.Column(db.String(100), nullable=False)
    grupo_resuelve = db.Column(db.String(100), nullable=False)
    email_notificacion = db.Column(db.String(200), nullable=False)
    tipo_contenido = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    adjuntos = db.Column(db.Text)
    estado = db.Column(db.String(50), default='Pendiente', nullable=False, index=True)
    prioridad = db.Column(db.String(20), default='Media', nullable=False)
    solucion = db.Column(db.Text)
    bitacora_publica = db.Column(db.Text)
    bitacora_oculta = db.Column(db.Text)
    resuelto_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha_cierre = db.Column(db.DateTime)
    fecha_primera_respuesta = db.Column(db.DateTime)
    tiempo_resolucion = db.Column(db.Integer)
    tipo_ticket = db.Column(db.String(50), default='REQUERIMIENTO')
    
    # Campos para el flujo de cierre
    servicio_solucion = db.Column(db.String(100))
    subcategoria_solucion = db.Column(db.String(100))
    codigo_solucion = db.Column(db.String(100))
    estado_publicacion = db.Column(db.String(50))
    comentarios_usuario = db.Column(db.Text)
    motivo_pendiente = db.Column(db.Text)
    motivo_reapertura = db.Column(db.Text)
    fecha_reapertura = db.Column(db.DateTime)
    reabierto_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    veces_reabierto = db.Column(db.Integer, default=0)
    
    # Campos para informe de anuncios
    publicado = db.Column(db.Boolean, default=False)  # Si se publicó el anuncio
    vendido = db.Column(db.Boolean, default=False)  # Si se vendió
    motivo_no_publicado = db.Column(db.Text)  # Por qué no se publicó
    
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id], backref='solicitudes_creadas')
    resolutor = db.relationship('Usuario', foreign_keys=[resuelto_por])
    
    @classmethod
    def get_by_status(cls, estado):
        return cls.get_active().filter_by(estado=estado).all()
    
    @classmethod
    def get_by_user(cls, usuario_id):
        return cls.get_active().filter_by(usuario_id=usuario_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_resolutor(cls, resolutor_id):
        return cls.get_active().filter_by(resuelto_por=resolutor_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_pending(cls):
        return cls.get_active().filter_by(estado='Pendiente').order_by(cls.created_at.desc()).all()
    
    @property
    def is_overdue(self):
        if self.estado in ['Cerrado', 'Solucionado']:
            return False
        dias_limite = {'Alta': 1, 'Media': 3, 'Baja': 7}
        limite = self.fecha_solicitud + timedelta(days=dias_limite.get(self.prioridad, 3))
        return datetime.now() > limite
    
    @property
    def is_open(self):
        return self.estado in ['Pendiente', 'Planificado']
    
    @property
    def sla_status(self):
        if self.estado in ['Cerrado', 'Solucionado']:
            return 'completado'
        
        dias_limite = {'Alta': 1, 'Media': 3, 'Baja': 7}
        limite = self.fecha_solicitud + timedelta(days=dias_limite.get(self.prioridad, 3))
        tiempo_restante = limite - datetime.now()
        
        if tiempo_restante.total_seconds() < 0:
            return 'vencido'
        elif tiempo_restante.total_seconds() < 3600 * 4:
            return 'critico'
        elif tiempo_restante.total_seconds() < 86400:
            return 'advertencia'
        return 'normal'
    
    @property
    def tiempo_transcurrido(self):
        if self.fecha_cierre:
            return int((self.fecha_cierre - self.fecha_solicitud).total_seconds() / 3600)
        return int((datetime.now() - self.fecha_solicitud).total_seconds() / 3600)
