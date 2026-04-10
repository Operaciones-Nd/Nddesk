"""
Servicio de Búsqueda Inteligente para Base de Conocimientos
Implementa búsqueda híbrida con ranking, fuzzy matching y sinónimos
"""
import re
import unicodedata
from math import log
from fuzzywuzzy import fuzz
from models import ArticuloKB, db

class KBSearchService:
    
    # Diccionario de sinónimos
    SINONIMOS = {
        "login": ["iniciar sesion", "acceso", "entrar", "ingresar"],
        "contraseña": ["clave", "password", "pass", "credencial"],
        "ticket": ["solicitud", "requerimiento", "caso", "incidente"],
        "usuario": ["cuenta", "perfil", "user"],
        "crear": ["nuevo", "agregar", "añadir", "generar"],
        "editar": ["modificar", "cambiar", "actualizar"],
        "eliminar": ["borrar", "quitar", "remover"],
        "estado": ["status", "situacion", "condicion"],
        "prioridad": ["urgencia", "importancia"],
        "asignar": ["designar", "delegar"],
        "cerrar": ["finalizar", "completar", "terminar"],
        "reabrir": ["reactivar", "volver abrir"],
        "base datos": ["bd", "database", "db"],
        "tecnologia": ["tech", "stack", "herramientas"],
        "puerto": ["port"],
        "iniciar": ["arrancar", "correr", "ejecutar", "start", "run"],
        "rol": ["permiso", "acceso", "privilegio"],
        "admin": ["administrador", "administrator"],
        "coordinador": ["supervisor", "jefe"],
        "resolutor": ["tecnico", "soporte"],
        "solicitante": ["cliente", "usuario final"]
    }
    
    # Palabras vacías (stopwords)
    STOPWORDS = {
        "el", "la", "los", "las", "un", "una", "unos", "unas",
        "de", "del", "al", "a", "en", "por", "para", "con",
        "y", "o", "pero", "si", "no", "que", "como", "cuando",
        "donde", "cual", "cuales", "este", "esta", "estos", "estas"
    }
    
    @staticmethod
    def normalizar_texto(texto):
        """Normaliza texto: minúsculas, sin acentos, sin stopwords"""
        if not texto:
            return ""
        
        # Minúsculas
        texto = texto.lower()
        
        # Eliminar acentos
        texto = ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )
        
        # Tokenizar
        tokens = re.findall(r'\w+', texto)
        
        # Eliminar stopwords
        tokens = [t for t in tokens if t not in KBSearchService.STOPWORDS]
        
        return ' '.join(tokens)
    
    @staticmethod
    def expandir_sinonimos(query):
        """Expande query con sinónimos"""
        query_norm = KBSearchService.normalizar_texto(query)
        terminos = set(query_norm.split())
        
        # Agregar sinónimos
        for termino in list(terminos):
            if termino in KBSearchService.SINONIMOS:
                terminos.update(KBSearchService.SINONIMOS[termino])
        
        return list(terminos)
    
    @staticmethod
    def calcular_score(articulo, query, terminos_expandidos):
        """Calcula score de relevancia del artículo"""
        query_norm = KBSearchService.normalizar_texto(query)
        titulo_norm = KBSearchService.normalizar_texto(articulo.titulo)
        contenido_norm = KBSearchService.normalizar_texto(articulo.contenido)
        tags_norm = KBSearchService.normalizar_texto(articulo.tags or "")
        
        score = 0
        
        # 1. Match en título (peso 5)
        for termino in terminos_expandidos:
            if termino in titulo_norm:
                score += 5
        
        # 2. Match en tags (peso 3)
        for termino in terminos_expandidos:
            if termino in tags_norm:
                score += 3
        
        # 3. Match en contenido (peso 1)
        for termino in terminos_expandidos:
            if termino in contenido_norm:
                score += 1
        
        # 4. Fuzzy score en título (peso 2)
        fuzzy_titulo = fuzz.partial_ratio(query_norm, titulo_norm)
        if fuzzy_titulo > 60:
            score += (fuzzy_titulo / 100) * 2
        
        # 5. Utilidad (peso 2)
        total_votos = articulo.util_si + articulo.util_no
        if total_votos > 0:
            utilidad = (articulo.util_si / total_votos) * 2
            score += utilidad
        
        # 6. Popularidad (log de vistas)
        score += log(articulo.vistas + 1)
        
        return score
    
    @staticmethod
    def buscar(query, rol=None, limit=10):
        """Búsqueda inteligente con ranking"""
        if not query or not isinstance(query, str) or len(query.strip()) < 2:
            return []
        
        try:
            # Expandir con sinónimos
            terminos_expandidos = KBSearchService.expandir_sinonimos(query)
            
            # Query base
            q = ArticuloKB.query.filter_by(estado='publicado', deleted_at=None)
            
            # Filtrar por rol
            if rol and rol not in ['admin', 'coordinador']:
                q = q.filter(
                    (ArticuloKB.roles_permitidos.is_(None)) | 
                    (ArticuloKB.roles_permitidos.like(f'%{rol}%'))
                )
            
            articulos = q.all()
            
            # Calcular score para cada artículo
            resultados = []
            for articulo in articulos:
                score = KBSearchService.calcular_score(articulo, query, terminos_expandidos)
                if score > 0:
                    resultados.append({
                        'articulo': articulo,
                        'score': score,
                        'snippet': KBSearchService.generar_snippet(articulo, query)
                    })
            
            # Ordenar por score DESC
            resultados.sort(key=lambda x: x['score'], reverse=True)
            
            return resultados[:limit]
        except Exception as e:
            return []
    
    @staticmethod
    def generar_snippet(articulo, query, max_length=200):
        """Genera snippet del contenido con términos resaltados"""
        query_norm = KBSearchService.normalizar_texto(query)
        contenido = articulo.contenido
        
        # Buscar primera ocurrencia del término
        terminos = query_norm.split()
        mejor_pos = -1
        
        for termino in terminos:
            pos = contenido.lower().find(termino)
            if pos != -1:
                mejor_pos = pos
                break
        
        # Si no encuentra, tomar inicio
        if mejor_pos == -1:
            snippet = contenido[:max_length]
        else:
            # Tomar contexto alrededor del término
            inicio = max(0, mejor_pos - 50)
            fin = min(len(contenido), mejor_pos + max_length)
            snippet = contenido[inicio:fin]
            
            if inicio > 0:
                snippet = "..." + snippet
            if fin < len(contenido):
                snippet = snippet + "..."
        
        return snippet
    
    @staticmethod
    def autocompletar(query, limit=5):
        """Autocompletado de títulos, tags y categorías"""
        if not query or len(query) < 2:
            return []
        
        query_norm = KBSearchService.normalizar_texto(query)
        like_pattern = f'%{query_norm}%'
        
        sugerencias = []
        
        # Títulos
        titulos = db.session.query(ArticuloKB.titulo).filter(
            ArticuloKB.estado == 'publicado',
            ArticuloKB.deleted_at.is_(None),
            ArticuloKB.titulo.ilike(like_pattern)
        ).limit(limit).all()
        
        for titulo in titulos:
            sugerencias.append({
                'tipo': 'titulo',
                'texto': titulo[0]
            })
        
        # Categorías
        categorias = db.session.query(ArticuloKB.categoria).filter(
            ArticuloKB.estado == 'publicado',
            ArticuloKB.deleted_at.is_(None),
            ArticuloKB.categoria.ilike(like_pattern)
        ).distinct().limit(3).all()
        
        for cat in categorias:
            sugerencias.append({
                'tipo': 'categoria',
                'texto': cat[0]
            })
        
        return sugerencias[:limit]
    
    @staticmethod
    def articulos_relacionados(articulo_id, limit=3):
        """Encuentra artículos relacionados por categoría y tags"""
        articulo = ArticuloKB.query.get(articulo_id)
        if not articulo:
            return []
        
        # Buscar por misma categoría
        relacionados = ArticuloKB.query.filter(
            ArticuloKB.id != articulo_id,
            ArticuloKB.categoria == articulo.categoria,
            ArticuloKB.estado == 'publicado',
            ArticuloKB.deleted_at.is_(None)
        ).order_by(ArticuloKB.vistas.desc()).limit(limit).all()
        
        return relacionados
