from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import CambioIA, Flujo, ReglaAutomatizacion, SLAConfig, Usuario, db
from services.flujo_generator_service import FlujoGeneratorService
from utils import login_required
import json

cambios_ia_bp = Blueprint('cambios_ia', __name__, url_prefix='/cambios-ia')

@cambios_ia_bp.route('/')
@login_required
def index():
    user = Usuario.query.get(session['user_id'])
    if not (user.is_admin or user.is_coordinador):
        flash('Sin permisos', 'danger')
        return redirect(url_for('solicitudes.index'))
    
    pendientes = CambioIA.get_pendientes()
    activos = CambioIA.query.filter_by(activo=True, validado=False, deleted_at=None).order_by(CambioIA.fecha_activacion.desc()).all()
    
    return render_template('cambios_ia/index.html', pendientes=pendientes, activos=activos)

@cambios_ia_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    user = Usuario.query.get(session['user_id'])
    if not user.is_admin:
        flash('Solo admin puede crear cambios', 'danger')
        return redirect(url_for('cambios_ia.index'))
    
    # Recuperar último prompt con error si existe
    ultimo_error = session.pop('ultimo_prompt_error', None)
    
    if request.method == 'POST':
        from services.comando_ia_simple import ComandoIASimple
        
        prompt = request.form['prompt']
        
        # Detectar si es crear usuario
        if 'usuario' in prompt.lower() and 'llamado' in prompt.lower():
            resultado = ComandoIASimple.crear_usuario(prompt, user)
        else:
            from services.comando_ia_service import ComandoIAService
            resultado = ComandoIAService.ejecutar_comando(prompt, user)
        
        if resultado.get('error'):
            flash(resultado['error'], 'danger')
            # Guardar el prompt con error para que pueda corregirlo
            session['ultimo_prompt_error'] = prompt
            return redirect(url_for('cambios_ia.nuevo'))
        else:
            flash(resultado['mensaje'], 'success')
            
            # Crear registro del cambio
            cambio = CambioIA(
                titulo=resultado['mensaje'],
                descripcion=str(resultado.get('datos', {})),
                prompt_usuario=prompt,
                tipo_cambio='comando',
                creado_por=user.id,
                activo=True
            )
            db.session.add(cambio)
            db.session.commit()
        
        return redirect(url_for('cambios_ia.index'))
    
    return render_template('cambios_ia/nuevo.html', ultimo_error=ultimo_error)

@cambios_ia_bp.route('/<int:id>/activar', methods=['POST'])
@login_required
def activar(id):
    user = Usuario.query.get(session['user_id'])
    if not user.is_admin:
        return jsonify({'error': 'Sin permisos'}), 403
    
    cambio = CambioIA.query.get_or_404(id)
    cambio.activar(user.id)
    
    return jsonify({'success': True, 'message': 'Cambio activado en producción'})

@cambios_ia_bp.route('/<int:id>/desactivar', methods=['POST'])
@login_required
def desactivar(id):
    user = Usuario.query.get(session['user_id'])
    if not user.is_admin:
        return jsonify({'error': 'Sin permisos'}), 403
    
    cambio = CambioIA.query.get_or_404(id)
    cambio.desactivar()
    
    return jsonify({'success': True, 'message': 'Cambio desactivado'})

@cambios_ia_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    user = Usuario.query.get(session['user_id'])
    if not user.is_admin:
        return jsonify({'error': 'Sin permisos'}), 403
    
    cambio = CambioIA.query.get_or_404(id)
    
    # Eliminar elemento relacionado
    if cambio.flujo_id:
        Flujo.query.filter_by(id=cambio.flujo_id).delete()
    elif cambio.regla_id:
        ReglaAutomatizacion.query.filter_by(id=cambio.regla_id).delete()
    
    db.session.delete(cambio)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Cambio eliminado'})

@cambios_ia_bp.route('/<int:id>/validar', methods=['POST'])
@login_required
def validar(id):
    user = Usuario.query.get(session['user_id'])
    if not (user.is_admin or user.is_coordinador):
        return jsonify({'error': 'Sin permisos'}), 403
    
    cambio = CambioIA.query.get_or_404(id)
    cambio.validar()
    
    return jsonify({'success': True, 'message': 'Cambio validado'})
