from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import Servicio, Subcategoria, db
from utils import login_required, role_required

servicios_bp = Blueprint('servicios', __name__)

@servicios_bp.route('/')
@login_required
@role_required('admin', 'coordinador')
def index():
    servicios = Servicio.query.filter_by(deleted_at=None).all()
    return render_template('servicios/index.html', servicios=servicios)

@servicios_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def nuevo():
    if request.method == 'POST':
        servicio = Servicio(
            nombre=request.form['nombre'],
            descripcion=request.form.get('descripcion'),
            activo=True
        )
        db.session.add(servicio)
        db.session.commit()
        flash('Servicio creado', 'success')
        return redirect(url_for('servicios.index'))
    return render_template('servicios/nuevo.html')

@servicios_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def editar(id):
    servicio = Servicio.query.get_or_404(id)
    if request.method == 'POST':
        servicio.nombre = request.form['nombre']
        servicio.descripcion = request.form.get('descripcion')
        servicio.activo = 'activo' in request.form
        db.session.commit()
        flash('Servicio actualizado', 'success')
        return redirect(url_for('servicios.index'))
    return render_template('servicios/editar.html', servicio=servicio)

@servicios_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
@role_required('admin')
def eliminar(id):
    servicio = Servicio.query.get_or_404(id)
    servicio.soft_delete()
    db.session.commit()
    flash('Servicio eliminado', 'success')
    return redirect(url_for('servicios.index'))

@servicios_bp.route('/<int:id>/subcategorias')
@login_required
def subcategorias(id):
    subcats = Subcategoria.query.filter_by(servicio_id=id, deleted_at=None, activo=True).all()
    return jsonify([{'id': s.id, 'nombre': s.nombre} for s in subcats])

@servicios_bp.route('/por-nombre/<nombre>')
@login_required
def por_nombre(nombre):
    servicio = Servicio.query.filter_by(nombre=nombre, deleted_at=None).first()
    if servicio:
        return jsonify({'id': servicio.id, 'nombre': servicio.nombre})
    return jsonify({'error': 'No encontrado'}), 404
