from models.base import BaseModel, db
from datetime import datetime

class ArticuloKB(BaseModel):
    __tablename__ = 'articulos_kb'
    
    titulo = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(500))
    autor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    estado = db.Column(db.String(20), default='borrador')
    vistas = db.Column(db.Integer, default=0)
    util_si = db.Column(db.Integer, default=0)
    util_no = db.Column(db.Integer, default=0)
    version = db.Column(db.Integer, default=1)
    roles_permitidos = db.Column(db.String(200))  # admin,coordinador,resolutor,solicitante
    
    autor = db.relationship('Usuario')
    
    @classmethod
    def buscar(cls, query, rol=None):
        """Búsqueda inteligente usando KBSearchService"""
        from services.kb_search_service import KBSearchService
        resultados = KBSearchService.buscar(query, rol)
        return [r['articulo'] for r in resultados]
    
    @classmethod
    def buscar_con_score(cls, query, rol=None):
        """Búsqueda con score y snippets"""
        from services.kb_search_service import KBSearchService
        return KBSearchService.buscar(query, rol)
    
    @classmethod
    def por_categoria(cls, categoria, rol=None):
        q = cls.query.filter_by(categoria=categoria, estado='publicado', deleted_at=None)
        if rol and rol not in ['admin', 'coordinador']:
            q = q.filter((cls.roles_permitidos.is_(None)) | (cls.roles_permitidos.like(f'%{rol}%')))
        return q.order_by(cls.vistas.desc()).all()
    
    @classmethod
    def articulos_relacionados(cls, articulo_id):
        """Artículos relacionados"""
        from services.kb_search_service import KBSearchService
        return KBSearchService.articulos_relacionados(articulo_id)

class VinculoTicketKB(BaseModel):
    __tablename__ = 'vinculos_ticket_kb'
    
    ticket_id = db.Column(db.Integer, db.ForeignKey('solicitudes.id'), nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulos_kb.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    ticket = db.relationship('Solicitud')
    articulo = db.relationship('ArticuloKB')
    usuario = db.relationship('Usuario')
