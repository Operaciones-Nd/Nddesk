from models import Solicitud
from datetime import datetime, timedelta

class TicketRepository:
    @staticmethod
    def find_by_user_and_status(user_id, status):
        return Solicitud.get_active().filter_by(
            usuario_id=user_id, 
            estado=status
        ).all()
    
    @staticmethod
    def find_overdue_tickets():
        tickets = Solicitud.get_active().filter(
            Solicitud.estado.in_(['Pendiente', 'Planificado'])
        ).all()
        return [t for t in tickets if t.is_overdue]
    
    @staticmethod
    def find_by_date_range(fecha_inicio, fecha_fin):
        return Solicitud.get_active().filter(
            Solicitud.created_at >= fecha_inicio,
            Solicitud.created_at <= fecha_fin
        ).all()
    
    @staticmethod
    def get_statistics():
        total = Solicitud.get_active().count()
        pendientes = Solicitud.get_active().filter_by(estado='Pendiente').count()
        planificados = Solicitud.get_active().filter_by(estado='Planificado').count()
        solucionados = Solicitud.get_active().filter_by(estado='Solucionado').count()
        cerrados = Solicitud.get_active().filter_by(estado='Cerrado').count()
        
        return {
            'total': total,
            'pendientes': pendientes,
            'planificados': planificados,
            'solucionados': solucionados,
            'cerrados': cerrados
        }
