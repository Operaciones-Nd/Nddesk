from flask import Blueprint, jsonify, request, session
from models import ArticuloKB, Usuario
from services.ia_help_service import IAHelpService
from utils import login_required

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/ayuda', methods=['POST'])
@login_required
def ayuda():
    """Agente IA de Ayuda - Solo responde preguntas y guía"""
    try:
        pregunta = request.json.get('pregunta', '').strip()
        user = Usuario.query.get(session['user_id'])
        
        if not pregunta:
            return jsonify({
                'respuesta': '¡Hola! Soy tu asistente virtual. Pregunta lo que necesites sobre el sistema.',
                'tipo': 'saludo'
            })
        
        # Generar respuesta usando el servicio de IA
        respuesta_data = IAHelpService.responder(pregunta, user.rol)
        
        return jsonify(respuesta_data)
    except Exception as e:
        return jsonify({
            'respuesta': 'Lo siento, ocurrió un error. Por favor intenta de nuevo.',
            'tipo': 'error'
        }), 500
