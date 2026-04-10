from models.base import BaseModel, db

class Servicio(BaseModel):
    __tablename__ = 'servicios'
    
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)
    
    subcategorias = db.relationship('Subcategoria', backref='servicio', lazy=True)
