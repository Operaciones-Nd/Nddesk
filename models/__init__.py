from models.base import db, BaseModel
from models.usuario_secciones import usuario_secciones
from models.usuario import Usuario
from models.solicitud import Solicitud
from models.turno import TurnoSemanal
from models.auditoria import AuditoriaTicket, AuditoriaUsuario, IntentoLogin
from models.comentario import Comentario
from models.comentario_ticket import ComentarioTicket
from models.adjunto_ticket import AdjuntoTicket
from models.calificacion_ticket import CalificacionTicket
from models.tipo_ticket import TipoTicket
from models.sla import SLAConfig, SLATracking, SLAPausa
from models.escalamiento import Escalamiento, EscalamientoConfig
from models.kb import ArticuloKB, VinculoTicketKB
from models.flujo import Flujo, Transicion, ReglaAutomatizacion
from models.cambio_ia import CambioIA
from models.seccion import Seccion, SeccionResolutor
from models.departamento import Departamento
from models.servicio import Servicio
from models.subcategoria import Subcategoria
from models.report import Report

__all__ = ['db', 'BaseModel', 'Usuario', 'Solicitud', 'TurnoSemanal', 
           'AuditoriaTicket', 'AuditoriaUsuario', 'IntentoLogin', 'Comentario',
           'ComentarioTicket', 'AdjuntoTicket', 'CalificacionTicket',
           'TipoTicket', 'SLAConfig', 'SLATracking', 'SLAPausa',
           'Escalamiento', 'EscalamientoConfig', 'ArticuloKB', 'VinculoTicketKB',
           'Flujo', 'Transicion', 'ReglaAutomatizacion', 'CambioIA',
           'Seccion', 'SeccionResolutor', 'Departamento', 'usuario_secciones',
           'Servicio', 'Subcategoria', 'Report']
