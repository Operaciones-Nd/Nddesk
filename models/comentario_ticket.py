from models.base import BaseModel, db
from datetime import datetime

class ComentarioTicket(BaseModel):
    __tablename__ = 'comentarios_ticket'
    
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitudes.id'), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    es_interno = db.Column(db.Boolean, default=False, nullable=False)
    
    solicitud = db.relationship('Solicitud', backref='comentarios')
    usuario = db.relationship('Usuario')
    
    @classmethod
    def get_by_ticket(cls, solicitud_id, solo_publicos=False):
        query = cls.query.filter_by(solicitud_id=solicitud_id)
        if solo_publicos:
            query = query.filter_by(es_interno=False)
        return query.order_by(cls.created_at.asc()).all()
