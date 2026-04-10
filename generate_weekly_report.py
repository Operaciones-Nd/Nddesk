#!/usr/bin/env python3
"""
Script para generar automáticamente el informe semanal
Ejecutar cada lunes a las 7:00 AM con cron:
0 7 * * 1 /var/www/nddesk/venv/bin/python /var/www/nddesk/generate_weekly_report.py
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from services.report_service import ReportService
from services.pdf_service import PDFService
from services.email_service import EmailService

def main():
    app = create_app()
    
    with app.app_context():
        try:
            print("Generando informe semanal...")
            
            # Obtener datos de la semana anterior
            fecha_inicio, fecha_fin = ReportService.get_semana_anterior()
            print(f"Semana: {fecha_inicio} - {fecha_fin}")
            
            # Generar datos
            datos = ReportService.generar_datos_semanales(fecha_inicio, fecha_fin)
            print(f"Total solicitudes: {datos['total']}")
            
            # Generar resumen
            resumen = ReportService.generar_resumen_ejecutivo(datos)
            
            # Generar PDF
            filename = PDFService.generar_pdf_semanal(datos, resumen)
            print(f"PDF generado: {filename}")
            
            # Guardar en BD
            reporte = ReportService.guardar_reporte(datos, filename)
            print(f"Reporte guardado con ID: {reporte.id}")
            
            # Enviar por correo
            destinatarios = [
                'redaccion@nuestrodiario.com.gt',
                'coordinacion@nuestrodiario.com.gt'
            ]
            
            EmailService.enviar_reporte_semanal(
                destinatarios=destinatarios,
                archivo_pdf=os.path.join('static', 'reports', filename),
                datos=datos
            )
            print("Correo enviado exitosamente")
            
            print("✅ Informe semanal generado y enviado correctamente")
            
        except Exception as e:
            print(f"❌ Error al generar informe: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    main()
