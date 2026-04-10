from datetime import datetime, timedelta
from models.sla import SLAConfig, SLATracking, SLAPausa
from models.base import db

class SLAService:
    
    @staticmethod
    def iniciar_tracking(solicitud):
        """Inicia el tracking de SLA para un ticket"""
        sla_config = SLAConfig.get_sla(
            tipo_ticket=solicitud.tipo_ticket or 'REQUERIMIENTO',
            prioridad=solicitud.prioridad,
            seccion=solicitud.seccion
        )
        
        if not sla_config:
            # SLA por defecto si no hay configuración
            sla_config = SLAService._get_sla_default(solicitud.prioridad)
        
        ahora = datetime.now()
        
        tracking = SLATracking(
            solicitud_id=solicitud.id,
            sla_config_id=sla_config.id if hasattr(sla_config, 'id') else None,
            fecha_primera_respuesta_objetivo=ahora + timedelta(minutes=sla_config.tiempo_primera_respuesta),
            fecha_resolucion_objetivo=ahora + timedelta(minutes=sla_config.tiempo_resolucion)
        )
        
        db.session.add(tracking)
        db.session.commit()
        
        return tracking
    
    @staticmethod
    def registrar_primera_respuesta(solicitud_id):
        """Registra cuando se da la primera respuesta"""
        tracking = SLATracking.query.filter_by(solicitud_id=solicitud_id).first()
        if not tracking or tracking.fecha_primera_respuesta_real:
            return
        
        ahora = datetime.now()
        tracking.fecha_primera_respuesta_real = ahora
        tracking.primera_respuesta_cumplida = ahora <= tracking.fecha_primera_respuesta_objetivo
        
        db.session.commit()
    
    @staticmethod
    def registrar_resolucion(solicitud_id):
        """Registra cuando se resuelve el ticket"""
        tracking = SLATracking.query.filter_by(solicitud_id=solicitud_id).first()
        if not tracking or tracking.fecha_resolucion_real:
            return
        
        ahora = datetime.now()
        # Ajustar por tiempo pausado
        objetivo_ajustado = tracking.fecha_resolucion_objetivo + timedelta(minutes=tracking.tiempo_pausado)
        
        tracking.fecha_resolucion_real = ahora
        tracking.resolucion_cumplida = ahora <= objetivo_ajustado
        
        db.session.commit()
    
    @staticmethod
    def pausar_sla(solicitud_id, razon, usuario_id):
        """Pausa el SLA de un ticket"""
        tracking = SLATracking.query.filter_by(solicitud_id=solicitud_id).first()
        if not tracking or tracking.esta_pausado:
            return False
        
        tracking.esta_pausado = True
        tracking.razon_pausa = razon
        
        pausa = SLAPausa(
            sla_tracking_id=tracking.id,
            razon=razon,
            usuario_id=usuario_id
        )
        
        db.session.add(pausa)
        db.session.commit()
        
        return True
    
    @staticmethod
    def reanudar_sla(solicitud_id):
        """Reanuda el SLA de un ticket"""
        tracking = SLATracking.query.filter_by(solicitud_id=solicitud_id).first()
        if not tracking or not tracking.esta_pausado:
            return False
        
        # Cerrar la pausa actual
        pausa_actual = SLAPausa.query.filter_by(
            sla_tracking_id=tracking.id,
            fecha_fin=None
        ).first()
        
        if pausa_actual:
            pausa_actual.fecha_fin = datetime.now()
            tracking.tiempo_pausado += pausa_actual.duracion_minutos
        
        tracking.esta_pausado = False
        tracking.razon_pausa = None
        
        db.session.commit()
        
        return True
    
    @staticmethod
    def _get_sla_default(prioridad):
        """Retorna SLA por defecto según prioridad"""
        slas_default = {
            'Alta': {'tiempo_primera_respuesta': 30, 'tiempo_resolucion': 240},
            'Media': {'tiempo_primera_respuesta': 120, 'tiempo_resolucion': 1440},
            'Baja': {'tiempo_primera_respuesta': 480, 'tiempo_resolucion': 4320}
        }
        
        config = slas_default.get(prioridad, slas_default['Media'])
        
        class SLADefault:
            def __init__(self, config):
                self.tiempo_primera_respuesta = config['tiempo_primera_respuesta']
                self.tiempo_resolucion = config['tiempo_resolucion']
        
        return SLADefault(config)
    
    @staticmethod
    def get_tickets_proximos_vencer(minutos=60):
        """Obtiene tickets próximos a vencer SLA"""
        limite = datetime.now() + timedelta(minutes=minutos)
        
        return SLATracking.query.filter(
            SLATracking.resolucion_cumplida.is_(None),
            SLATracking.fecha_resolucion_objetivo <= limite,
            SLATracking.esta_pausado == False
        ).all()
    
    @staticmethod
    def get_metricas_sla(fecha_inicio=None, fecha_fin=None):
        """Calcula métricas de cumplimiento de SLA"""
        query = SLATracking.query.filter(SLATracking.resolucion_cumplida.isnot(None))
        
        if fecha_inicio:
            query = query.filter(SLATracking.fecha_resolucion_real >= fecha_inicio)
        if fecha_fin:
            query = query.filter(SLATracking.fecha_resolucion_real <= fecha_fin)
        
        trackings = query.all()
        
        if not trackings:
            return {
                'total': 0,
                'cumplidos': 0,
                'incumplidos': 0,
                'porcentaje_cumplimiento': 0
            }
        
        cumplidos = sum(1 for t in trackings if t.resolucion_cumplida)
        
        return {
            'total': len(trackings),
            'cumplidos': cumplidos,
            'incumplidos': len(trackings) - cumplidos,
            'porcentaje_cumplimiento': round((cumplidos / len(trackings)) * 100, 2)
        }
