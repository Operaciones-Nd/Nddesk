from datetime import datetime, timedelta
from models import db, Solicitud, Report
from sqlalchemy import func

class ReportService:
    
    @staticmethod
    def get_semana_actual():
        """Obtiene inicio y fin de la semana actual (lunes a domingo)"""
        hoy = datetime.now().date()
        inicio = hoy - timedelta(days=hoy.weekday())  # Lunes
        fin = inicio + timedelta(days=6)  # Domingo
        return inicio, fin
    
    @staticmethod
    def get_semana_anterior():
        """Obtiene inicio y fin de la semana anterior"""
        hoy = datetime.now().date()
        inicio = hoy - timedelta(days=hoy.weekday() + 7)
        fin = inicio + timedelta(days=6)
        return inicio, fin
    
    @staticmethod
    def calcular_cumplimiento(solicitud):
        """Determina el estado de publicación/venta del anuncio"""
        if solicitud.publicado and solicitud.vendido:
            return 'publicado_vendido'
        elif solicitud.publicado and not solicitud.vendido:
            return 'publicado_no_vendido'
        elif not solicitud.publicado:
            return 'no_publicado'
        return 'pendiente'
    
    @staticmethod
    def generar_datos_semanales(fecha_inicio, fecha_fin):
        """Genera los datos del informe semanal"""
        
        # Solicitudes de la semana
        solicitudes = Solicitud.query.filter(
            Solicitud.created_at >= fecha_inicio,
            Solicitud.created_at <= datetime.combine(fecha_fin, datetime.max.time()),
            Solicitud.deleted_at.is_(None)
        ).all()
        
        # Métricas generales
        total = len(solicitudes)
        publicado_vendido = 0
        publicado_no_vendido = 0
        no_publicado = 0
        pendientes = 0
        
        # Métricas por sección
        por_seccion = {}
        
        # Actividad por responsable
        por_responsable = {}
        
        # Casos no publicados
        casos_no_publicados = []
        
        for sol in solicitudes:
            estado = ReportService.calcular_cumplimiento(sol)
            
            if estado == 'publicado_vendido':
                publicado_vendido += 1
            elif estado == 'publicado_no_vendido':
                publicado_no_vendido += 1
            elif estado == 'no_publicado':
                no_publicado += 1
                casos_no_publicados.append(sol)
            else:
                pendientes += 1
            
            # Por sección
            if sol.seccion not in por_seccion:
                por_seccion[sol.seccion] = {'total': 0, 'publicado_vendido': 0, 'publicado_no_vendido': 0, 'no_publicado': 0}
            por_seccion[sol.seccion]['total'] += 1
            if estado == 'publicado_vendido':
                por_seccion[sol.seccion]['publicado_vendido'] += 1
            elif estado == 'publicado_no_vendido':
                por_seccion[sol.seccion]['publicado_no_vendido'] += 1
            elif estado == 'no_publicado':
                por_seccion[sol.seccion]['no_publicado'] += 1
            
            # Por responsable
            if sol.resolutor:
                nombre = sol.resolutor.nombre
                if nombre not in por_responsable:
                    por_responsable[nombre] = {'total': 0, 'publicado_vendido': 0, 'publicado_no_vendido': 0}
                por_responsable[nombre]['total'] += 1
                if estado == 'publicado_vendido':
                    por_responsable[nombre]['publicado_vendido'] += 1
                elif estado == 'publicado_no_vendido':
                    por_responsable[nombre]['publicado_no_vendido'] += 1
        
        publicados_total = publicado_vendido + publicado_no_vendido
        tasa_conversion = (publicado_vendido / publicados_total * 100) if publicados_total > 0 else 0
        tasa_publicacion = (publicados_total / total * 100) if total > 0 else 0
        
        return {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'total': total,
            'publicado_vendido': publicado_vendido,
            'publicado_no_vendido': publicado_no_vendido,
            'no_publicado': no_publicado,
            'pendientes': pendientes,
            'tasa_conversion': round(tasa_conversion, 1),
            'tasa_publicacion': round(tasa_publicacion, 1),
            'solicitudes': solicitudes,
            'por_seccion': por_seccion,
            'por_responsable': por_responsable,
            'casos_no_publicados': casos_no_publicados
        }
    
    @staticmethod
    def generar_resumen_ejecutivo(datos):
        """Genera el texto del resumen ejecutivo"""
        total = datos['total']
        publicado_vendido = datos['publicado_vendido']
        publicado_no_vendido = datos['publicado_no_vendido']
        no_publicado = datos['no_publicado']
        tasa_conversion = datos['tasa_conversion']
        tasa_publicacion = datos['tasa_publicacion']
        
        # Determinar tono del resumen
        if tasa_conversion >= 80:
            evaluacion = "excelente"
            comentario = "El equipo demuestra un desempeño sobresaliente en la publicación y venta de anuncios."
        elif tasa_conversion >= 60:
            evaluacion = "satisfactorio"
            comentario = "El rendimiento se mantiene en niveles aceptables con oportunidades de mejora en conversión."
        elif tasa_conversion >= 40:
            evaluacion = "regular"
            comentario = "Se requiere atención para mejorar la tasa de conversión de anuncios publicados a vendidos."
        else:
            evaluacion = "crítico"
            comentario = "Se identifican problemas significativos en la conversión de anuncios que requieren acción inmediata."
        
        publicados_total = publicado_vendido + publicado_no_vendido
        
        resumen = f"""Durante la semana del {datos['fecha_inicio'].strftime('%d/%m/%Y')} al {datos['fecha_fin'].strftime('%d/%m/%Y')}, 
se recibieron {total} solicitudes de anuncios de diferentes departamentos.

💰 PUBLICADO Y VENDIDO: {publicado_vendido} anuncios ({tasa_conversion}% de conversión)
📋 PUBLICADO NO VENDIDO: {publicado_no_vendido} anuncios
❌ NO PUBLICADO: {no_publicado} anuncios
⏳ PENDIENTES: {datos['pendientes']} anuncios

Tasa de publicación: {tasa_publicacion}%
Tasa de conversión (vendidos/publicados): {tasa_conversion}%

El nivel de desempeño se considera {evaluacion}. {comentario}

Las secciones con mayor volumen fueron: {', '.join(list(datos['por_seccion'].keys())[:3])}.
"""
        return resumen.strip()
    
    @staticmethod
    def guardar_reporte(datos, archivo_pdf):
        """Guarda el registro del reporte en la base de datos"""
        reporte = Report(
            tipo='semanal',
            semana_inicio=datos['fecha_inicio'],
            semana_fin=datos['fecha_fin'],
            archivo_pdf=archivo_pdf,
            total_solicitudes=datos['total'],
            cumplidas_tiempo=datos['publicado_vendido'],
            fuera_fecha=datos['no_publicado'],
            porcentaje_cumplimiento=datos['tasa_conversion'],
            generado_por='Sistema Automático'
        )
        db.session.add(reporte)
        db.session.commit()
        return reporte
