from flask import request, render_template, redirect, url_for, Blueprint
from flask_login import current_user
from app.quoting import generate_pdf
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
