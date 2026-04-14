from flask import redirect, url_for, render_template, request, Blueprint, flash
from flask_login import login_user, logout_user, current_user
from app.models import User
from app.utils.encryption import encrypt_data, decrypt_data
import sqlite3
import gc
import json
from flask import current_app

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

@private_bp.route('/configuration')
def configuration():
    return render_template('auth/configuration.html')

def get_user_db_connection():
    """Get connection to user settings database"""
    conn = sqlite3.connect('user.db')
    conn.row_factory = sqlite3.Row
    return conn

@private_bp.route('/email_settings', methods=['GET', 'POST'])
def email_settings():
    
    if request.method == 'POST':
        email_address = request.form['email_address']
        email_password = request.form['email_password']
        
        # Get SMTP settings from form (with smart defaults)
        smtp_server = request.form.get('smtp_server', f'smtp.{email_address.split("@")[-1]}')
        smtp_port = int(request.form.get('smtp_port', 587))
        smtp_use_tls = request.form.get('smtp_use_tls', 'on') == 'on'
        smtp_use_ssl = request.form.get('smtp_use_ssl', 'off') == 'on'
        
        # Encrypt the email password (we need the original for SMTP authentication)
        email_password_encrypted = encrypt_data(email_password)
        
        # Clear the password from memory by overwriting it
        email_password = '*' * len(email_password)
        
        # Force garbage collection to clear memory
        gc.collect()
        
        # Store in database
        conn = get_user_db_connection()
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
        
        # Clear any existing settings and add new ones
        cursor.execute('DELETE FROM email_settings')
        cursor.execute('''
            INSERT INTO email_settings 
            (email_address, email_password_encrypted, smtp_server, smtp_port, smtp_use_tls, smtp_use_ssl)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (email_address, email_password_encrypted, smtp_server, smtp_port, smtp_use_tls, smtp_use_ssl))
        
        conn.commit()
        conn.close()
        
        if hasattr(current_app, 'init_mail'):
            mail_instance = current_app.init_mail()
            print(f"Flask-Mail reinitialized with new credentials: {mail_instance}")
        
        print(f"Email settings saved successfully: {email_address}")
        return render_template('auth/email_settings.html', success=True)
    
    # For GET request, show empty form for now
    return render_template('auth/email_settings.html')
