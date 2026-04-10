from models.base import BaseModel, db

class CalificacionTicket(BaseModel):
    __tablename__ = 'calificaciones_ticket'
    
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitudes.id'), nullable=False, unique=True, index=True)
    calificacion = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text)
    
    solicitud = db.relationship('Solicitud', backref='calificacion')
    
    @classmethod
    def get_by_ticket(cls, solicitud_id):
        return cls.query.filter_by(solicitud_id=solicitud_id).first()
