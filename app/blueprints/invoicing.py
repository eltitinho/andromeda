from flask import request, render_template, redirect, url_for, Blueprint
from flask_login import current_user
from app.invoicing import generate_pdf
import time

invoicing_bp = Blueprint('invoicing', __name__)

@invoicing_bp.before_request
def before_invoicing_request():
    if not current_user.is_authenticated:
        return redirect(url_for('public.login', next=request.url))

@invoicing_bp.route('/', methods=['GET', 'POST'])
def invoicing_home():
    if request.method == 'POST':
        return generate_pdf(request)
    return render_template('invoicing/upload.html')  # Updated path
