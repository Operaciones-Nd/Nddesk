from flask import Blueprint, jsonify, request, session, flash, redirect, url_for
from models import Escalamiento, Solicitud
from services import EscalamientoService
from utils import login_required

escalamiento_bp = Blueprint('escalamiento', __name__, url_prefix='/escalamiento')

@escalamiento_bp.route('/<int:ticket_id>/escalar', methods=['POST'])
@login_required
def escalar(ticket_id):
    nivel = int(request.form.get('nivel', 2))
    grupo = request.form.get('grupo')
    razon = request.form.get('razon')
    
    if not grupo or not razon:
        flash('Grupo y razón son requeridos', 'danger')
        return redirect(url_for('solicitudes.ver', id=ticket_id))
    
    success = EscalamientoService.escalar_ticket(
        ticket_id=ticket_id,
        nivel_nuevo=nivel,
        grupo_nuevo=grupo,
        razon=razon,
        tipo='manual',
        usuario_id=session['user_id']
    )
    
    if success:
        flash('Ticket escalado exitosamente', 'success')
    else:
        flash('Error al escalar ticket', 'danger')
    
    return redirect(url_for('solicitudes.ver', id=ticket_id))

@escalamiento_bp.route('/api/metricas')
@login_required
def metricas():
    from datetime import datetime
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
    
    metricas = EscalamientoService.get_metricas_escalamiento(fecha_inicio, fecha_fin)
    return jsonify(metricas)
