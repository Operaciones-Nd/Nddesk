from werkzeug.security import generate_password_hash, check_password_hash
from models.base import BaseModel, db

class Usuario(BaseModel):
    __tablename__ = 'usuarios'
    
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), nullable=False, index=True)
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamentos.id'))
    seccion_id = db.Column(db.Integer, db.ForeignKey('secciones.id'))
    activo = db.Column(db.Boolean, default=True, nullable=False)
    requiere_cambio_password = db.Column(db.Boolean, default=True, nullable=False)
    ultimo_acceso = db.Column(db.DateTime)
    fondo_preferido = db.Column(db.String(50), default='default')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def get_by_username(cls, username):
        return cls.get_active().filter_by(username=username).first()
    
    @classmethod
    def get_by_rol(cls, rol):
        return cls.get_active().filter_by(rol=rol, activo=True).all()
    
    @classmethod
    def get_resolutores_by_seccion(cls, seccion_id):
        return cls.get_active().filter_by(rol='resolutor', seccion_id=seccion_id, activo=True).all()
    
    @property
    def is_admin(self):
        return self.rol == 'admin'
    
    @property
    def is_coordinador(self):
        return self.rol == 'coordinador'
    
    @property
    def is_resolutor(self):
        return self.rol == 'resolutor'

# Definir relación después de la clase
from models.usuario_secciones import usuario_secciones
Usuario.secciones = db.relationship('Seccion', secondary=usuario_secciones, backref='usuarios')
Usuario.departamento_obj = db.relationship('Departamento', foreign_keys=[Usuario.departamento_id])
