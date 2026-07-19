from flask import request, render_template, redirect, url_for, Blueprint, send_file, session, flash
from flask_login import current_user
from app.quoting import generate_pdf
import os
import time

quoting_bp = Blueprint('quoting', __name__)

@quoting_bp.before_request
def before_quoting_request():
    if not current_user.is_authenticated:
        return redirect(url_for('public.login', next=request.url))

@quoting_bp.route('/', methods=['GET', 'POST'])
def quoting_home():
    if request.method == 'POST':
        return generate_pdf(request)
    return render_template('quoting/upload.html')  # Updated path

@quoting_bp.route('/result')
def quoting_result():
    # Get the PDF filename and tracking number from session
    pdf_filename = session.pop('pdf_filename', None)
    tracking_number = session.pop('tracking_number', None)
    
    if not pdf_filename:
        flash('No PDF file found. Please generate a quote first.', 'error')
        return redirect(url_for('quoting.quoting_home'))
    
    # The flash messages are already in the session from generate_pdf
    # Render the result page with download link and tracking info
    return render_template('quoting/result.html', pdf_filename=pdf_filename, tracking_number=tracking_number)

@quoting_bp.route('/download/<pdf_filename>')
def download_pdf(pdf_filename):
    # Serve the PDF file for download
    temp_dir = os.path.join(os.path.dirname(__file__), '../../temp_pdfs')
    pdf_path = os.path.join(temp_dir, pdf_filename)
    
    if not os.path.exists(pdf_path):
        flash('PDF file not found.', 'error')
        return redirect(url_for('quoting.quoting_home'))
    
    # Return the file for download
    return send_file(pdf_path, as_attachment=True, download_name='cotizacion.pdf', mimetype='application/pdf')
