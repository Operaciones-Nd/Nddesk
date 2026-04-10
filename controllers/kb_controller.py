from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import Usuario
from services.kb_service import KBService
from services.kb_search_service import KBSearchService
from utils import login_required

kb_bp = Blueprint('kb', __name__, url_prefix='/kb')

@kb_bp.route('/')
def index():
    try:
        categoria = request.args.get('categoria')
        busqueda = request.args.get('q')
        
        rol = None
        if session.get('user_id'):
            user = Usuario.query.get(session['user_id'])
            rol = user.rol
        
        articulos = KBService.listar_articulos(categoria, busqueda, rol)
        categorias = KBService.obtener_categorias()
        
        return render_template('kb/index.html', articulos=articulos, categorias=categorias, busqueda=busqueda)
    except Exception as e:
        flash('Error al cargar artículos', 'danger')
        return render_template('kb/index.html', articulos=[], categorias=[])

@kb_bp.route('/autocomplete')
def autocomplete():
    """Autocompletado para búsqueda"""
    q = request.args.get('q', '')
    sugerencias = KBSearchService.autocompletar(q)
    return jsonify(sugerencias)

@kb_bp.route('/<int:id>')
def ver(id):
    import markdown
    from models import ArticuloKB
    from flask import current_app
    
    try:
        articulo = KBService.obtener_articulo(id)
        KBService.incrementar_vistas(articulo)
        relacionados = ArticuloKB.articulos_relacionados(id)
        articulo.contenido_html = markdown.markdown(articulo.contenido)
        return render_template('kb/ver.html', articulo=articulo, relacionados=relacionados)
    except Exception as e:
        current_app.logger.error(f'Error en KB ver ID {id}: {str(e)}')
        import traceback
        current_app.logger.error(traceback.format_exc())
        flash('Artículo no encontrado', 'danger')
        return redirect(url_for('kb.index'))

@kb_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    try:
        user = Usuario.query.get(session['user_id'])
        
        if not (user.is_admin or user.is_coordinador):
            flash('Sin permisos', 'danger')
            return redirect(url_for('kb.index'))
        
        if request.method == 'POST':
            articulo = KBService.crear_articulo(
                titulo=request.form['titulo'],
                contenido=request.form['contenido'],
                categoria=request.form['categoria'],
                tags=request.form.get('tags', ''),
                autor_id=user.id,
                estado=request.form.get('estado', 'borrador'),
                roles_permitidos=request.form.get('roles_permitidos')
            )
            flash('Artículo creado', 'success')
            return redirect(url_for('kb.ver', id=articulo.id))
        
        return render_template('kb/form.html')
    except Exception as e:
        flash('Error al crear artículo', 'danger')
        return redirect(url_for('kb.index'))

@kb_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    try:
        articulo = KBService.obtener_articulo(id)
        user = Usuario.query.get(session['user_id'])
        
        if not KBService.puede_editar(articulo, user):
            flash('Sin permisos', 'danger')
            return redirect(url_for('kb.ver', id=id))
        
        if request.method == 'POST':
            KBService.actualizar_articulo(
                articulo,
                titulo=request.form['titulo'],
                contenido=request.form['contenido'],
                categoria=request.form['categoria'],
                tags=request.form.get('tags', ''),
                estado=request.form.get('estado', articulo.estado),
                roles_permitidos=request.form.get('roles_permitidos')
            )
            flash('Artículo actualizado', 'success')
            return redirect(url_for('kb.ver', id=id))
        
        return render_template('kb/form.html', articulo=articulo)
    except Exception as e:
        flash('Error al editar artículo', 'danger')
        return redirect(url_for('kb.index'))

@kb_bp.route('/<int:id>/util', methods=['POST'])
def marcar_util(id):
    try:
        articulo = KBService.obtener_articulo(id)
        util = request.json.get('util', True)
        KBService.marcar_utilidad(articulo, util)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@kb_bp.route('/vincular', methods=['POST'])
@login_required
def vincular():
    try:
        ticket_id = request.form.get('ticket_id')
        articulo_id = request.form.get('articulo_id')
        KBService.vincular_ticket(ticket_id, articulo_id, session['user_id'])
        flash('Artículo vinculado', 'success')
        return redirect(url_for('solicitudes.ver', id=ticket_id))
    except Exception as e:
        flash('Error al vincular artículo', 'danger')
        return redirect(url_for('solicitudes.ver', id=ticket_id))

@kb_bp.route('/buscar')
def buscar():
    try:
        q = request.args.get('q', '')
        articulos = KBService.listar_articulos(busqueda=q)
        return jsonify([{
            'id': a.id,
            'titulo': a.titulo,
            'categoria': a.categoria,
            'vistas': a.vistas
        } for a in articulos[:10]])
    except Exception as e:
        return jsonify({'error': str(e)}), 400
