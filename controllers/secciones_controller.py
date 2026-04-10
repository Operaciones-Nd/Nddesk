from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Seccion, SeccionResolutor, Usuario
from utils.decorators import login_required, role_required

secciones_bp = Blueprint('secciones', __name__)

@secciones_bp.route('/')
@login_required
@role_required('admin', 'coordinador')
def index():
    secciones = Seccion.query.filter_by(deleted_at=None).all()
    return render_template('secciones/index.html', secciones=secciones)

@secciones_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def nueva():
    if request.method == 'POST':
        nombre = request.form['nombre']
        medio = request.form['medio']
        descripcion = request.form.get('descripcion', '')
        email = request.form.get('email_notificacion', '')
        
        seccion = Seccion(nombre=nombre, medio=medio, descripcion=descripcion, email_notificacion=email)
        db.session.add(seccion)
        db.session.commit()
        
        flash('Sección creada exitosamente', 'success')
        return redirect(url_for('secciones.index'))
    
    return render_template('secciones/nueva.html')

@secciones_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def editar(id):
    seccion = Seccion.query.get_or_404(id)
    
    if request.method == 'POST':
        seccion.nombre = request.form['nombre']
        seccion.medio = request.form['medio']
        seccion.descripcion = request.form.get('descripcion', '')
        seccion.email_notificacion = request.form.get('email_notificacion', '')
        db.session.commit()
        
        flash('Sección actualizada exitosamente', 'success')
        return redirect(url_for('secciones.index'))
    
    return render_template('secciones/editar.html', seccion=seccion)

@secciones_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def eliminar(id):
    seccion = Seccion.query.get_or_404(id)
    seccion.soft_delete()
    db.session.commit()
    flash('Sección eliminada exitosamente', 'success')
    return redirect(url_for('secciones.index'))

@secciones_bp.route('/email/<string:nombre>')
@login_required
def get_email(nombre):
    from flask import jsonify
    seccion = Seccion.query.filter_by(nombre=nombre, deleted_at=None, activo=True).first()
    if seccion and seccion.email_notificacion:
        return jsonify({'email': seccion.email_notificacion})
    return jsonify({'email': 'digital.tickets@nuestrodiario.com.gt'})
