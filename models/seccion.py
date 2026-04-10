from models.base import BaseModel, db

class Seccion(BaseModel):
    __tablename__ = 'secciones'
    
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    medio = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200))
    email_notificacion = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Seccion {self.nombre}>'
    
    @classmethod
    def get_resolutores(cls, seccion_id):
        from models import Usuario
        return Usuario.query.filter_by(seccion_id=seccion_id, deleted_at=None).all()
    
    @classmethod
    def get_activas(cls):
        """Obtiene solo secciones activas y no eliminadas"""
        return cls.query.filter_by(deleted_at=None, activo=True).all()

class SeccionResolutor(BaseModel):
    __tablename__ = 'seccion_resolutores'
    
    seccion_id = db.Column(db.Integer, db.ForeignKey('secciones.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    def __repr__(self):
        return f'<SeccionResolutor {self.seccion_id}-{self.usuario_id}>'
