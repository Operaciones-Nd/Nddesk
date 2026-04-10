from models import TurnoSemanal

class AssignmentService:
    EMAIL_MAPPING = {
        'Digital': 'digital.tickets@nuestrodiario.com.gt',
        'Deportes': 'deportes.tickets@nuestrodiario.com.gt',
        'Suave': 'softnews.tickets@nuestrodiario.com.gt',
        'Marketing de contenidos': 'marketing.tickets@nuestrodiario.com.gt',
        'Regionales': 'regionales.tickets@nuestrodiario.com.gt',
        'Soy502': 's502.tickets@soy502.com'
    }
    
    @staticmethod
    def auto_assign(ticket):
        turno = TurnoSemanal.get_turno_actual(ticket.seccion)
        if turno:
            ticket.resuelto_por = turno.analista_id
        return ticket
    
    @staticmethod
    def get_notification_email(seccion):
        return AssignmentService.EMAIL_MAPPING.get(seccion, 'tickets@nuestrodiario.com.gt')
