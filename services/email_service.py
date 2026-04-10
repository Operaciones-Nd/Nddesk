"""
Servicio de Email para NDDesk
Envía notificaciones a grupos de Zoho Mail según el área del ticket
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, url_for
from datetime import datetime

# Email por defecto si no se encuentra
DEFAULT_EMAIL = 'digital.tickets@nuestrodiario.com.gt'

class EmailService:
    
    @staticmethod
    def get_group_email(area):
        """Obtiene el email del grupo desde la base de datos"""
        from models.seccion import Seccion
        
        seccion = Seccion.query.filter_by(nombre=area, deleted_at=None, activo=True).first()
        
        if seccion and seccion.email_notificacion:
            return seccion.email_notificacion
        
        return DEFAULT_EMAIL
    
    @staticmethod
    def send_email(to_email, subject, html_body):
        """Envía email usando Zoho Mail SMTP con SSL"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            with smtplib.SMTP_SSL(
                current_app.config['MAIL_SERVER'], 
                current_app.config['MAIL_PORT']
            ) as server:
                server.login(
                    current_app.config['MAIL_USERNAME'],
                    current_app.config['MAIL_PASSWORD']
                )
                server.send_message(msg)
            
            current_app.logger.info(f'Email enviado a {to_email}: {subject}')
            return True
            
        except smtplib.SMTPException as e:
            current_app.logger.error(f'Error SMTP enviando email a {to_email}: {str(e)}')
            return False
        except Exception as e:
            current_app.logger.error(f'Error enviando email a {to_email}: {str(e)}')
            return False
    
    @staticmethod
    def build_ticket_html(ticket, event_type='created'):
        """Construye el HTML del correo según el evento"""
        
        event_config = {
            'created': {
                'title': '🎫 Nuevo Ticket Creado',
                'color': '#1e3a8a',
                'bg_color': '#eff6ff'
            },
            'updated': {
                'title': '🔄 Ticket Actualizado',
                'color': '#f59e0b',
                'bg_color': '#fffbeb'
            },
            'closed': {
                'title': '✅ Ticket Cerrado',
                'color': '#10b981',
                'bg_color': '#f0fdf4'
            }
        }
        
        config = event_config.get(event_type, event_config['created'])
        
        prioridad_color = {
            'Alta': '#ef4444',
            'Media': '#f59e0b',
            'Baja': '#10b981'
        }.get(ticket.prioridad, '#64748b')
        
        ticket_url = f"https://nddesk.nuestrodiario.net/solicitudes/{ticket.id}"
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background-color: #f3f4f6;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background-color: {config['color']}; padding: 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 600;">{config['title']}</h1>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 30px;">
                            <p style="margin: 0 0 20px 0; color: #111827; font-size: 16px;">
                                Se ha {event_type == 'created' and 'creado un nuevo' or event_type == 'updated' and 'actualizado el' or 'cerrado el'} ticket en NDDesk:
                            </p>
                            
                            <!-- Ticket Info Box -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: {config['bg_color']}; border-left: 4px solid {config['color']}; border-radius: 4px; margin: 20px 0;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <table width="100%" cellpadding="8" cellspacing="0">
                                            <tr>
                                                <td style="color: #6b7280; font-size: 14px; font-weight: 600;">Ticket #</td>
                                                <td style="color: #111827; font-size: 14px; font-weight: 700;">{ticket.id}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #6b7280; font-size: 14px; font-weight: 600;">Área</td>
                                                <td style="color: #111827; font-size: 14px;">{ticket.seccion or 'N/A'}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #6b7280; font-size: 14px; font-weight: 600;">Descripción</td>
                                                <td style="color: #111827; font-size: 14px;">{ticket.descripcion[:150]}{'...' if len(ticket.descripcion) > 150 else ''}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #6b7280; font-size: 14px; font-weight: 600;">Estado</td>
                                                <td style="color: #111827; font-size: 14px;">{ticket.estado}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #6b7280; font-size: 14px; font-weight: 600;">Prioridad</td>
                                                <td style="color: {prioridad_color}; font-size: 14px; font-weight: 600;">{ticket.prioridad}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #6b7280; font-size: 14px; font-weight: 600;">Tipo</td>
                                                <td style="color: #111827; font-size: 14px;">{ticket.tipo_contenido or 'N/A'}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #6b7280; font-size: 14px; font-weight: 600;">Solicitante</td>
                                                <td style="color: #111827; font-size: 14px;">{ticket.usuario.nombre if ticket.usuario else 'N/A'}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #6b7280; font-size: 14px; font-weight: 600;">Fecha</td>
                                                <td style="color: #111827; font-size: 14px;">{ticket.created_at.strftime('%d/%m/%Y %H:%M') if ticket.created_at else 'N/A'}</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- CTA Button -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{ticket_url}" style="display: inline-block; background-color: #3b82f6; color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 6px; font-size: 16px; font-weight: 600;">Ver Ticket Completo</a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0; color: #6b7280; font-size: 12px;">
                                <strong>NDDesk</strong> - Sistema de Gestión de Tickets<br>
                                Nuestro Diario © {datetime.now().year}
                            </p>
                            <p style="margin: 10px 0 0 0; color: #9ca3af; font-size: 11px;">
                                Este correo fue enviado automáticamente. No responder.
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    
    @staticmethod
    def notify_ticket_created(ticket):
        """Notifica creación de ticket al grupo y departamento correspondiente"""
        from models.departamento import Departamento
        
        # Notificar a la sección
        area = ticket.seccion
        group_email = EmailService.get_group_email(area)
        subject = f'[NDDesk] Nuevo Ticket #{ticket.id} - {area}'
        html = EmailService.build_ticket_html(ticket, 'created')
        EmailService.send_email(group_email, subject, html)
        
        # Notificar al departamento si tiene email configurado
        if ticket.departamento:
            dept = Departamento.query.filter_by(nombre=ticket.departamento, deleted_at=None).first()
            if dept and dept.email_notificacion:
                EmailService.send_email(dept.email_notificacion, subject, html)
        
        return True
    
    @staticmethod
    def notify_ticket_updated(ticket):
        """Notifica actualización de ticket al grupo y departamento correspondiente"""
        from models.departamento import Departamento
        
        # Notificar a la sección
        area = ticket.seccion
        group_email = EmailService.get_group_email(area)
        subject = f'[NDDesk] Ticket #{ticket.id} Actualizado - {area}'
        html = EmailService.build_ticket_html(ticket, 'updated')
        EmailService.send_email(group_email, subject, html)
        
        # Notificar al departamento si tiene email configurado
        if ticket.departamento:
            dept = Departamento.query.filter_by(nombre=ticket.departamento, deleted_at=None).first()
            if dept and dept.email_notificacion:
                EmailService.send_email(dept.email_notificacion, subject, html)
        
        return True
    
    @staticmethod
    def notify_new_comment(ticket, comentario):
        """Notifica nuevo comentario en ticket a sección y departamento"""
        from models.departamento import Departamento
        
        # Solo notificar comentarios públicos
        if comentario.es_interno:
            return True
        
        # Notificar a la sección
        area = ticket.seccion
        group_email = EmailService.get_group_email(area)
        subject = f'[NDDesk] Nuevo Comentario en Ticket #{ticket.id}'
        html = EmailService.build_comment_html(ticket, comentario)
        EmailService.send_email(group_email, subject, html)
        
        # Notificar al departamento si tiene email configurado
        if ticket.departamento:
            dept = Departamento.query.filter_by(nombre=ticket.departamento, deleted_at=None).first()
            if dept and dept.email_notificacion:
                EmailService.send_email(dept.email_notificacion, subject, html)
        
        return True
    
    @staticmethod
    def build_comment_html(ticket, comentario):
        """Construye el HTML del correo para nuevo comentario"""
        ticket_url = f"https://nddesk.nuestrodiario.net/solicitudes/{ticket.id}#seguimiento"
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background-color: #f3f4f6;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background-color: #7c3aed; padding: 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 600;">💬 Nuevo Comentario</h1>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 30px;">
                            <p style="margin: 0 0 20px 0; color: #111827; font-size: 16px;">
                                Se ha agregado un nuevo comentario al ticket #{ticket.id}:
                            </p>
                            
                            <!-- Ticket Info -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #faf5ff; border-left: 4px solid #7c3aed; border-radius: 4px; margin: 20px 0;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <table width="100%" cellpadding="8" cellspacing="0">
                                            <tr>
                                                <td style="color: #6b7280; font-size: 14px; font-weight: 600;">Ticket #</td>
                                                <td style="color: #111827; font-size: 14px; font-weight: 700;">{ticket.id}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #6b7280; font-size: 14px; font-weight: 600;">Área</td>
                                                <td style="color: #111827; font-size: 14px;">{ticket.seccion or 'N/A'}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #6b7280; font-size: 14px; font-weight: 600;">Comentario de</td>
                                                <td style="color: #111827; font-size: 14px;">{comentario.usuario.nombre if comentario.usuario else 'N/A'}</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Comment Box -->
                            <div style="background: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0;">
                                <p style="margin: 0; color: #111827; font-size: 14px; line-height: 1.6;">{comentario.contenido[:300]}{'...' if len(comentario.contenido) > 300 else ''}</p>
                            </div>
                            
                            <!-- CTA Button -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{ticket_url}" style="display: inline-block; background-color: #7c3aed; color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 6px; font-size: 16px; font-weight: 600;">Ver Comentario Completo</a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0; color: #6b7280; font-size: 12px;">
                                <strong>NDDesk</strong> - Sistema de Gestión de Tickets<br>
                                Nuestro Diario © {datetime.now().year}
                            </p>
                            <p style="margin: 10px 0 0 0; color: #9ca3af; font-size: 11px;">
                                Este correo fue enviado automáticamente. No responder.
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    
    @staticmethod
    def notify_ticket_closed(ticket):
        """Notifica cierre de ticket al grupo correspondiente"""
        area = ticket.seccion
        group_email = EmailService.get_group_email(area)
        subject = f'[NDDesk] Ticket #{ticket.id} Cerrado - {area}'
        html = EmailService.build_ticket_html(ticket, 'closed')
        
        return EmailService.send_email(group_email, subject, html)
    
    @staticmethod
    def enviar_reporte_semanal(destinatarios, archivo_pdf, datos):
        """Envía el informe semanal por correo con el PDF adjunto"""
        from email.mime.base import MIMEBase
        from email import encoders
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
            msg['To'] = ', '.join(destinatarios)
            msg['Subject'] = f"Informe Semanal de Cumplimiento Editorial - {datos['fecha_inicio'].strftime('%d/%m/%Y')}"
            
            # Cuerpo del email
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #1e40af;">Informe Semanal de Cumplimiento Editorial</h2>
        <p>Estimado equipo de Redacción,</p>
        <p>Adjunto encontrarán el informe semanal de cumplimiento editorial correspondiente a la semana del 
        <strong>{datos['fecha_inicio'].strftime('%d/%m/%Y')}</strong> al 
        <strong>{datos['fecha_fin'].strftime('%d/%m/%Y')}</strong>.</p>
        
        <div style="background: #f8fafc; padding: 15px; border-left: 4px solid #3b82f6; margin: 20px 0;">
            <h3 style="margin-top: 0;">Resumen Rápido:</h3>
            <ul style="margin: 0; padding-left: 20px;">
                <li>Total de solicitudes: <strong>{datos['total']}</strong></li>
                <li>Publicadas a tiempo: <strong>{datos['a_tiempo']}</strong></li>
                <li>Fuera de fecha: <strong>{datos['fuera_fecha']}</strong></li>
                <li>Porcentaje de cumplimiento: <strong>{datos['porcentaje_cumplimiento']}%</strong></li>
            </ul>
        </div>
        
        <p>Para ver el informe completo con detalles, gráficas y recomendaciones, por favor revise el archivo PDF adjunto.</p>
        
        <p style="margin-top: 30px;">Saludos cordiales,<br>
        <strong>Sistema NDDesk</strong></p>
        
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
        <p style="font-size: 12px; color: #64748b; text-align: center;">
            Este correo fue generado automáticamente por el sistema NDDesk<br>
            Nuestro Diario © {datetime.now().year}
        </p>
    </div>
</body>
</html>
"""
            
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # Adjuntar PDF
            with open(archivo_pdf, 'rb') as f:
                part = MIMEBase('application', 'pdf')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{os.path.basename(archivo_pdf)}"'
                )
                msg.attach(part)
            
            # Enviar
            with smtplib.SMTP_SSL(
                current_app.config['MAIL_SERVER'], 
                current_app.config['MAIL_PORT']
            ) as server:
                server.login(
                    current_app.config['MAIL_USERNAME'],
                    current_app.config['MAIL_PASSWORD']
                )
                server.send_message(msg)
            
            current_app.logger.info(f'Informe semanal enviado a {destinatarios}')
            return True
            
        except Exception as e:
            current_app.logger.error(f'Error enviando informe semanal: {str(e)}')
            return False
