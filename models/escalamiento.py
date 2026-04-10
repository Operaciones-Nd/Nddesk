from datetime import datetime
from models.base import BaseModel, db

class EscalamientoConfig(BaseModel):
    __tablename__ = 'escalamiento_config'
    
    nombre = db.Column(db.String(100), nullable=False)
    tipo_ticket = db.Column(db.String(50))
    prioridad = db.Column(db.String(20))
    seccion = db.Column(db.String(100))
    
    # Niveles de escalamiento
    nivel_1_grupo = db.Column(db.String(100), nullable=False)
    nivel_1_tiempo = db.Column(db.Integer, nullable=False)  # minutos
    
    nivel_2_grupo = db.Column(db.String(100))
    nivel_2_tiempo = db.Column(db.Integer)
    
    nivel_3_grupo = db.Column(db.String(100))
    nivel_3_tiempo = db.Column(db.Integer)
    
    activo = db.Column(db.Boolean, default=True)
    
    @classmethod
    def get_config(cls, tipo_ticket, prioridad, seccion):
        return cls.query.filter_by(
            tipo_ticket=tipo_ticket,
            prioridad=prioridad,
            seccion=seccion,
            activo=True
        ).first()


class Escalamiento(BaseModel):
    __tablename__ = 'escalamientos'
    
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitudes.id'), nullable=False)
    nivel_anterior = db.Column(db.Integer, nullable=False)
    nivel_actual = db.Column(db.Integer, nullable=False)
    
    grupo_anterior = db.Column(db.String(100))
    grupo_actual = db.Column(db.String(100), nullable=False)
    
    tipo = db.Column(db.String(20), nullable=False)  # automatico, manual
    razon = db.Column(db.Text, nullable=False)
    
    escalado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha_escalamiento = db.Column(db.DateTime, nullable=False, default=datetime.now)
    
    notificado = db.Column(db.Boolean, default=False)
    
    solicitud = db.relationship('Solicitud', backref='escalamientos')
    usuario = db.relationship('Usuario')
    
    @classmethod
    def get_by_ticket(cls, solicitud_id):
        return cls.query.filter_by(solicitud_id=solicitud_id).order_by(cls.fecha_escalamiento.desc()).all()
    
    @classmethod
    def get_nivel_actual(cls, solicitud_id):
        ultimo = cls.query.filter_by(solicitud_id=solicitud_id).order_by(cls.fecha_escalamiento.desc()).first()
        return ultimo.nivel_actual if ultimo else 1
