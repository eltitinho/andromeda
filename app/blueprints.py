from flask import Blueprint, session, redirect, url_for, render_template, request, send_file
from flask_login import login_user, logout_user, current_user
from app.invoicing import generate_pdf
from app.tracking import tracking_management, tracking_view
from app.models import User
from urllib.parse import urlparse, urljoin

# Public Blueprint
public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def home():
    return render_template('index.html')

@public_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            user = User(id=1, username='admin', is_admin=True)
            login_user(user)
            next_page = request.args.get('next', url_for('public.home'))
            return redirect(next_page)
    return render_template('login.html')

@public_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('public.home'))

# Private Blueprint
private_bp = Blueprint('private', __name__)

@private_bp.before_request
def before_private_request():
    if not current_user.is_authenticated:
        return redirect(url_for('public.login', next=request.url))

@private_bp.route('/dashboard')
def dashboard():
    return "Private Dashboard"

# Invoicing Blueprint
invoicing_bp = Blueprint('invoicing', __name__)

@invoicing_bp.before_request
def before_invoicing_request():
    if not current_user.is_authenticated:
        return redirect(url_for('public.login', next=request.url))

@invoicing_bp.route('/', methods=['GET', 'POST'])
def invoicing_home():
    if request.method == 'POST':
        return generate_pdf(request)
    return render_template('upload.html')

# Tracking Blueprint
tracking_bp = Blueprint('tracking', __name__)

@tracking_bp.before_request
def before_tracking_request():
    if not current_user.is_authenticated:
        return redirect(url_for('public.login', next=request.url))

@tracking_bp.route('/tracking_view', methods=['GET', 'POST'])
def tracking_view_route():
    return tracking_view()

@tracking_bp.route('/tracking_management')
def tracking_management_route():
    return tracking_management()

def init_app(app):
    app.register_blueprint(public_bp)
    app.register_blueprint(private_bp, url_prefix='/private')
    app.register_blueprint(invoicing_bp, url_prefix='/invoicing')
    app.register_blueprint(tracking_bp, url_prefix='/tracking')
