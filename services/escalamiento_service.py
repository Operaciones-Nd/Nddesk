from datetime import datetime, timedelta
from models.escalamiento import Escalamiento, EscalamientoConfig
from models.solicitud import Solicitud
from models.base import db

class EscalamientoService:
    
    @staticmethod
    def verificar_escalamiento_automatico():
        """Verifica tickets que requieren escalamiento automático"""
        tickets_escalados = []
        
        # Obtener tickets abiertos
        tickets = Solicitud.query.filter(
            Solicitud.estado.in_(['Pendiente', 'Planificado']),
            Solicitud.deleted_at.is_(None)
        ).all()
        
        for ticket in tickets:
            config = EscalamientoConfig.get_config(
                tipo_ticket=ticket.tipo_ticket or 'REQUERIMIENTO',
                prioridad=ticket.prioridad,
                seccion=ticket.seccion
            )
            
            if not config:
                continue
            
            nivel_actual = Escalamiento.get_nivel_actual(ticket.id)
            tiempo_transcurrido = (datetime.now() - ticket.fecha_solicitud).total_seconds() / 60
            
            # Verificar si debe escalar
            debe_escalar = False
            nuevo_nivel = nivel_actual
            nuevo_grupo = None
            
            if nivel_actual == 1 and tiempo_transcurrido >= config.nivel_1_tiempo:
                debe_escalar = True
                nuevo_nivel = 2
                nuevo_grupo = config.nivel_2_grupo
            elif nivel_actual == 2 and config.nivel_2_tiempo and tiempo_transcurrido >= config.nivel_2_tiempo:
                debe_escalar = True
                nuevo_nivel = 3
                nuevo_grupo = config.nivel_3_grupo
            
            if debe_escalar and nuevo_grupo:
                EscalamientoService.escalar_ticket(
                    ticket_id=ticket.id,
                    nivel_nuevo=nuevo_nivel,
                    grupo_nuevo=nuevo_grupo,
                    razon=f"Escalamiento automático por tiempo ({int(tiempo_transcurrido)} minutos)",
                    tipo='automatico'
                )
                tickets_escalados.append(ticket.id)
        
        return tickets_escalados
    
    @staticmethod
    def escalar_ticket(ticket_id, nivel_nuevo, grupo_nuevo, razon, tipo='manual', usuario_id=None):
        """Escala un ticket a un nuevo nivel"""
        ticket = Solicitud.query.get(ticket_id)
        if not ticket:
            return False
        
        nivel_actual = Escalamiento.get_nivel_actual(ticket_id)
        grupo_actual = ticket.grupo_resuelve
        
        escalamiento = Escalamiento(
            solicitud_id=ticket_id,
            nivel_anterior=nivel_actual,
            nivel_actual=nivel_nuevo,
            grupo_anterior=grupo_actual,
            grupo_actual=grupo_nuevo,
            tipo=tipo,
            razon=razon,
            escalado_por=usuario_id
        )
        
        # Actualizar grupo del ticket
        ticket.grupo_resuelve = grupo_nuevo
        
        db.session.add(escalamiento)
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_historial_escalamiento(ticket_id):
        """Obtiene el historial de escalamientos de un ticket"""
        return Escalamiento.get_by_ticket(ticket_id)
    
    @staticmethod
    def get_metricas_escalamiento(fecha_inicio=None, fecha_fin=None):
        """Calcula métricas de escalamiento"""
        query = Escalamiento.query
        
        if fecha_inicio:
            query = query.filter(Escalamiento.fecha_escalamiento >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Escalamiento.fecha_escalamiento <= fecha_fin)
        
        escalamientos = query.all()
        
        if not escalamientos:
            return {
                'total': 0,
                'automaticos': 0,
                'manuales': 0,
                'por_nivel': {}
            }
        
        automaticos = sum(1 for e in escalamientos if e.tipo == 'automatico')
        por_nivel = {}
        
        for e in escalamientos:
            nivel = f"Nivel {e.nivel_actual}"
            por_nivel[nivel] = por_nivel.get(nivel, 0) + 1
        
        return {
            'total': len(escalamientos),
            'automaticos': automaticos,
            'manuales': len(escalamientos) - automaticos,
            'por_nivel': por_nivel
        }
