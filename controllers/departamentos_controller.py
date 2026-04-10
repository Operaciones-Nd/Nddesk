from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Departamento
from utils.decorators import login_required, role_required

departamentos_bp = Blueprint('departamentos', __name__)

@departamentos_bp.route('/')
@login_required
@role_required('admin', 'coordinador')
def index():
    departamentos = Departamento.query.filter_by(deleted_at=None).all()
    return render_template('departamentos/index.html', departamentos=departamentos)

@departamentos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def nuevo():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion', '')
        email_notificacion = request.form.get('email_notificacion', '')
        
        dept = Departamento(nombre=nombre, descripcion=descripcion, email_notificacion=email_notificacion)
        db.session.add(dept)
        db.session.commit()
        
        flash('Departamento creado exitosamente', 'success')
        return redirect(url_for('departamentos.index'))
    
    return render_template('departamentos/nuevo.html')

@departamentos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def editar(id):
    dept = Departamento.query.get_or_404(id)
    
    if request.method == 'POST':
        dept.nombre = request.form['nombre']
        dept.descripcion = request.form.get('descripcion', '')
        dept.email_notificacion = request.form.get('email_notificacion', '')
        db.session.commit()
        
        flash('Departamento actualizado exitosamente', 'success')
        return redirect(url_for('departamentos.index'))
    
    return render_template('departamentos/editar.html', departamento=dept)

@departamentos_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def eliminar(id):
    dept = Departamento.query.get_or_404(id)
    dept.soft_delete()
    db.session.commit()
    
    flash('Departamento eliminado exitosamente', 'success')
    return redirect(url_for('departamentos.index'))
