from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.units import inch
from xml.sax.saxutils import escape
from datetime import datetime


def generar_pdf_estadisticas(datos, ruta):

    documento = SimpleDocTemplate(
        ruta,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=35,
        bottomMargin=35
    )

    estilos = getSampleStyleSheet()

    verde = colors.HexColor("#234B4A")
    cafe = colors.HexColor("#8B5E3C")
    gris = colors.HexColor("#F2F2F2")
    blanco = colors.white
    texto = colors.HexColor("#333333")

    titulo = ParagraphStyle(
        "TituloBiblioteca",
        parent=estilos["Title"],
        alignment=TA_CENTER,
        textColor=verde,
        fontSize=18,
        leading=22,
        spaceAfter=6
    )

    subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=estilos["Normal"],
        alignment=TA_CENTER,
        textColor=texto,
        fontSize=11,
        leading=15,
        spaceAfter=5
    )

    encabezado_seccion = ParagraphStyle(
        "EncabezadoSeccion",
        parent=estilos["Heading2"],
        textColor=verde,
        fontSize=12,
        leading=15,
        spaceBefore=8,
        spaceAfter=7
    )

    estilo_resumen = ParagraphStyle(
        "Resumen",
        parent=estilos["Normal"],
        fontSize=9,
        leading=14,
        textColor=texto,
        alignment=0
    )

    elementos = []

    # ENCABEZADO
    elementos.append(Paragraph(
        "Sistema de Gestión Bibliotecaria - León",
        titulo
    ))

    elementos.append(Paragraph(
        "Reporte de estadísticas de préstamos",
        subtitulo
    ))

    elementos.append(Paragraph(
        f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        subtitulo
    ))

    elementos.append(Paragraph(
        "Período del reporte: últimos seis meses",
        subtitulo
    ))

    elementos.append(Spacer(1, 12))

    # RESUMEN DE PRÉSTAMOS
    elementos.append(Paragraph(
        "Resumen de préstamos",
        encabezado_seccion
    ))

    tabla_indicadores = [
        ["Indicador", "Cantidad"],
        ["Total de préstamos", datos["total"]],
        ["Préstamos activos", datos["activos"]],
        ["Préstamos vencidos", datos["vencidos"]],
        ["Libros devueltos", datos["devueltos"]]
    ]

    tabla = Table(
        tabla_indicadores,
        colWidths=[330, 150],
        hAlign="LEFT"
    )

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), verde),
        ("TEXTCOLOR", (0, 0), (-1, 0), blanco),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
        ("TEXTCOLOR", (0, 1), (-1, -1), texto),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [blanco, gris]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
    ]))

    elementos.append(tabla)
    elementos.append(Spacer(1, 12))

    # PRÉSTAMOS POR MES
    elementos.append(Paragraph(
        "Préstamos por mes",
        encabezado_seccion
    ))

    tabla_meses = [["Mes", "Cantidad"]]
    tabla_meses.extend(datos["meses"])

    tabla = Table(
        tabla_meses,
        colWidths=[330, 150],
        hAlign="LEFT"
    )

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), verde),
        ("TEXTCOLOR", (0, 0), (-1, 0), blanco),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
        ("TEXTCOLOR", (0, 1), (-1, -1), texto),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [blanco, gris]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
    ]))

    elementos.append(tabla)
    elementos.append(Spacer(1, 12))

    # LIBROS MÁS SOLICITADOS
    elementos.append(Paragraph(
        "Libros más solicitados",
        encabezado_seccion
    ))

    tabla_libros = [["Libro", "Cantidad"]]
    tabla_libros.extend(datos["libros"])

    tabla = Table(
        tabla_libros,
        colWidths=[330, 150],
        hAlign="LEFT"
    )

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), cafe),
        ("TEXTCOLOR", (0, 0), (-1, 0), blanco),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
        ("TEXTCOLOR", (0, 1), (-1, -1), texto),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [blanco, gris]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
    ]))

    elementos.append(tabla)
    elementos.append(Spacer(1, 14))

    # RESUMEN DEL PERÍODO
    elementos.append(Paragraph(
        "Resumen del período",
        encabezado_seccion
    ))

    if datos["libros"]:
        libro_mas_solicitado = datos["libros"][0][0]
        cantidad_libro = datos["libros"][0][1]

        texto_libro = (
            f"El libro más solicitado fue "
            f"<b>{escape(str(libro_mas_solicitado))}</b>, "
            f"con {cantidad_libro} préstamo(s)."
        )
    else:
        texto_libro = "No hay libros prestados registrados en el período."

    resumen = (
        f"Durante el período se registraron "
        f"<b>{datos['total']}</b> préstamos en total. "
        f"Actualmente hay <b>{datos['activos']}</b> préstamos activos "
        f"y <b>{datos['vencidos']}</b> préstamos vencidos. "
        f"{texto_libro}"
    )

    elementos.append(Paragraph(resumen, estilo_resumen))

    documento.build(elementos)

    return ruta