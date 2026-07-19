from flask import request, render_template, send_file, session, current_app, flash
from flask_mail import Message
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfWriter, PdfReader
from app.utils.encryption import decrypt_data
import io
from PIL import Image
from datetime import datetime
import os
import sqlite3
import uuid

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

# Tracking number generation function
def generate_and_store_tracking_number():
    """Generate a unique tracking number and store it in tracking.db with status 0 (created)"""
    tracking_number = f"TRACK{uuid.uuid4().hex[:8].upper()}"
    
    conn = sqlite3.connect('tracking.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tracking (tracking_number, status) VALUES (?, ?)', 
                   (tracking_number, 0))
    conn.commit()
    conn.close()
    
    return tracking_number

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
    
    # Check if email should be sent
    send_email = request.form.get('send_email')
    client_email = request.form.get('email')
    
    # Generate tracking number for this quote
    tracking_number = generate_and_store_tracking_number()
    
    if send_email and client_email:
        # Send email with PDF attachment to client
        output_buffer.seek(0)  # Rewind buffer for email attachment
        success, error_msg = send_quote_email(client_email, output_buffer, request.form, tracking_number)
        if success:
            print(f"Quote email sent successfully to {client_email}")
            flash(f'Email enviado a {client_email}!', 'success')
            output_buffer.seek(0)  # Rewind again for download
        else:
            print(f"Failed to send quote email to {client_email}: {error_msg}")
            flash(f'Error al enviar email a {client_email}: {error_msg}', 'error')
            output_buffer.seek(0)  # Rewind for download
    else:
        # Email not sent - either checkbox not checked or no client email
        if send_email:
            flash('Email no enviado: Favor de poner un correo electronico de destino.', 'warning')
        else:
            flash('Email no enviado: Envio de mail no seleccionado.', 'warning')
        # Continue with PDF download even if email fails
    
    # Store PDF in temp file and redirect to result page
    import tempfile
    import uuid
    from flask import session, redirect, url_for
    
    # Create temp directory if it doesn't exist
    temp_dir = os.path.join(os.path.dirname(__file__), '../temp_pdfs')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate unique filename
    pdf_filename = f"cotizacion_{uuid.uuid4().hex}.pdf"
    pdf_path = os.path.join(temp_dir, pdf_filename)
    
    # Save PDF to temp file
    output_buffer.seek(0)
    with open(pdf_path, 'wb') as f:
        f.write(output_buffer.read())
    
    # Store filename and tracking number in session for the result page
    session['pdf_filename'] = pdf_filename
    session['tracking_number'] = tracking_number
    
    # Redirect to result page
    return redirect(url_for('quoting.quoting_result'))
    
