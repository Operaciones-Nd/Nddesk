from models.base import BaseModel, db

class Comentario(BaseModel):
    __tablename__ = 'comentarios'
    
    ticket_id = db.Column(db.Integer, db.ForeignKey('solicitudes.id'), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    es_publico = db.Column(db.Boolean, default=True)
    
    ticket = db.relationship('Solicitud', backref='comentarios_legacy')
    usuario = db.relationship('Usuario', backref='comentarios_realizados')
