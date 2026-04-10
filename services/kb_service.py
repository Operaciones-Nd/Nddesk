"""
Servicio de Base de Conocimientos
Encapsula toda la lógica de negocio de KB
"""
from models import ArticuloKB, VinculoTicketKB, db
from services.kb_search_service import KBSearchService

class KBService:
    
    @staticmethod
    def listar_articulos(categoria=None, busqueda=None, rol=None):
        """Lista artículos con filtros opcionales"""
        if busqueda:
            resultados = ArticuloKB.buscar_con_score(busqueda, rol)
            articulos = [r['articulo'] for r in resultados]
            for i, articulo in enumerate(articulos):
                articulo.snippet = resultados[i]['snippet']
                articulo.score = resultados[i]['score']
            return articulos
        
        if categoria:
            return ArticuloKB.por_categoria(categoria, rol)
        
        q = ArticuloKB.query.filter_by(estado='publicado', deleted_at=None)
        if rol and rol not in ['admin', 'coordinador']:
            q = q.filter((ArticuloKB.roles_permitidos.is_(None)) | (ArticuloKB.roles_permitidos.like(f'%{rol}%')))
        return q.order_by(ArticuloKB.vistas.desc()).all()
    
    @staticmethod
    def obtener_categorias():
        """Obtiene todas las categorías publicadas"""
        return db.session.query(ArticuloKB.categoria).filter_by(
            estado='publicado', 
            deleted_at=None
        ).distinct().all()
    
    @staticmethod
    def obtener_articulo(id):
        """Obtiene un artículo por ID"""
        return ArticuloKB.query.get_or_404(id)
    
    @staticmethod
    def incrementar_vistas(articulo):
        """Incrementa contador de vistas"""
        articulo.vistas += 1
        db.session.commit()
    
    @staticmethod
    def crear_articulo(titulo, contenido, categoria, tags, autor_id, estado='borrador', roles_permitidos=None):
        """Crea un nuevo artículo"""
        articulo = ArticuloKB(
            titulo=titulo,
            contenido=contenido,
            categoria=categoria,
            tags=tags,
            autor_id=autor_id,
            estado=estado,
            roles_permitidos=roles_permitidos
        )
        db.session.add(articulo)
        db.session.commit()
        return articulo
    
    @staticmethod
    def actualizar_articulo(articulo, titulo, contenido, categoria, tags, estado, roles_permitidos):
        """Actualiza un artículo existente"""
        articulo.titulo = titulo
        articulo.contenido = contenido
        articulo.categoria = categoria
        articulo.tags = tags
        articulo.estado = estado
        articulo.roles_permitidos = roles_permitidos
        articulo.version += 1
        db.session.commit()
        return articulo
    
    @staticmethod
    def marcar_utilidad(articulo, util):
        """Marca si un artículo fue útil o no"""
        if util:
            articulo.util_si += 1
        else:
            articulo.util_no += 1
        db.session.commit()
    
    @staticmethod
    def vincular_ticket(ticket_id, articulo_id, usuario_id):
        """Vincula un artículo con un ticket"""
        vinculo = VinculoTicketKB(
            ticket_id=ticket_id,
            articulo_id=articulo_id,
            usuario_id=usuario_id
        )
        db.session.add(vinculo)
        db.session.commit()
        return vinculo
    
    @staticmethod
    def puede_editar(articulo, usuario):
        """Verifica si un usuario puede editar el artículo"""
        return usuario.is_admin or usuario.is_coordinador or articulo.autor_id == usuario.id
