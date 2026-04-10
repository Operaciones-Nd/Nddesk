from models import Solicitud, AuditoriaTicket, db, Usuario
from services.assignment_service import AssignmentService
from services.email_service import EmailService
from services.sla_service import SLAService
from utils import ValidationError, TicketValidator

class TicketService:
    @staticmethod
    def create_ticket(data, user, ip_address):
        TicketValidator.validate_create(data)
        
        ticket = Solicitud(
            usuario_id=user.id,
            fecha_publicacion=data['fecha_publicacion'],
            medio=data['medio'],
            departamento=data['departamento'],
            seccion=data['seccion'],
            familia_servicios=data['familia_servicios'],
            servicio=data['servicio'],
            grupo_resuelve=data['grupo_resuelve'],
            email_notificacion=data['email_notificacion'],
            tipo_contenido=data['tipo_contenido'],
            descripcion=data['descripcion'],
            prioridad=data.get('prioridad', 'Media'),
            adjuntos=data.get('adjuntos')
        )
        
        db.session.add(ticket)
        db.session.flush()
        
        auditoria = AuditoriaTicket(
            ticket_id=ticket.id,
            usuario_id=user.id,
            accion='CREADO',
            ip_address=ip_address
        )
        db.session.add(auditoria)
        
        AssignmentService.auto_assign(ticket)
        SLAService.iniciar_tracking(ticket)
        
        db.session.commit()
        
        # Notificar al grupo del área
        EmailService.notify_ticket_created(ticket)
        
        return ticket
    
    @staticmethod
    def update_ticket(ticket, data, user, ip_address):
        changes = []
        for field in ['estado', 'prioridad', 'solucion', 'bitacora_publica', 'bitacora_oculta']:
            if field in data and getattr(ticket, field) != data[field]:
                old_value = getattr(ticket, field)
                setattr(ticket, field, data[field])
                changes.append((field, old_value, data[field]))
        
        if 'estado' in data and data['estado'] == 'Solucionado':
            SLAService.registrar_resolucion(ticket.id)
        
        for field, old, new in changes:
            auditoria = AuditoriaTicket(
                ticket_id=ticket.id,
                usuario_id=user.id,
                accion='EDITADO',
                campo_modificado=field,
                valor_anterior=str(old),
                valor_nuevo=str(new),
                ip_address=ip_address
            )
            db.session.add(auditoria)
        
        db.session.commit()
        
        # Notificar actualización al grupo
        if changes:
            EmailService.notify_ticket_updated(ticket)
        
        return ticket
    
    @staticmethod
    def close_ticket(ticket, user, ip_address):
        from datetime import datetime
        ticket.estado = 'Cerrado'
        ticket.fecha_cierre = datetime.now()
        ticket.resuelto_por = user.id
        
        SLAService.registrar_resolucion(ticket.id)
        
        auditoria = AuditoriaTicket(
            ticket_id=ticket.id,
            usuario_id=user.id,
            accion='CERRADO',
            ip_address=ip_address
        )
        db.session.add(auditoria)
        
        db.session.commit()
        
        # Notificar cierre al grupo
        EmailService.notify_ticket_closed(ticket)
        
        return ticket

class BaseModel:
    def save(self):
        db.session.add(self)
        return self
