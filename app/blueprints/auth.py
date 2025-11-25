from flask import redirect, url_for, render_template, request, Blueprint
from flask_login import login_user, logout_user, current_user
from app.models import User

public_bp = Blueprint('public', __name__)
private_bp = Blueprint('private', __name__)

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

@private_bp.before_request
def before_private_request():
    if not current_user.is_authenticated:
        return redirect(url_for('public.login', next=request.url))

@private_bp.route('/dashboard')
def dashboard():
    return render_template('auth/dashboard.html')  # Updated path
