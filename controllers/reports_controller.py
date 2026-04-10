from flask import Blueprint, render_template, send_file, jsonify, flash, redirect, url_for
from services.report_service import ReportService
from services.pdf_service import PDFService
from models import Report
from utils.decorators import login_required, role_required
import os

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
@role_required('admin', 'coordinador')
def index():
    """Lista de reportes generados"""
    reportes = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('reports/index.html', reportes=reportes)

@reports_bp.route('/generate', methods=['POST'])
@login_required
@role_required('admin', 'coordinador')
def generate():
    """Genera un nuevo reporte semanal"""
    try:
        # Obtener datos de la semana ACTUAL (no anterior)
        fecha_inicio, fecha_fin = ReportService.get_semana_actual()
        
        # Generar datos del reporte
        datos = ReportService.generar_datos_semanales(fecha_inicio, fecha_fin)
        
        # Generar resumen ejecutivo
        resumen = ReportService.generar_resumen_ejecutivo(datos)
        
        # Generar PDF
        filename = PDFService.generar_pdf_semanal(datos, resumen)
        
        # Guardar registro en BD
        reporte = ReportService.guardar_reporte(datos, filename)
        
        flash(f'Reporte semanal generado exitosamente: {filename}', 'success')
        return redirect(url_for('reports.index'))
        
    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'danger')
        return redirect(url_for('reports.index'))

@reports_bp.route('/download/<int:id>')
@login_required
@role_required('admin', 'coordinador')
def download(id):
    """Descarga un reporte específico"""
    reporte = Report.query.get_or_404(id)
    filepath = os.path.join('static', 'reports', reporte.archivo_pdf)
    
    if not os.path.exists(filepath):
        flash('Archivo no encontrado', 'danger')
        return redirect(url_for('reports.index'))
    
    return send_file(filepath, as_attachment=True)

@reports_bp.route('/preview')
@login_required
@role_required('admin', 'coordinador')
def preview():
    """Vista previa de datos del reporte sin generar PDF"""
    fecha_inicio, fecha_fin = ReportService.get_semana_anterior()
    datos = ReportService.generar_datos_semanales(fecha_inicio, fecha_fin)
    resumen = ReportService.generar_resumen_ejecutivo(datos)
    
    return render_template('reports/preview.html', datos=datos, resumen=resumen)

@reports_bp.route('/api/stats')
@login_required
def api_stats():
    """API para obtener estadísticas rápidas"""
    fecha_inicio, fecha_fin = ReportService.get_semana_actual()
    datos = ReportService.generar_datos_semanales(fecha_inicio, fecha_fin)
    
    return jsonify({
        'total': datos['total'],
        'a_tiempo': datos['a_tiempo'],
        'fuera_fecha': datos['fuera_fecha'],
        'porcentaje': datos['porcentaje_cumplimiento']
    })
