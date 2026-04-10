from models.base import BaseModel, db

class AuditoriaTicket(BaseModel):
    __tablename__ = 'auditoria_tickets'
    
    ticket_id = db.Column(db.Integer, db.ForeignKey('solicitudes.id'), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    accion = db.Column(db.String(50), nullable=False)
    campo_modificado = db.Column(db.String(100))
    valor_anterior = db.Column(db.Text)
    valor_nuevo = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    
    usuario = db.relationship('Usuario', backref='auditorias_realizadas')
    ticket = db.relationship('Solicitud', backref='historial_auditoria')

class AuditoriaUsuario(BaseModel):
    __tablename__ = 'auditoria_usuarios'
    
    admin_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    usuario_afectado_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    accion = db.Column(db.String(50), nullable=False)
    detalle = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    
    admin = db.relationship('Usuario', foreign_keys=[admin_id], backref='auditorias_admin')
    usuario_afectado = db.relationship('Usuario', foreign_keys=[usuario_afectado_id])

class IntentoLogin(BaseModel):
    __tablename__ = 'intentos_login'
    
    username = db.Column(db.String(50), nullable=False, index=True)
    exitoso = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(50))
    bloqueado_hasta = db.Column(db.DateTime)
