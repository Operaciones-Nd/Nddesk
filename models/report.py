from models import db
from datetime import datetime

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)  # 'semanal', 'mensual'
    semana_inicio = db.Column(db.Date, nullable=False)
    semana_fin = db.Column(db.Date, nullable=False)
    archivo_pdf = db.Column(db.String(255))
    total_solicitudes = db.Column(db.Integer, default=0)
    cumplidas_tiempo = db.Column(db.Integer, default=0)
    fuera_fecha = db.Column(db.Integer, default=0)
    porcentaje_cumplimiento = db.Column(db.Float, default=0.0)
    generado_por = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Report {self.tipo} {self.semana_inicio} - {self.semana_fin}>'