def get_email_credentials():
    """Retrieve email credentials and SMTP settings from user database"""
    try:
        conn = sqlite3.connect('user.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_address TEXT NOT NULL,
                email_password_encrypted TEXT NOT NULL,
                smtp_server TEXT NOT NULL,
                smtp_port INTEGER NOT NULL,
                smtp_use_tls BOOLEAN NOT NULL,
                smtp_use_ssl BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("Email settings table ensured to exist")
        
        cursor.execute('''
            SELECT email_address, email_password_encrypted, 
                   smtp_server, smtp_port, smtp_use_tls, smtp_use_ssl
            FROM email_settings ORDER BY id DESC LIMIT 1
        ''')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            try:
                # Decrypt the password for use with SMTP
                email_password = decrypt_data(result['email_password_encrypted'])
                if email_password is None:
                    error_msg = "Failed to decrypt email password. The encryption key may have changed. Please re-enter your email credentials."
                    print(error_msg)
                    flash(error_msg, 'error')
                    return None
                print(f"Found email credentials in database: {result['email_address']}")
                print(f"SMTP Server: {result['smtp_server']}:{result['smtp_port']}")
                return {
                    'email_address': result['email_address'],
                    'email_password': email_password,
                    'smtp_server': result['smtp_server'],
                    'smtp_port': result['smtp_port'],
                    'smtp_use_tls': bool(result['smtp_use_tls']),
                    'smtp_use_ssl': bool(result['smtp_use_ssl'])
                }
            except Exception as e:
                error_msg = f"Failed to decrypt email password: {str(e)}. The encryption key may have changed. Please re-enter your email credentials."
                print(error_msg)
                flash(error_msg, 'error')
                return None
        else:
            print("No email credentials found in database (table exists but empty)")
            return None
            
    except Exception as e:
        error_msg = f"Error retrieving email credentials: {str(e)}"
        print(error_msg)
        flash(error_msg, 'error')
        return None

def update_mail_config():
    """Update Flask-Mail configuration with database credentials"""
    from flask import current_app
    
    credentials = get_email_credentials()
    if not credentials:
        print("No email credentials found")
        return False

    # Update Flask config with database credentials
    current_app.config.update({
        'MAIL_SERVER': credentials['smtp_server'],
        'MAIL_PORT': credentials['smtp_port'],
        'MAIL_USE_TLS': credentials['smtp_use_tls'],
        'MAIL_USE_SSL': credentials['smtp_use_ssl'],
        'MAIL_USERNAME': credentials['email_address'],
        'MAIL_PASSWORD': credentials['email_password']
    })

    # Initialize Mail if not already done
    if hasattr(current_app, 'init_mail'):
        mail_instance = current_app.init_mail()
        print(f"Flask-Mail initialized: {mail_instance}")
        return True
    else:
        print("init_mail function not available")
        return False

def send_email_with_current_config():
    """Send email using the current database credentials"""
    from flask import current_app
    from flask_mail import Message
    
    # Ensure Mail is properly initialized with current credentials
    if not update_mail_config():
        print("Cannot send email - no valid credentials")
        return False
    
    try:
        # Get the Mail instance
        mail = current_app.extensions.get('mail')
        if not mail:
            print("Flask-Mail not initialized")
            return False
        
        credentials = get_email_credentials()
        if not credentials:
            return False
        
        with current_app.app_context():
            msg = Message("Test Email from Andromeda",
                         sender=credentials['email_address'],
                         recipients=["kris_generic@tuta.com"])
            msg.body = "This is a test email sent with proper Flask-Mail configuration"
            mail.send(msg)
            print("Email sent successfully!")
            return True
            
    except Exception as e:
        print(f"Failed to send email: {e}")
        import traceback
        traceback.print_exc()
        return False


def send_quote_email(client_email, pdf_buffer, form_data, tracking_number=None):
    """Send quote email with PDF attachment to client
    
    Args:
        client_email: Recipient email address
        pdf_buffer: PDF file buffer to attach
        form_data: Form data containing client information
        tracking_number: Optional tracking number to include in email
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    from flask import current_app
    from flask_mail import Message
    
    # Ensure Mail is properly initialized with current credentials
    if not update_mail_config():
        error_msg = "Cannot send email - no valid credentials found in database. Please configure your email settings first."
        print(error_msg)
        return False, error_msg
    
    try:
        # Get the Mail instance
        mail = current_app.extensions.get('mail')
        if not mail:
            error_msg = "Flask-Mail extension not initialized. Email cannot be sent."
            print(error_msg)
            return False, error_msg
        
        credentials = get_email_credentials()
        if not credentials:
            error_msg = "No email credentials found. Please configure your email settings."
            print(error_msg)
            return False, error_msg
        
        # Get client name from form data
        cliente = form_data.get('cliente', 'Cliente')
        
        # Build tracking URL if tracking number is provided
        tracking_url = None
        if tracking_number:
            tracking_url = f"http://68.183.137.189/public_tracking/view?tracking_number={tracking_number}"
        
        with current_app.app_context():
            msg = Message(
                subject="Cotización adjunta",
                sender=credentials['email_address'],
                recipients=[client_email]
            )
            
            # Spanish email body
            if tracking_url:
                msg.body = f"""Estimado/a {cliente},

Adjunto encontrará la cotización solicitada.

Puede rastrear el estado de su cotización usando el siguiente enlace:
{tracking_url}

Por favor revise el documento y, si todo está correcto, responda a este correo para confirmar.

Gracias"""
            else:
                msg.body = f"""Estimado/a {cliente},

Adjunto encontrará la cotización solicitada.

Por favor revise el documento y, si todo está correcto, responda a este correo para confirmar.

Gracias"""
            
            # Attach PDF
            pdf_buffer.seek(0)
            msg.attach(
                filename='cotizacion.pdf',
                content_type='application/pdf',
                data=pdf_buffer.read()
            )
            pdf_buffer.seek(0)  # Rewind for potential reuse
            
            mail.send(msg)
            print(f"Quote email sent successfully to {client_email}")
            return True, None
            
    except Exception as e:
        error_msg = f"Failed to send quote email to {client_email}: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return False, error_msg
