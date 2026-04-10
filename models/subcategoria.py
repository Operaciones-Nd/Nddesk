from models.base import BaseModel, db

class Subcategoria(BaseModel):
    __tablename__ = 'subcategorias'
    
    nombre = db.Column(db.String(100), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
