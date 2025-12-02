from flask import redirect, url_for, render_template, request, Blueprint, flash
from flask_login import login_user, logout_user, current_user
from app.models import User

public_bp = Blueprint('public', __name__)
private_bp = Blueprint('private', __name__)

@public_bp.route('/')
def home():
    print(f"Home route - User authenticated: {current_user.is_authenticated}")  # Debug
    return render_template('index.html')

@public_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get(1)  # Get the default admin user
        if user and user.username == username and user.check_password(password):
            print("passed check")
            print(f"User before login: {user}")  # Debug
            login_result = login_user(user)
            print(f"Login result: {login_result}")  # Debug
            print(f"User after login: {current_user}")  # Debug
            next_page = request.args.get('next', url_for('public.home'))
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@public_bp.route('/logout')
def logout():
    print(f"Logout - User before logout: {current_user}")  # Debug
    logout_user()
    print(f"Logout - User after logout: {current_user}")  # Debug
    return redirect(url_for('public.home'))

@private_bp.before_request
def before_private_request():
    print(f"Private route - User authenticated: {current_user.is_authenticated}")  # Debug
    if not current_user.is_authenticated:
        return redirect(url_for('public.login', next=request.url))

@private_bp.route('/dashboard')
def dashboard():
    return render_template('auth/dashboard.html')  # Updated path
