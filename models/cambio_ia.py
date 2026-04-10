from models.base import BaseModel, db
from datetime import datetime

class CambioIA(BaseModel):
    __tablename__ = 'cambios_ia'
    
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    prompt_usuario = db.Column(db.Text, nullable=False)
    tipo_cambio = db.Column(db.String(50), nullable=False)  # flujo, regla, sla, campo
    codigo_generado = db.Column(db.Text)
    configuracion_json = db.Column(db.Text)
    
    activo = db.Column(db.Boolean, default=False)
    validado = db.Column(db.Boolean, default=False)
    aprobado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha_activacion = db.Column(db.DateTime)
    fecha_desactivacion = db.Column(db.DateTime)
    fecha_validacion = db.Column(db.DateTime)
    
    creado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Relaciones
    flujo_id = db.Column(db.Integer, db.ForeignKey('flujos.id'))
    regla_id = db.Column(db.Integer, db.ForeignKey('reglas_automatizacion.id'))
    sla_id = db.Column(db.Integer, db.ForeignKey('sla_config.id'))
    
    creador = db.relationship('Usuario', foreign_keys=[creado_por])
    aprobador = db.relationship('Usuario', foreign_keys=[aprobado_por])
    flujo = db.relationship('Flujo', backref='cambios_ia')
    regla = db.relationship('ReglaAutomatizacion', backref='cambios_ia')
    sla = db.relationship('SLAConfig', backref='cambios_ia')
    
    @classmethod
    def get_pendientes(cls):
        return cls.query.filter_by(activo=False, deleted_at=None).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_activos(cls):
        return cls.query.filter_by(activo=True, deleted_at=None).order_by(cls.fecha_activacion.desc()).all()
    
    @classmethod
    def get_activos_no_validados(cls):
        return cls.query.filter_by(activo=True, validado=False, deleted_at=None).order_by(cls.fecha_activacion.desc()).all()
    
    def activar(self, usuario_id):
        self.activo = True
        self.aprobado_por = usuario_id
        self.fecha_activacion = datetime.now()
        
        # Activar el elemento relacionado
        if self.flujo_id:
            self.flujo.activo = True
        elif self.regla_id:
            self.regla.activo = True
        elif self.sla_id:
            self.sla.activo = True
        
        db.session.commit()
    
    def desactivar(self):
        self.activo = False
        self.fecha_desactivacion = datetime.now()
        
        # Desactivar el elemento relacionado
        if self.flujo_id:
            self.flujo.activo = False
        elif self.regla_id:
            self.regla.activo = False
        elif self.sla_id:
            self.sla.activo = False
        
        db.session.commit()
    
    def validar(self):
        self.validado = True
        self.fecha_validacion = datetime.now()
        db.session.commit()
