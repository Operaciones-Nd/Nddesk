from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Subcategoria, Servicio, db
from utils import login_required, role_required

subcategorias_bp = Blueprint('subcategorias', __name__)

@subcategorias_bp.route('/')
@login_required
@role_required('admin', 'coordinador')
def index():
    subcategorias = Subcategoria.query.filter_by(deleted_at=None).all()
    return render_template('subcategorias/index.html', subcategorias=subcategorias)

@subcategorias_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def nuevo():
    if request.method == 'POST':
        subcat = Subcategoria(
            nombre=request.form['nombre'],
            servicio_id=request.form['servicio_id'],
            activo=True
        )
        db.session.add(subcat)
        db.session.commit()
        flash('Subcategoría creada', 'success')
        return redirect(url_for('subcategorias.index'))
    servicios = Servicio.query.filter_by(deleted_at=None, activo=True).all()
    return render_template('subcategorias/nuevo.html', servicios=servicios)

@subcategorias_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def editar(id):
    subcat = Subcategoria.query.get_or_404(id)
    if request.method == 'POST':
        subcat.nombre = request.form['nombre']
        subcat.servicio_id = request.form['servicio_id']
        subcat.activo = 'activo' in request.form
        db.session.commit()
        flash('Subcategoría actualizada', 'success')
        return redirect(url_for('subcategorias.index'))
    servicios = Servicio.query.filter_by(deleted_at=None, activo=True).all()
    return render_template('subcategorias/editar.html', subcat=subcat, servicios=servicios)

@subcategorias_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
@role_required('admin')
def eliminar(id):
    subcat = Subcategoria.query.get_or_404(id)
    subcat.soft_delete()
    db.session.commit()
    flash('Subcategoría eliminada', 'success')
    return redirect(url_for('subcategorias.index'))
