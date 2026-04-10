from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import TurnoSemanal, Usuario, db
from utils import login_required, role_required
from datetime import datetime

turnos_bp = Blueprint('turnos', __name__)

@turnos_bp.route('/')
@role_required('admin', 'coordinador')
def index():
    turnos = TurnoSemanal.query.order_by(TurnoSemanal.fecha_inicio.desc()).all()
    return render_template('turnos/index.html', turnos=turnos)

@turnos_bp.route('/nuevo', methods=['GET', 'POST'])
@role_required('admin', 'coordinador')
def nuevo():
    if request.method == 'POST':
        try:
            # Obtener analistas seleccionados (puede ser múltiple)
            analistas_ids = request.form.getlist('analistas_ids')
            
            if not analistas_ids:
                flash('Debes seleccionar al menos un analista', 'warning')
                resolutores = Usuario.get_by_rol('resolutor')
                return render_template('turnos/nuevo.html', resolutores=resolutores)
            
            turno = TurnoSemanal(
                seccion=request.form['seccion'],
                fecha_inicio=datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date(),
                fecha_fin=datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d').date(),
                creado_por=session['user_id']
            )
            
            # Agregar analistas
            for analista_id in analistas_ids:
                analista = Usuario.query.get(int(analista_id))
                if analista:
                    turno.analistas.append(analista)
            
            db.session.add(turno)
            db.session.commit()
            flash(f'Turno creado con {len(analistas_ids)} analista(s)', 'success')
            return redirect(url_for('turnos.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    resolutores = Usuario.get_by_rol('resolutor')
    return render_template('turnos/nuevo.html', resolutores=resolutores)

@turnos_bp.route('/<int:id>/inactivar', methods=['POST'])
@role_required('admin', 'coordinador')
def inactivar(id):
    turno = TurnoSemanal.query.get_or_404(id)
    turno.activo = False
    db.session.commit()
    flash('Turno inactivado correctamente', 'success')
    return '', 200

@turnos_bp.route('/<int:id>/activar', methods=['POST'])
@role_required('admin', 'coordinador')
def activar(id):
    turno = TurnoSemanal.query.get_or_404(id)
    turno.activo = True
    db.session.commit()
    flash('Turno activado correctamente', 'success')
    return '', 200
