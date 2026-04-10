from models.base import BaseModel, db

# Tabla de asociación para múltiples analistas por turno
turno_analistas = db.Table('turno_analistas',
    db.Column('turno_id', db.Integer, db.ForeignKey('turnos_semanales.id'), primary_key=True),
    db.Column('analista_id', db.Integer, db.ForeignKey('usuarios.id'), primary_key=True)
)

class TurnoSemanal(BaseModel):
    __tablename__ = 'turnos_semanales'
    
    seccion = db.Column(db.String(100), nullable=False, index=True)
    analista_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)  # Mantener por compatibilidad
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    creado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    # Relación many-to-many para múltiples analistas
    analistas = db.relationship('Usuario', secondary=turno_analistas, backref='turnos_multiples')
    analista = db.relationship('Usuario', foreign_keys=[analista_id], backref='turnos_asignados')  # Mantener por compatibilidad
    coordinador = db.relationship('Usuario', foreign_keys=[creado_por])
    
    @classmethod
    def get_turno_actual(cls, seccion):
        from datetime import date
        return cls.get_active().filter(
            cls.seccion == seccion,
            cls.fecha_inicio <= date.today(),
            cls.fecha_fin >= date.today(),
            cls.activo == True
        ).first()
    
    @classmethod
    def get_analistas_turno(cls, seccion):
        """Obtiene todos los analistas de turno para una sección"""
        turno = cls.get_turno_actual(seccion)
        if turno:
            return turno.analistas if turno.analistas else ([turno.analista] if turno.analista else [])
        return []
