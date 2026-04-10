from models.base import BaseModel, db

usuario_secciones = db.Table('usuario_secciones',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuarios.id'), nullable=False),
    db.Column('seccion_id', db.Integer, db.ForeignKey('secciones.id'), nullable=False),
    db.Column('created_at', db.DateTime, nullable=False, default=db.func.current_timestamp()),
    db.Column('updated_at', db.DateTime),
    db.Column('deleted_at', db.DateTime)
)
