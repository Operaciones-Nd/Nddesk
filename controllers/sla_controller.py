from flask import Blueprint, jsonify, request, session
from models import SLATracking, Solicitud, Usuario
from services import SLAService
from utils import login_required
from datetime import datetime

sla_bp = Blueprint('sla', __name__, url_prefix='/api/sla')

@sla_bp.route('/pausar/<int:ticket_id>', methods=['POST'])
@login_required
def pausar(ticket_id):
    razon = request.json.get('razon')
    if not razon:
        return jsonify({'error': 'Razón requerida'}), 400
    
    success = SLAService.pausar_sla(ticket_id, razon, session['user_id'])
    if success:
        return jsonify({'message': 'SLA pausado'})
    return jsonify({'error': 'No se pudo pausar'}), 400

@sla_bp.route('/reanudar/<int:ticket_id>', methods=['POST'])
@login_required
def reanudar(ticket_id):
    success = SLAService.reanudar_sla(ticket_id)
    if success:
        return jsonify({'message': 'SLA reanudado'})
    return jsonify({'error': 'No se pudo reanudar'}), 400

@sla_bp.route('/metricas')
@login_required
def metricas():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
    
    metricas = SLAService.get_metricas_sla(fecha_inicio, fecha_fin)
    return jsonify(metricas)
