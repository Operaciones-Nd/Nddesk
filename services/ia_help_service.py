"""
Servicio de Agente IA de Ayuda
Solo responde preguntas, explica pasos y guía al usuario
NO ejecuta acciones del sistema
"""
from services.kb_search_service import KBSearchService
from flask import session

class IAHelpService:
    
    # Intenciones soportadas
    INTENTS = {
        "como_hacer": ["como", "cómo", "pasos", "hacer", "puedo", "debo", "tutorial", "guia"],
        "problema": ["error", "no funciona", "problema", "falla", "ayuda", "no puedo"],
        "buscar_info": ["buscar", "informacion", "información", "articulo", "artículo", "documentacion"],
        "ayuda_general": ["ayuda", "soporte", "asistencia", "necesito"],
        "que_es": ["que es", "qué es", "significa", "definicion", "definición"]
    }
    
    # Temas principales
    TEMAS = {
        "contraseña": ["contraseña", "clave", "password", "pass", "credencial"],
        "ticket": ["ticket", "solicitud", "requerimiento", "caso", "incidente"],
        "login": ["login", "iniciar sesion", "acceso", "entrar", "ingresar"],
        "usuario": ["usuario", "cuenta", "perfil", "user"],
        "estado": ["estado", "status", "situacion"],
        "prioridad": ["prioridad", "urgencia", "importancia"],
        "rol": ["rol", "permiso", "acceso", "privilegio"],
        "crear": ["crear", "nuevo", "agregar"],
        "editar": ["editar", "modificar", "cambiar"],
        "cerrar": ["cerrar", "finalizar", "completar"],
        "asignar": ["asignar", "designar"],
        "base_datos": ["base datos", "bd", "database"],
        "tecnologia": ["tecnologia", "stack", "herramientas"],
        "iniciar_app": ["iniciar", "arrancar", "ejecutar", "correr"],
        "reportes": ["reporte", "reportes", "informe", "estadistica", "estadisticas", "metricas", "dashboard"]
    }
    
    @staticmethod
    def detectar_intencion(pregunta):
        """Detecta la intención del usuario"""
        pregunta_lower = pregunta.lower()
        
        for intencion, keywords in IAHelpService.INTENTS.items():
            for keyword in keywords:
                if keyword in pregunta_lower:
                    return intencion
        
        return "ayuda_general"
    
    @staticmethod
    def detectar_tema(pregunta):
        """Detecta el tema principal de la pregunta"""
        pregunta_lower = pregunta.lower()
        
        for tema, keywords in IAHelpService.TEMAS.items():
            for keyword in keywords:
                if keyword in pregunta_lower:
                    return tema
        
        return None
    
    @staticmethod
    def responder(pregunta, rol=None):
        """Genera respuesta conversacional basada en KB"""
        
        # Validar entrada
        if not pregunta or not isinstance(pregunta, str):
            return {
                'respuesta': 'Por favor escribe una pregunta válida.',
                'tipo': 'error'
            }
        
        if len(pregunta) > 500:
            return {
                'respuesta': 'Tu pregunta es muy larga. Por favor hazla más breve.',
                'tipo': 'error'
            }
        
        # Detectar intención y tema
        intencion = IAHelpService.detectar_intencion(pregunta)
        tema = IAHelpService.detectar_tema(pregunta)
        
        # Buscar en KB
        resultados = KBSearchService.buscar(pregunta, rol, limit=3)
        
        # Verificar si pregunta por reportes
        if tema == "reportes":
            return IAHelpService._respuesta_reportes()
        
        # Generar respuesta según intención
        if intencion == "como_hacer":
            return IAHelpService._respuesta_como_hacer(pregunta, tema, resultados)
        elif intencion == "problema":
            return IAHelpService._respuesta_problema(pregunta, tema, resultados)
        elif intencion == "buscar_info":
            return IAHelpService._respuesta_buscar_info(pregunta, resultados)
        elif intencion == "que_es":
            return IAHelpService._respuesta_que_es(pregunta, tema, resultados)
        else:
            return IAHelpService._respuesta_general(pregunta, resultados)
    
    @staticmethod
    def _respuesta_reportes():
        """Respuesta específica para reportes"""
        respuesta = "📊 **Generar Reportes**\n\n"
        respuesta += "Para acceder a los reportes del sistema:\n\n"
        respuesta += "1️⃣ Ve al menú superior\n"
        respuesta += "2️⃣ Haz clic en **Reportes**\n"
        respuesta += "3️⃣ Selecciona el tipo de reporte que necesitas\n\n"
        respuesta += "**Reportes disponibles**:\n"
        respuesta += "• 📈 Tickets por estado\n"
        respuesta += "• 👥 Tickets por técnico\n"
        respuesta += "• 📅 Tickets por fecha\n"
        respuesta += "• ⏱️ Tiempos de respuesta\n\n"
        respuesta += "[🔗 Ir a Reportes](/solicitudes/reportes)\n\n"
        respuesta += "¿Necesitas ayuda con algún reporte específico?"
        return {
            "respuesta": respuesta,
            "tipo": "reportes",
            "accion": "/solicitudes/reportes"
        }


    @staticmethod
    def _respuesta_como_hacer(pregunta, tema, resultados):
        """Respuesta para 'cómo hacer algo'"""
        if not resultados:
            return IAHelpService._respuesta_sin_resultados(pregunta, tema)
        
        articulo = resultados[0]['articulo']
        snippet = resultados[0]['snippet']
        
        # Extraer pasos si existen
        pasos = IAHelpService._extraer_pasos(articulo.contenido)
        
        respuesta = f"Para {tema or 'esto'}, te recomiendo revisar esta guía:\n\n"
        
        # Si hay pasos válidos, mostrarlos
        if pasos and len(pasos) >= 3:
            for i, paso in enumerate(pasos[:5], 1):
                respuesta += f"{i}️⃣ {paso}\n"
        else:
            # Si no hay suficientes pasos, mostrar snippet
            respuesta += f"{snippet}\n"
        
        respuesta += f"\n📘 **Artículo relacionado**: [{articulo.titulo}](/kb/{articulo.id})\n"
        
        # Artículos adicionales
        if len(resultados) > 1:
            respuesta += "\n**También puedes consultar**:\n"
            for r in resultados[1:3]:
                respuesta += f"• [{r['articulo'].titulo}](/kb/{r['articulo'].id})\n"
        
        respuesta += "\n¿Necesitas más ayuda con esto?"
        
        return {
            'respuesta': respuesta,
            'articulo_principal': articulo.id,
            'articulos_relacionados': [r['articulo'].id for r in resultados[1:3]]
        }
    
    @staticmethod
    def _respuesta_problema(pregunta, tema, resultados):
        """Respuesta para problemas/errores"""
        if not resultados:
            return IAHelpService._respuesta_sin_resultados(pregunta, tema)
        
        articulo = resultados[0]['articulo']
        
        respuesta = f"Entiendo que tienes un problema con {tema or 'el sistema'}. Aquí te ayudo:\n\n"
        respuesta += f"**Solución sugerida**:\n{resultados[0]['snippet']}\n\n"
        respuesta += f"📘 **Guía completa**: [{articulo.titulo}](/kb/{articulo.id})\n\n"
        
        respuesta += "**Pasos para resolver**:\n"
        respuesta += "1️⃣ Verifica que estés usando las credenciales correctas\n"
        respuesta += "2️⃣ Revisa la guía completa en el artículo\n"
        respuesta += "3️⃣ Si persiste, contacta al soporte\n\n"
        
        respuesta += "¿Esto resolvió tu problema?"
        
        return {
            'respuesta': respuesta,
            'articulo_principal': articulo.id,
            'tipo': 'problema'
        }
    
    @staticmethod
    def _respuesta_buscar_info(pregunta, resultados):
        """Respuesta para búsqueda de información"""
        if not resultados:
            return {
                'respuesta': "No encontré artículos sobre ese tema. ¿Puedes ser más específico?",
                'sugerencias': IAHelpService._sugerir_temas()
            }
        
        respuesta = f"Encontré {len(resultados)} artículo(s) sobre tu búsqueda:\n\n"
        
        for i, r in enumerate(resultados, 1):
            articulo = r['articulo']
            respuesta += f"{i}. **[{articulo.titulo}](/kb/{articulo.id})**\n"
            respuesta += f"   {r['snippet'][:100]}...\n"
            respuesta += f"   👁️ {articulo.vistas} vistas | 👍 {articulo.util_si} útil\n\n"
        
        respuesta += "Haz clic en cualquier artículo para ver más detalles."
        
        return {
            'respuesta': respuesta,
            'articulos': [r['articulo'].id for r in resultados]
        }
    
    @staticmethod
    def _respuesta_que_es(pregunta, tema, resultados):
        """Respuesta para definiciones"""
        if not resultados:
            return IAHelpService._respuesta_sin_resultados(pregunta, tema)
        
        articulo = resultados[0]['articulo']
        snippet = resultados[0]['snippet']
        
        respuesta = f"**{articulo.titulo}**\n\n"
        respuesta += f"{snippet}\n\n"
        respuesta += f"📘 **Leer más**: [{articulo.titulo}](/kb/{articulo.id})\n\n"
        respuesta += "¿Quieres saber más sobre este tema?"
        
        return {
            'respuesta': respuesta,
            'articulo_principal': articulo.id
        }
    
    @staticmethod
    def _respuesta_general(pregunta, resultados):
        """Respuesta general"""
        if not resultados:
            return IAHelpService._respuesta_sin_resultados(pregunta, None)
        
        articulo = resultados[0]['articulo']
        
        respuesta = f"Encontré información que puede ayudarte:\n\n"
        respuesta += f"**{articulo.titulo}**\n"
        respuesta += f"{resultados[0]['snippet']}\n\n"
        respuesta += f"📘 **Ver artículo completo**: [Aquí](/kb/{articulo.id})\n\n"
        respuesta += "¿Esto responde tu pregunta?"
        
        return {
            'respuesta': respuesta,
            'articulo_principal': articulo.id
        }
    
    @staticmethod
    def _respuesta_sin_resultados(pregunta, tema):
        """Respuesta cuando no hay resultados"""
        respuesta = f"No encontré información específica sobre '{pregunta}'.\n\n"
        respuesta += "**Puedo ayudarte con**:\n"
        respuesta += "• Cómo cambiar tu contraseña\n"
        respuesta += "• Cómo crear un ticket\n"
        respuesta += "• Cómo iniciar sesión\n"
        respuesta += "• Qué significan los estados de tickets\n"
        respuesta += "• Información sobre roles y permisos\n\n"
        respuesta += "¿Sobre cuál de estos temas necesitas ayuda?"
        
        return {
            'respuesta': respuesta,
            'sugerencias': IAHelpService._sugerir_temas()
        }
    
    @staticmethod
    def _extraer_pasos(contenido):
        """Extrae pasos numerados del contenido"""
        import re
        
        # Buscar líneas que empiecen con números (con o sin espacios)
        patron = r'^\s*(\d+)[.):\-]\s*(.+)$'
        pasos = []
        
        for linea in contenido.split('\n'):
            linea_limpia = linea.strip()
            match = re.match(patron, linea_limpia)
            if match:
                paso_texto = match.group(2).strip()
                # Limpiar markdown
                paso_texto = re.sub(r'\*\*(.+?)\*\*', r'\1', paso_texto)
                paso_texto = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', paso_texto)
                if len(paso_texto) > 10:  # Solo pasos con contenido significativo
                    pasos.append(paso_texto)
        
        return pasos[:5]  # Máximo 5 pasos
    
    @staticmethod
    def _sugerir_temas():
        """Sugiere temas populares"""
        return [
            "Cambiar contraseña",
            "Crear ticket",
            "Iniciar sesión",
            "Estados de tickets",
            "Roles y permisos"
        ]
