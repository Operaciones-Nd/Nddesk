from flask import Blueprint, request, jsonify, session
from models import Solicitud, Usuario, db
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta
from utils import login_required

solicitudes_dt_bp = Blueprint('solicitudes_dt', __name__)

@solicitudes_dt_bp.route('/api/tickets/datatable', methods=['POST'])
@login_required
def datatable_tickets():
    """
    Endpoint para DataTables con procesamiento del lado del servidor.
    Soporta paginación, búsqueda, ordenamiento y filtros avanzados.
    """
    user = Usuario.query.get(session['user_id'])
    
    # Parámetros de DataTables
    draw = request.form.get('draw', type=int, default=1)
    start = request.form.get('start', type=int, default=0)
    length = request.form.get('length', type=int, default=25)
    search_value = request.form.get('search[value]', default='')
    order_column_idx = request.form.get('order[0][column]', type=int, default=0)
    order_dir = request.form.get('order[0][dir]', default='desc')
    
    # Filtros personalizados
    tab_filter = request.form.get('tab', default='activos')
    estado_filter = request.form.get('estado', default='')
    prioridad_filter = request.form.get('prioridad', default='')
    seccion_filter = request.form.get('seccion', default='')
    fecha_inicio = request.form.get('fecha_inicio', default='')
    fecha_fin = request.form.get('fecha_fin', default='')
    
    # Query base según rol
    query = Solicitud.query.filter_by(deleted_at=None)
    
    if user.is_admin or user.is_coordinador:
        # Admin y Coordinador ven todos
        pass
    elif user.is_resolutor:
        # Resolutores ven tickets de sus secciones o asignados a ellos
        secciones_usuario = [s.nombre for s in user.secciones]
        query = query.filter(
            or_(
                Solicitud.seccion.in_(secciones_usuario),
                Solicitud.resuelto_por == user.id
            )
        )
    else:
        # Solicitantes ven tickets de su departamento
        if user.departamento_obj:
            query = query.filter_by(departamento=user.departamento_obj.nombre)
        else:
            # Si no tiene departamento, solo ve los suyos
            query = query.filter_by(usuario_id=user.id)
    
    # Aplicar filtro de TAB (vista por defecto)
    if tab_filter == 'activos':
        # Activos: Pendiente, Planificado, Escalado de últimos 30 días
        fecha_limite = datetime.now() - timedelta(days=30)
        query = query.filter(
            and_(
                Solicitud.estado.in_(['Pendiente', 'Planificado', 'Escalado']),
                Solicitud.created_at >= fecha_limite
            )
        )
    elif tab_filter == 'solucionados':
        query = query.filter_by(estado='Solucionado')
    elif tab_filter == 'cerrados':
        query = query.filter_by(estado='Cerrado')
    elif tab_filter == 'historico':
        # Histórico: todos sin restricción de fecha
        pass
    
    # Filtros adicionales
    if estado_filter:
        query = query.filter_by(estado=estado_filter)
    
    if prioridad_filter:
        query = query.filter_by(prioridad=prioridad_filter)
    
    if seccion_filter:
        query = query.filter_by(seccion=seccion_filter)
    
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            query = query.filter(Solicitud.created_at >= fecha_inicio_dt)
        except:
            pass
    
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            fecha_fin_dt = fecha_fin_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(Solicitud.created_at <= fecha_fin_dt)
        except:
            pass
    
    # Búsqueda global (ID, descripción, solicitante)
    if search_value:
        # Búsqueda por ID (con o sin #, con o sin ceros)
        search_clean = search_value.lstrip('#')
        if search_clean.isdigit():
            try:
                ticket_id = int(search_clean)
                query = query.filter(Solicitud.id == ticket_id)
            except:
                pass
        else:
            # Búsqueda en descripción, tipo_contenido, y nombre de solicitante
            query = query.join(Usuario, Solicitud.usuario_id == Usuario.id).filter(
                or_(
                    Solicitud.descripcion.ilike(f'%{search_value}%'),
                    Solicitud.tipo_contenido.ilike(f'%{search_value}%'),
                    Solicitud.seccion.ilike(f'%{search_value}%'),
                    Usuario.nombre.ilike(f'%{search_value}%')
                )
            )
    
    # Total de registros (sin filtros)
    total_records = Solicitud.query.filter_by(deleted_at=None).count()
    
    # Total de registros filtrados
    filtered_records = query.count()
    
    # Ordenamiento
    columns = [
        Solicitud.id,
        Solicitud.estado,
        Solicitud.prioridad,
        Solicitud.seccion,
        Solicitud.resuelto_por,
        Solicitud.created_at,
        Solicitud.usuario_id
    ]
    
    if order_column_idx < len(columns):
        order_column = columns[order_column_idx]
        if order_dir == 'asc':
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())
    else:
        query = query.order_by(Solicitud.created_at.desc())
    
    # Paginación
    tickets = query.offset(start).limit(length).all()
    
    # Formatear datos para DataTables
    data = []
    for ticket in tickets:
        resolutor = Usuario.query.get(ticket.resuelto_por) if ticket.resuelto_por else None
        solicitante = Usuario.query.get(ticket.usuario_id)
        
        # Badge de estado
        estado_colors = {
            'Pendiente': {'bg': '#fef3c7', 'color': '#92400e'},
            'Planificado': {'bg': '#dbeafe', 'color': '#1e40af'},
            'Solucionado': {'bg': '#d1fae5', 'color': '#065f46'},
            'Cerrado': {'bg': '#e5e7eb', 'color': '#374151'},
            'Escalado': {'bg': '#fed7aa', 'color': '#9a3412'}
        }
        estado_style = estado_colors.get(ticket.estado, {'bg': '#dbeafe', 'color': '#1e40af'})
        
        estado_badge = f'''<span class="badge" style="background: {estado_style['bg']}; color: {estado_style['color']}; padding: 0.4rem 0.8rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600; white-space: nowrap;">
            {ticket.estado}
            {'<i class="fas fa-redo ml-1" title="Reabierto" style="font-size: 0.7rem;"></i>' if ticket.veces_reabierto and ticket.veces_reabierto > 0 else ''}
        </span>'''
        
        # Badge de prioridad
        prioridad_colors = {
            'Alta': {'bg': '#fee2e2', 'color': '#991b1b', 'icon': '<i class="fas fa-arrow-up" style="font-size: 0.7rem;"></i> '},
            'Media': {'bg': '#fef3c7', 'color': '#92400e', 'icon': ''},
            'Baja': {'bg': '#f3f4f6', 'color': '#374151', 'icon': ''}
        }
        prioridad_style = prioridad_colors.get(ticket.prioridad, {'bg': '#f3f4f6', 'color': '#374151', 'icon': ''})
        
        prioridad_badge = f'''<span class="badge" style="background: {prioridad_style['bg']}; color: {prioridad_style['color']}; padding: 0.4rem 0.8rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600; white-space: nowrap;">
            {prioridad_style['icon']}{ticket.prioridad}
        </span>'''
        
        # Asignado a
        if resolutor:
            asignado = f'''<span class="badge" style="background: #dbeafe; color: #1e40af; padding: 0.4rem 0.8rem; border-radius: 6px; font-size: 0.75rem; white-space: nowrap;">
                <i class="fas fa-user" style="font-size: 0.7rem;"></i> {resolutor.nombre.split()[0]}
            </span>'''
        else:
            asignado = '<span class="badge" style="background: #f3f4f6; color: #6b7280; padding: 0.4rem 0.8rem; border-radius: 6px; font-size: 0.75rem; white-space: nowrap;">Sin asignar</span>'
        
        # Tiempo
        tiempo_html = f'''<small class="text-muted" style="font-size: 0.8rem; white-space: nowrap;">
            {ticket.created_at.strftime('%d/%m/%Y')}
        </small>'''
        
        # Solicitante
        solicitante_html = f'''<div class="d-flex align-items-center">
            <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center" style="width: 28px; height: 28px; font-size: 0.7rem; font-weight: 600; margin-right: 0.5rem; flex-shrink: 0;">
                {solicitante.nombre[:2].upper() if solicitante else 'NA'}
            </div>
            <span style="font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{solicitante.nombre.split()[0] if solicitante else 'N/A'}</span>
        </div>'''
        
        # Acciones
        acciones = f'''<a href="/solicitudes/{ticket.id}" class="btn btn-sm btn-primary" title="Ver ticket" style="padding: 0.35rem 0.75rem; border-radius: 6px;">
            <i class="fas fa-eye" style="font-size: 0.85rem;"></i> Ver
        </a>'''
        
        data.append([
            f'<a href="/solicitudes/{ticket.id}" style="color: #0d6efd; font-weight: 600; font-size: 0.9rem;">#{ticket.id:05d}</a>',
            estado_badge,
            prioridad_badge,
            ticket.seccion,
            asignado,
            tiempo_html,
            solicitante_html,
            acciones
        ])
    
    return jsonify({
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    })
