from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import Usuario, AuditoriaUsuario, db
from utils import login_required, role_required, get_client_ip

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/')
@login_required
@role_required('admin', 'coordinador')
def index():
    usuarios = Usuario.get_active().all()
    return render_template('usuarios/index.html', usuarios=usuarios)

@usuarios_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def nuevo():
    if request.method == 'POST':
        try:
            # Validar que el username no exista (incluyendo eliminados)
            username = request.form['username']
            usuario_existente = Usuario.query.filter_by(username=username).first()
            
            if usuario_existente:
                if usuario_existente.deleted_at:
                    # Reactivar usuario eliminado
                    usuario_existente.deleted_at = None
                    usuario_existente.nombre = request.form['nombre']
                    usuario_existente.rol = request.form['rol']
                    usuario_existente.departamento_id = request.form.get('departamento_id') or None
                    usuario_existente.activo = True
                    usuario_existente.requiere_cambio_password = True
                    usuario_existente.set_password(request.form['password'])
                    
                    # Actualizar secciones
                    usuario_existente.secciones.clear()
                    secciones_ids = request.form.getlist('secciones_ids')
                    if secciones_ids:
                        from models import Seccion
                        for seccion_id in secciones_ids:
                            seccion = Seccion.query.get(int(seccion_id))
                            if seccion:
                                usuario_existente.secciones.append(seccion)
                    
                    db.session.commit()
                    flash(f'Usuario "{username}" reactivado exitosamente', 'success')
                    return redirect(url_for('usuarios.index'))
                else:
                    flash(f'El usuario "{username}" ya existe', 'warning')
                    from models import Seccion, Departamento
                    secciones = Seccion.query.filter_by(deleted_at=None, activo=True).all()
                    departamentos = Departamento.query.filter_by(deleted_at=None, activo=True).all()
                    return render_template('usuarios/nuevo.html', secciones=secciones, departamentos=departamentos)
            
            user = Usuario(
                username=username,
                nombre=request.form['nombre'],
                rol=request.form['rol'],
                departamento_id=request.form.get('departamento_id') or None,
                activo=True,
                requiere_cambio_password=True
            )
            user.set_password(request.form['password'])
            
            db.session.add(user)
            db.session.flush()
            
            # Asignar múltiples secciones usando ORM
            secciones_ids = request.form.getlist('secciones_ids')
            if secciones_ids:
                from models import Seccion
                for seccion_id in secciones_ids:
                    seccion = Seccion.query.get(int(seccion_id))
                    if seccion:
                        user.secciones.append(seccion)
            
            auditoria = AuditoriaUsuario(
                admin_id=session['user_id'],
                usuario_afectado_id=user.id,
                accion='CREADO',
                detalle=f'Usuario {user.username} creado',
                ip_address=get_client_ip(request)
            )
            db.session.add(auditoria)
            
            db.session.commit()
            flash(f'Usuario {user.username} creado', 'success')
            return redirect(url_for('usuarios.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    from models import Seccion, Departamento
    secciones = Seccion.query.filter_by(deleted_at=None, activo=True).all()
    departamentos = Departamento.query.filter_by(deleted_at=None, activo=True).all()
    return render_template('usuarios/nuevo.html', secciones=secciones, departamentos=departamentos)

@usuarios_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def editar(id):
    usuario = Usuario.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            usuario.nombre = request.form['nombre']
            usuario.rol = request.form['rol']
            usuario.departamento_id = request.form.get('departamento_id') or None
            usuario.activo = 'activo' in request.form
            
            if request.form.get('password'):
                usuario.set_password(request.form['password'])
            
            # Actualizar secciones usando ORM
            usuario.secciones.clear()
            secciones_ids = request.form.getlist('secciones_ids')
            if secciones_ids:
                from models import Seccion
                for seccion_id in secciones_ids:
                    seccion = Seccion.query.get(int(seccion_id))
                    if seccion:
                        usuario.secciones.append(seccion)
            
            auditoria = AuditoriaUsuario(
                admin_id=session['user_id'],
                usuario_afectado_id=usuario.id,
                accion='EDITADO',
                detalle=f'Usuario {usuario.username} modificado',
                ip_address=get_client_ip(request)
            )
            db.session.add(auditoria)
            
            db.session.commit()
            flash('Usuario actualizado', 'success')
            return redirect(url_for('usuarios.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    from models import Seccion, Departamento
    secciones = Seccion.query.filter_by(deleted_at=None, activo=True).all()
    departamentos = Departamento.query.filter_by(deleted_at=None, activo=True).all()
    
    # Obtener secciones asignadas usando ORM
    secciones_ids = [s.id for s in usuario.secciones]
    
    return render_template('usuarios/editar.html', usuario=usuario, secciones=secciones, departamentos=departamentos, secciones_ids=secciones_ids)

@usuarios_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
@role_required('admin')
def eliminar(id):
    usuario = Usuario.query.get_or_404(id)
    usuario.soft_delete()
    db.session.commit()
    flash('Usuario eliminado', 'success')
    return redirect(url_for('usuarios.index'))

