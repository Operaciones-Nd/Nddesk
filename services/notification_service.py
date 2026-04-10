"""
Servicio de Notificaciones
Genera notificaciones dinámicas para usuarios
"""
from models import CambioIA, Solicitud, Usuario
from datetime import datetime, timedelta
from flask import url_for, current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class NotificationService:
    
    @staticmethod
    def obtener_cambios_no_validados():
        """Cuenta cambios IA pendientes de validación"""
        return CambioIA.query.filter_by(activo=True, validado=False, deleted_at=None).count()
    
    @staticmethod
    def generar_notificaciones(user):
        """Genera notificaciones según el rol del usuario"""
        if not user:
            return []
        
        notificaciones = []
        
        # Tickets nuevos para resolutores
        if user.is_resolutor:
            tickets_nuevos = NotificationService._contar_tickets_nuevos(user)
            if tickets_nuevos > 0:
                notificaciones.append({
                    'mensaje': f'{tickets_nuevos} ticket{"s" if tickets_nuevos > 1 else ""} nuevo{"s" if tickets_nuevos > 1 else ""} pendiente{"s" if tickets_nuevos > 1 else ""}',
                    'icono': 'fas fa-ticket-alt text-warning',
                    'url': url_for('solicitudes.index'),
                    'tiempo': 'Hoy'
                })
        
        # Tickets actualizados para solicitantes
        if user.rol == 'solicitante':
            tickets_actualizados = NotificationService._contar_tickets_actualizados(user)
            if tickets_actualizados > 0:
                notificaciones.append({
                    'mensaje': f'{tickets_actualizados} ticket{"s" if tickets_actualizados > 1 else ""} actualizado{"s" if tickets_actualizados > 1 else ""}',
                    'icono': 'fas fa-sync text-info',
                    'url': url_for('solicitudes.index'),
                    'tiempo': 'Hoy'
                })
        
        return notificaciones
    
    @staticmethod
    def _contar_tickets_nuevos(user):
        """Cuenta tickets nuevos asignados al resolutor"""
        try:
            return Solicitud.query.filter(
                Solicitud.seccion.in_([s.nombre for s in user.secciones]),
                Solicitud.estado == 'Pendiente',
                Solicitud.created_at >= datetime.now() - timedelta(hours=24),
                Solicitud.deleted_at == None
            ).count()
        except:
            return 0
    
    @staticmethod
    def _contar_tickets_actualizados(user):
        """Cuenta tickets actualizados del solicitante"""
        try:
            return Solicitud.query.filter(
                Solicitud.usuario_id == user.id,
                Solicitud.updated_at >= datetime.now() - timedelta(hours=24),
                Solicitud.updated_at > Solicitud.created_at,
                Solicitud.deleted_at == None
            ).count()
        except:
            return 0
    
    @staticmethod
    def enviar_email(destinatario, asunto, cuerpo_html):
        """Envía email usando Zoho Mail con SSL"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
            msg['To'] = destinatario
            msg['Subject'] = asunto
            
            msg.attach(MIMEText(cuerpo_html, 'html'))
            
            with smtplib.SMTP_SSL(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
                server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
                server.send_message(msg)
            
            current_app.logger.info(f'Email enviado a {destinatario}')
            return True
        except Exception as e:
            current_app.logger.error(f'Error enviando email: {str(e)}')
            return False
    
    @staticmethod
    def notify_new_ticket(ticket, resolutores):
        """Notifica creación de nuevo ticket a resolutores"""
        asunto = f'[NDdesk] Nuevo Ticket #{ticket.id} - {ticket.seccion}'
        
        cuerpo = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
                .header {{ background: #1e3a8a; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .ticket-info {{ background: #f8fafc; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0; }}
                .ticket-info p {{ margin: 8px 0; }}
                .btn {{ display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                .footer {{ background: #f8fafc; padding: 15px; text-align: center; font-size: 12px; color: #64748b; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎫 Nuevo Ticket Asignado</h1>
                </div>
                <div class="content">
                    <p>Hola,</p>
                    <p>Se ha creado un nuevo ticket que requiere tu atención:</p>
                    
                    <div class="ticket-info">
                        <p><strong>Ticket #:</strong> {ticket.id}</p>
                        <p><strong>Sección:</strong> {ticket.seccion}</p>
                        <p><strong>Prioridad:</strong> <span style="color: {'#ef4444' if ticket.prioridad == 'Alta' else '#f59e0b' if ticket.prioridad == 'Media' else '#10b981'};">{ticket.prioridad}</span></p>
                        <p><strong>Tipo:</strong> {ticket.tipo_contenido}</p>
                        <p><strong>Descripción:</strong> {ticket.descripcion[:200]}...</p>
                        <p><strong>Solicitante:</strong> {ticket.usuario.nombre if ticket.usuario else 'N/A'}</p>
                    </div>
                    
                    <a href="{url_for('solicitudes.ver', id=ticket.id, _external=True)}" class="btn">Ver Ticket Completo</a>
                </div>
                <div class="footer">
                    <p>NDdesk - Sistema de Gestión de Tickets</p>
                    <p>Nuestro Diario © 2025</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        for resolutor in resolutores:
            if resolutor.username and '@' in resolutor.username:
                NotificationService.enviar_email(resolutor.username, asunto, cuerpo)
    
    @staticmethod
    def notify_ticket_closed(ticket):
        """Notifica cierre de ticket al solicitante"""
        if not ticket.usuario or not ticket.usuario.username or '@' not in ticket.usuario.username:
            return
        
        asunto = f'[NDdesk] Ticket #{ticket.id} Cerrado'
        
        cuerpo = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
                .header {{ background: #10b981; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .ticket-info {{ background: #f0fdf4; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0; }}
                .ticket-info p {{ margin: 8px 0; }}
                .btn {{ display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                .footer {{ background: #f8fafc; padding: 15px; text-align: center; font-size: 12px; color: #64748b; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Ticket Cerrado</h1>
                </div>
                <div class="content">
                    <p>Hola {ticket.usuario.nombre},</p>
                    <p>Tu ticket ha sido cerrado exitosamente.</p>
                    
                    <div class="ticket-info">
                        <p><strong>Ticket #:</strong> {ticket.id}</p>
                        <p><strong>Estado:</strong> {ticket.estado}</p>
                        <p><strong>Solución:</strong> {ticket.solucion or 'Ver detalles en el sistema'}</p>
                    </div>
                    
                    <p>Si tienes alguna pregunta o el problema persiste, puedes reabrir el ticket.</p>
                    
                    <a href="{url_for('solicitudes.ver', id=ticket.id, _external=True)}" class="btn">Ver Detalles</a>
                </div>
                <div class="footer">
                    <p>NDdesk - Sistema de Gestión de Tickets</p>
                    <p>Nuestro Diario © 2025</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        NotificationService.enviar_email(ticket.usuario.username, asunto, cuerpo)
