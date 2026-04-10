from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import Flujo, Transicion, ReglaAutomatizacion, db
from services.flujo_generator_service import FlujoGeneratorService
from utils import login_required
import json

flujo_bp = Blueprint('flujo', __name__, url_prefix='/flujos')

@flujo_bp.route('/')
@login_required
def index():
    flujos = Flujo.query.all()
    return render_template('flujos/index.html', flujos=flujos)

@flujo_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        modo = request.form.get('modo', 'manual')
        
        if modo == 'auto':
            instruccion = request.form.get('instruccion')
            tipo_ticket = request.form['tipo_ticket']
            
            flujo = FlujoGeneratorService.generar_desde_texto(instruccion, tipo_ticket)
            flash(f'Flujo "{flujo.nombre}" generado automáticamente', 'success')
            return redirect(url_for('flujo.editar', id=flujo.id))
        else:
            flujo = Flujo(
                nombre=request.form['nombre'],
                tipo_ticket=request.form['tipo_ticket'],
                descripcion=request.form.get('descripcion')
            )
            db.session.add(flujo)
            db.session.commit()
            
            flash('Flujo creado', 'success')
            return redirect(url_for('flujo.editar', id=flujo.id))
    
    return render_template('flujos/form.html')

@flujo_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    flujo = Flujo.query.get_or_404(id)
    
    if request.method == 'POST':
        flujo.nombre = request.form['nombre']
        flujo.descripcion = request.form.get('descripcion')
        flujo.activo = request.form.get('activo') == 'true'
        
        db.session.commit()
        flash('Flujo actualizado', 'success')
    
    return render_template('flujos/editar.html', flujo=flujo)

@flujo_bp.route('/<int:id>/transicion', methods=['POST'])
@login_required
def agregar_transicion(id):
    transicion = Transicion(
        flujo_id=id,
        estado_origen=request.form['estado_origen'],
        estado_destino=request.form['estado_destino'],
        nombre=request.form['nombre'],
        requiere_comentario=request.form.get('requiere_comentario') == 'true',
        requiere_adjunto=request.form.get('requiere_adjunto') == 'true',
        roles_permitidos=request.form.get('roles_permitidos')
    )
    db.session.add(transicion)
    db.session.commit()
    
    return jsonify({'success': True, 'id': transicion.id})

@flujo_bp.route('/reglas')
@login_required
def reglas():
    reglas = ReglaAutomatizacion.query.all()
    return render_template('flujos/reglas.html', reglas=reglas)

@flujo_bp.route('/reglas/nueva', methods=['POST'])
@login_required
def nueva_regla():
    regla = ReglaAutomatizacion(
        nombre=request.form['nombre'],
        tipo_ticket=request.form.get('tipo_ticket'),
        condiciones=request.form['condiciones'],
        acciones=request.form['acciones']
    )
    db.session.add(regla)
    db.session.commit()
    
    flash('Regla creada', 'success')
    return redirect(url_for('flujo.reglas'))


@flujo_bp.route('/<int:id>/toggle', methods=['POST'])
@login_required
def toggle(id):
    flujo = Flujo.query.get_or_404(id)
    flujo.activo = not flujo.activo
    db.session.commit()
    
    return jsonify({'success': True, 'activo': flujo.activo})
