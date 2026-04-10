from datetime import datetime, timedelta
from models.base import BaseModel, db

class SLAConfig(BaseModel):
    __tablename__ = 'sla_config'
    
    nombre = db.Column(db.String(100), nullable=False)
    tipo_ticket = db.Column(db.String(50), nullable=False)  # Incidente, Requerimiento, Cambio, Problema
    prioridad = db.Column(db.String(20), nullable=False)
    seccion = db.Column(db.String(100))
    
    # Tiempos en minutos
    tiempo_primera_respuesta = db.Column(db.Integer, nullable=False)
    tiempo_resolucion = db.Column(db.Integer, nullable=False)
    
    activo = db.Column(db.Boolean, default=True)
    
    @classmethod
    def get_sla(cls, tipo_ticket, prioridad, seccion=None):
        query = cls.query.filter_by(
            tipo_ticket=tipo_ticket,
            prioridad=prioridad,
            activo=True
        )
        if seccion:
            sla = query.filter_by(seccion=seccion).first()
            if sla:
                return sla
        return query.filter_by(seccion=None).first()


class SLATracking(BaseModel):
    __tablename__ = 'sla_tracking'
    
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitudes.id'), nullable=False, unique=True)
    sla_config_id = db.Column(db.Integer, db.ForeignKey('sla_config.id'))
    
    # Primera respuesta
    fecha_primera_respuesta_objetivo = db.Column(db.DateTime, nullable=False)
    fecha_primera_respuesta_real = db.Column(db.DateTime)
    primera_respuesta_cumplida = db.Column(db.Boolean)
    
    # Resolución
    fecha_resolucion_objetivo = db.Column(db.DateTime, nullable=False)
    fecha_resolucion_real = db.Column(db.DateTime)
    resolucion_cumplida = db.Column(db.Boolean)
    
    # Pausas
    tiempo_pausado = db.Column(db.Integer, default=0)  # minutos
    esta_pausado = db.Column(db.Boolean, default=False)
    razon_pausa = db.Column(db.String(200))
    
    solicitud = db.relationship('Solicitud', backref='sla_tracking')
    sla_config = db.relationship('SLAConfig')
    
    @property
    def estado_primera_respuesta(self):
        if self.primera_respuesta_cumplida is not None:
            return 'cumplido' if self.primera_respuesta_cumplida else 'incumplido'
        
        if self.esta_pausado:
            return 'pausado'
        
        ahora = datetime.now()
        tiempo_restante = (self.fecha_primera_respuesta_objetivo - ahora).total_seconds() / 60
        
        if tiempo_restante < 0:
            return 'vencido'
        elif tiempo_restante < 60:
            return 'critico'
        elif tiempo_restante < 240:
            return 'advertencia'
        return 'normal'
    
    @property
    def estado_resolucion(self):
        if self.resolucion_cumplida is not None:
            return 'cumplido' if self.resolucion_cumplida else 'incumplido'
        
        if self.esta_pausado:
            return 'pausado'
        
        ahora = datetime.now()
        tiempo_restante = (self.fecha_resolucion_objetivo - ahora).total_seconds() / 60
        
        if tiempo_restante < 0:
            return 'vencido'
        elif tiempo_restante < 240:
            return 'critico'
        elif tiempo_restante < 1440:
            return 'advertencia'
        return 'normal'


class SLAPausa(BaseModel):
    __tablename__ = 'sla_pausas'
    
    sla_tracking_id = db.Column(db.Integer, db.ForeignKey('sla_tracking.id'), nullable=False)
    razon = db.Column(db.String(200), nullable=False)
    fecha_inicio = db.Column(db.DateTime, nullable=False, default=datetime.now)
    fecha_fin = db.Column(db.DateTime)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    sla_tracking = db.relationship('SLATracking', backref='pausas')
    usuario = db.relationship('Usuario')
    
    @property
    def duracion_minutos(self):
        fin = self.fecha_fin or datetime.now()
        return int((fin - self.fecha_inicio).total_seconds() / 60)
