from flask import request, render_template, send_file, session
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfWriter, PdfReader
import io
from PIL import Image
from datetime import datetime
import os

# Utility functions
def draw_long_string(c: canvas.Canvas, start_x: int, start_y: int, s: str, max_width: int):
    text = c.beginText(start_x, start_y)
    paragraphs = s.replace('\r', '').split('\n')
    for p in paragraphs:
        words = p.split(' ')
        line = words[0]
        length = c.stringWidth(line)
        for w in words[1:]:
            if length + c.stringWidth(f" {w}") > max_width:
                text.textLine(line)
                length = 0
                line = w
                length = c.stringWidth(w)
            line += f" {w}"
            length += c.stringWidth(f" {w}")
        text.textLine(line)
    c.drawText(text)

def image_resize(path: str, desiredWidth: int) -> tuple[int, int]:
    with Image.open(path) as image:
        width, height = image.size
        ratio = desiredWidth / width
        desiredHeight = height * ratio
        return desiredWidth, desiredHeight

def align_vertically(c: canvas.Canvas, l: list, width: int, y: int, margin: int = 0) -> list[int]:
    font = "Helvetica"
    size = 10
    c.setFont(font, size)
    xs = []
    for i, e in enumerate(l):
        string_width = c.stringWidth(e, font, size)
        x = (width-2*margin)*i/(len(l) - 1) + margin
        x -= string_width/2
        xs.append(x)
        c.drawString(x, y, e)
    return xs

def align_vertically_around(c: canvas.Canvas, l: list, y: int, center: int, separator: str = ""):
    if len(l) == 0:
        return
    font = "Helvetica"
    size = 10
    c.setFont(font, size)
    full_string = l[0]
    for e in l[1:]:
        full_string += f"{separator}{e}"
    c.drawCentredString(center, y, full_string)

def strings_to_column(c: canvas.Canvas, l: list, columns: list, y: int, font: str = "Helvetica", size: int = 10):
    c.setFont(font, size)
    for i, e in enumerate(l):
        c.drawString(columns[i], y, e)

# PDF generation function
def generate_pdf(request):
    empresa = request.form['empresa']
    cliente = request.form['cliente']
    email = request.form['email']
    localizacion_cliente = request.form['localizacion_cliente']
    fecha = request.form['fecha']
    date_obj = datetime.strptime(fecha, '%Y-%m-%d')
    fecha = date_obj.strftime('%d/%m/%Y')
    vigencia = request.form['vigencia']
    date_obj = datetime.strptime(vigencia, '%Y-%m-%d')
    vigencia = date_obj.strftime('%d/%m/%Y')
    comment_title = request.form['comment_title']
    notas = request.form.getlist('notas[]')
    localizacion_flete = f"{request.form['ciudad_flete']}, {request.form['estado_flete']} CP:{request.form['cp_flete']}, {request.form['pais_flete']}"
    localizacion_destino = f"{request.form['direccion_destino']} {request.form['ciudad_destino']},{request.form['estado_destino']} CP:{request.form['cp_destino']}, {request.form['pais_destino']}"
    general_comment = request.form['general_comment']
    moneda = request.form['moneda']
    articulos = request.form.getlist('articulos[]')
    precios = request.form.getlist('precios[]')
    ivas = set(request.form.getlist('ivas[]'))
    observaciones = request.form.getlist('observaciones[]')
    assurance = request.form['assurance']
    transit_time = request.form['transit_time']
    background_pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ressources/BFA_background.pdf'))

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    client_info = [empresa, cliente, email, localizacion_cliente]
    y_position = 584
    columns_abscisse = [42, 190, 342, 490]
    strings_to_column(c, client_info, columns_abscisse, y_position, font="Helvetica-Bold", size=8)
    c.setFont("Helvetica", 8)
    c.drawString(columns_abscisse[-1], y_position - 12, fecha)
    c.drawString(columns_abscisse[-1], y_position - 2*12, f"Vigencia: {vigencia}")

    y_position = height*5/8
    c.setFont("Helvetica-Bold",18)
    c.drawCentredString(width/4, y_position, comment_title)
    c.setFont("Helvetica", 10)
    y_position -= 20
    align_vertically_around(c, notas, y_position, width/4, " - ")
    x_position = width*5/8
    y_position = height*5/8 + 20
    c.drawString(x_position, y_position, localizacion_flete)
    y_position -= 20
    c.drawString(x_position, y_position, localizacion_destino)
    y_position -= 20
    draw_long_string(c, x_position, y_position, general_comment, width - x_position - 5)

    delta_y = 12
    y_position = height/2
    columns_abscisse = [width/12, width*3/12, width*9/12, width*10/12, width*11/12]
    line = ["Artículo", "Descripción", "Costo", "Moneda", "+IVA"]
    strings_to_column(c, line, columns_abscisse, y_position, font="Helvetica-Bold")
    y_position -= delta_y
    for i, (articulo, precio, observacion) in enumerate(zip(articulos, precios, observaciones), start=1):
        has_iva = f"{i}" in ivas
        line = [articulo, "", precio, moneda, ""]
        if observacion != "":
            line[1] = observacion
        if has_iva:
            line[4] = "Sí"
        else:
            line[4] = "No"
        y_position -= delta_y
        strings_to_column(c, line, columns_abscisse, y_position)
        if y_position < 50:
            c.showPage()
            y_position = height - 50

    y_position -= delta_y
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(columns_abscisse[2] - 10, y_position, "Total")
    total = sum([eval(i) for i in precios])
    total_line = ["", "", str(total), moneda]
    strings_to_column(c, total_line, columns_abscisse, y_position)
    if y_position < 50:
        c.showPage()
        y_position = height - 50

    footer_postition = 50
    delta_y = 10
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2, footer_postition, "No incluye despacho de Exportación/Importación/Impuestos/Gastos de almacenaje.")
    footer_postition -= delta_y
    c.drawCentredString(width/2, footer_postition, "La mercancía viaja por cuenta y riesgo de nuestros clientes en caso de no asegurar la carga.")
    footer_postition -= delta_y
    c.drawCentredString(width/2, footer_postition, f"Seguro de carga: {assurance}% valor de aduana.")
    footer_postition -= delta_y
    c.drawCentredString(width/2, footer_postition, f"Tiempo de tránsito {transit_time} días.")

    c.save()
    buffer.seek(0)

    output_buffer = io.BytesIO()
    background = PdfReader(background_pdf_path)
    new_pdf = PdfReader(buffer)
    writer = PdfWriter()
    page = background.pages[0]
    page.merge_page(new_pdf.pages[0])
    writer.add_page(page)
    for i in range(1, len(new_pdf.pages)):
        writer.add_page(new_pdf.pages[i])
    writer.write(output_buffer)
    output_buffer.seek(0)
    return send_file(output_buffer, as_attachment=True, download_name='information.pdf', mimetype='application/pdf')

