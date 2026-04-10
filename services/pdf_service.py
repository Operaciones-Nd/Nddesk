from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os
from datetime import datetime

class PDFService:
    
    # Paleta corporativa elegante
    AZUL_CORPORATIVO = colors.HexColor('#0f172a')
    AZUL_MEDIO = colors.HexColor('#1e40af')
    AZUL_CLARO = colors.HexColor('#3b82f6')
    VERDE_EXITO = colors.HexColor('#059669')
    AMARILLO_ALERTA = colors.HexColor('#d97706')
    ROJO_CRITICO = colors.HexColor('#dc2626')
    GRIS_OSCURO = colors.HexColor('#475569')
    GRIS_MEDIO = colors.HexColor('#94a3b8')
    GRIS_CLARO = colors.HexColor('#f1f5f9')
    
    @staticmethod
    def generar_pdf_semanal(datos, resumen_ejecutivo):
        """Genera PDF ejecutivo de nivel gerencial"""
        
        filename = f"informe_semanal_{datos['fecha_inicio'].strftime('%Y%m%d')}.pdf"
        filepath = os.path.join('static', 'reports', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter, 
                               topMargin=0.3*inch, leftMargin=0.5*inch, 
                               rightMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # === PORTADA EJECUTIVA ===
        # Franja superior corporativa
        header_table = Table([['']], colWidths=[7.5*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PDFService.AZUL_CORPORATIVO),
            ('TOPPADDING', (0, 0), (-1, -1), 50),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 50),
        ]))
        story.append(header_table)
        
        # Título en franja
        story.append(Spacer(1, -1.8*inch))
        title_style = ParagraphStyle(
            'ExecutiveTitle',
            parent=styles['Heading1'],
            fontSize=32,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=38
        )
        story.append(Paragraph("INFORME SEMANAL", title_style))
        
        subtitle_style = ParagraphStyle(
            'ExecutiveSubtitle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#cbd5e1'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        story.append(Paragraph("Gestión de Anuncios Publicitarios", subtitle_style))
        
        # Badge de fecha
        story.append(Spacer(1, 1.2*inch))
        fecha_badge = Table([[f"Semana del {datos['fecha_inicio'].strftime('%d/%m/%Y')} al {datos['fecha_fin'].strftime('%d/%m/%Y')}"]], 
                           colWidths=[4*inch])
        fecha_badge.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PDFService.AZUL_CLARO),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('ROUNDEDCORNERS', [5, 5, 5, 5]),
        ]))
        story.append(fecha_badge)
        
        story.append(Spacer(1, 0.5*inch))
        
        # === TARJETAS DE MÉTRICAS (Dashboard Style) ===
        metricas = [
            ('TOTAL SOLICITUDES', datos['total'], PDFService.AZUL_MEDIO, ''),
            ('PUBLICADO Y VENDIDO', datos['publicado_vendido'], PDFService.VERDE_EXITO, f"{datos['tasa_conversion']}% conversión"),
            ('PUBLICADO NO VENDIDO', datos['publicado_no_vendido'], PDFService.AMARILLO_ALERTA, ''),
            ('NO PUBLICADO', datos['no_publicado'], PDFService.ROJO_CRITICO, 'Requiere atención'),
        ]
        
        # Crear tarjetas en grid 2x2
        for i in range(0, len(metricas), 2):
            row_data = []
            for metrica in metricas[i:i+2]:
                label, valor, color, nota = metrica
                card_content = [
                    [Paragraph(f'<font size="10" color="#64748b">{label}</font>', styles['Normal'])],
                    [Paragraph(f'<font size="36" color="{color.hexval()}"><b>{valor}</b></font>', styles['Normal'])],
                    [Paragraph(f'<font size="8" color="#94a3b8">{nota}</font>', styles['Normal'])] if nota else ['']
                ]
                card_table = Table(card_content, colWidths=[3*inch])
                card_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 15),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ('BOX', (0, 0), (-1, -1), 1, PDFService.GRIS_CLARO),
                    ('LINEBELOW', (0, 1), (-1, 1), 3, color),
                ]))
                row_data.append(card_table)
            
            cards_row = Table([row_data], colWidths=[3.5*inch, 3.5*inch], spaceBefore=10, spaceAfter=10)
            cards_row.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(cards_row)
        
        story.append(Spacer(1, 0.4*inch))
        
        # === GRÁFICA LIMPIA ===
        if datos['total'] > 0:
            heading_style = ParagraphStyle(
                'SectionHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=PDFService.AZUL_CORPORATIVO,
                fontName='Helvetica-Bold',
                spaceBefore=10,
                spaceAfter=15,
                borderPadding=(0, 0, 5, 0),
                borderColor=PDFService.AZUL_CLARO,
                borderWidth=0,
                leftIndent=0
            )
            story.append(Paragraph("DISTRIBUCIÓN DE ANUNCIOS", heading_style))
            
            drawing = Drawing(500, 180)
            pie = Pie()
            pie.x = 50
            pie.y = 20
            pie.width = 140
            pie.height = 140
            pie.data = [datos['publicado_vendido'], datos['publicado_no_vendido'], 
                       datos['no_publicado'], datos['pendientes']]
            pie.labels = None  # Sin labels en el pastel
            pie.slices.strokeWidth = 0
            pie.slices[0].fillColor = PDFService.VERDE_EXITO
            pie.slices[1].fillColor = PDFService.AMARILLO_ALERTA
            pie.slices[2].fillColor = PDFService.ROJO_CRITICO
            pie.slices[3].fillColor = PDFService.GRIS_MEDIO
            
            # Leyenda lateral elegante
            legend_data = [
                [Rect(0, 0, 12, 12, fillColor=PDFService.VERDE_EXITO, strokeColor=None), 
                 f"  Publicado y Vendido: {datos['publicado_vendido']} ({datos['tasa_conversion']}%)"],
                [Rect(0, 0, 12, 12, fillColor=PDFService.AMARILLO_ALERTA, strokeColor=None), 
                 f"  Publicado No Vendido: {datos['publicado_no_vendido']}"],
                [Rect(0, 0, 12, 12, fillColor=PDFService.ROJO_CRITICO, strokeColor=None), 
                 f"  No Publicado: {datos['no_publicado']}"],
                [Rect(0, 0, 12, 12, fillColor=PDFService.GRIS_MEDIO, strokeColor=None), 
                 f"  Pendientes: {datos['pendientes']}"],
            ]
            
            for i, (rect, text) in enumerate(legend_data):
                drawing.add(rect)
                rect.x = 220
                rect.y = 130 - (i * 30)
                drawing.add(String(240, 132 - (i * 30), text, fontSize=10, fillColor=PDFService.GRIS_OSCURO))
            
            story.append(drawing)
            
            # Interpretación automática
            interp_style = ParagraphStyle(
                'Interpretation',
                parent=styles['Normal'],
                fontSize=9,
                textColor=PDFService.GRIS_OSCURO,
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName='Helvetica-Oblique'
            )
            if datos['tasa_conversion'] >= 70:
                interpretacion = f"Excelente desempeño: {datos['tasa_conversion']}% de los anuncios publicados fueron vendidos."
            elif datos['tasa_conversion'] >= 50:
                interpretacion = f"Desempeño satisfactorio con {datos['tasa_conversion']}% de conversión. Oportunidad de mejora."
            else:
                interpretacion = f"Atención requerida: Solo {datos['tasa_conversion']}% de conversión en anuncios publicados."
            story.append(Paragraph(interpretacion, interp_style))
        
        # === PÁGINA 2: RESUMEN EJECUTIVO ===
        story.append(PageBreak())
        
        story.append(Paragraph("RESUMEN EJECUTIVO", heading_style))
        
        # Bloques de texto con bullets
        exec_style = ParagraphStyle(
            'ExecutiveText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=PDFService.GRIS_OSCURO,
            leading=16,
            spaceAfter=10
        )
        
        lineas = resumen_ejecutivo.split('\n')
        for linea in lineas:
            if linea.strip():
                if linea.strip().startswith('💰') or linea.strip().startswith('📋') or linea.strip().startswith('❌'):
                    story.append(Paragraph(f"• {linea.strip()}", exec_style))
                else:
                    story.append(Paragraph(linea.strip(), exec_style))
        
        story.append(Spacer(1, 0.3*inch))
        
        # === TABLA POR SECCIÓN (Elegante) ===
        if datos['por_seccion']:
            story.append(Paragraph("DESEMPEÑO POR SECCIÓN", heading_style))
            
            seccion_data = [['Sección', 'Total', 'Vendido', 'No Vendido', 'No Pub.', '% Conv.']]
            for seccion, metricas in datos['por_seccion'].items():
                total_pub = metricas['publicado_vendido'] + metricas['publicado_no_vendido']
                conv = (metricas['publicado_vendido'] / total_pub * 100) if total_pub > 0 else 0
                
                # Color según conversión
                if conv >= 70:
                    conv_text = f'<font color="{PDFService.VERDE_EXITO.hexval()}"><b>{conv:.0f}%</b></font>'
                elif conv >= 50:
                    conv_text = f'<font color="{PDFService.AMARILLO_ALERTA.hexval()}"><b>{conv:.0f}%</b></font>'
                else:
                    conv_text = f'<font color="{PDFService.ROJO_CRITICO.hexval()}"><b>{conv:.0f}%</b></font>'
                
                seccion_data.append([
                    seccion,
                    str(metricas['total']),
                    str(metricas['publicado_vendido']),
                    str(metricas['publicado_no_vendido']),
                    str(metricas['no_publicado']),
                    Paragraph(conv_text, styles['Normal'])
                ])
            
            seccion_table = Table(seccion_data, colWidths=[1.8*inch, 0.7*inch, 0.8*inch, 1*inch, 0.8*inch, 0.7*inch])
            seccion_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), PDFService.AZUL_CORPORATIVO),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, PDFService.GRIS_CLARO),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, PDFService.GRIS_CLARO])
            ]))
            story.append(seccion_table)
        
        # === CASOS NO PUBLICADOS (Sobrio) ===
        if datos['casos_no_publicados']:
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("ANUNCIOS NO PUBLICADOS - SEGUIMIENTO PRIORITARIO", heading_style))
            
            no_pub_data = [['ID', 'Sección', 'Departamento', 'Motivo']]
            for sol in datos['casos_no_publicados'][:8]:
                no_pub_data.append([
                    f"#{sol.id}",
                    sol.seccion[:20],
                    sol.departamento[:20],
                    sol.motivo_no_publicado[:40] if sol.motivo_no_publicado else 'No especificado'
                ])
            
            no_pub_table = Table(no_pub_data, colWidths=[0.6*inch, 1.5*inch, 1.5*inch, 2.8*inch])
            no_pub_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), PDFService.ROJO_CRITICO),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, PDFService.GRIS_CLARO),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            story.append(no_pub_table)
            
            nota_style = ParagraphStyle(
                'Note',
                parent=styles['Normal'],
                fontSize=8,
                textColor=PDFService.GRIS_MEDIO,
                spaceAfter=10,
                fontName='Helvetica-Oblique'
            )
            story.append(Paragraph("Nota: Se recomienda seguimiento inmediato con los departamentos involucrados.", nota_style))
        
        # === CONCLUSIÓN EJECUTIVA ===
        story.append(Spacer(1, 0.4*inch))
        
        conclusion_box = Table([['']], colWidths=[7.5*inch])
        conclusion_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PDFService.AZUL_CLARO),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        story.append(conclusion_box)
        
        story.append(Spacer(1, -0.8*inch))
        conclusion_style = ParagraphStyle(
            'Conclusion',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=18
        )
        story.append(Paragraph(
            f"TASA DE CONVERSIÓN: {datos['tasa_conversion']}%<br/>TASA DE PUBLICACIÓN: {datos['tasa_publicacion']}%",
            conclusion_style
        ))
        
        # === FOOTER DISCRETO ===
        story.append(Spacer(1, 0.6*inch))
        separator = Table([['']], colWidths=[7.5*inch])
        separator.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 1, PDFService.GRIS_CLARO),
        ]))
        story.append(separator)
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=PDFService.GRIS_MEDIO,
            alignment=TA_CENTER,
            spaceAfter=5
        )
        story.append(Paragraph(
            f"Generado automáticamente por NDdesk | {datetime.now().strftime('%d de %B de %Y a las %H:%M hrs')}",
            footer_style
        ))
        story.append(Paragraph("Nuestro Diario © - Documento de uso interno", footer_style))
        
        doc.build(story)
        return filename
