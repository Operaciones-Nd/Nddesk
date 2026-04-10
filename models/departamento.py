from models.base import BaseModel, db

class Departamento(BaseModel):
    __tablename__ = 'departamentos'
    
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(200))
    email_notificacion = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Departamento {self.nombre}>'
