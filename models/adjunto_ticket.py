from models.base import BaseModel, db

class AdjuntoTicket(BaseModel):
    __tablename__ = 'adjuntos_ticket'
    
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitudes.id'), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.String(500), nullable=False)
    tamano = db.Column(db.Integer)
    tipo_mime = db.Column(db.String(100))
    
    solicitud = db.relationship('Solicitud', backref='adjuntos_files')
    usuario = db.relationship('Usuario')
    
    @classmethod
    def get_by_ticket(cls, solicitud_id):
        return cls.query.filter_by(solicitud_id=solicitud_id).order_by(cls.created_at.desc()).all()
