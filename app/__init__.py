from flask import Flask
from flask_login import LoginManager
from app.blueprints import init_app as init_blueprints
from app.models import User
import secrets
from datetime import timedelta

# Initialize extensions that don't need immediate config
login_manager = LoginManager()
mail = None  # Flask-Mail will be initialized later when we have credentials

@login_manager.user_loader
def load_user(user_id):
    print(f"User loader called for ID: {user_id}")
    user = User.get(user_id)
    print(f"Loaded user: {user}")
    return user

def create_app():
    global mail
    
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(32)

    app.config.update(
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(days=1),
        SESSION_COOKIE_PATH='/',
        #SESSION_COOKIE_DOMAIN='68.183.137.189',
    )

    # Load basic configuration (but don't initialize Mail yet)
    app.config.from_object('config.Config')

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    # Don't initialize mail.init_app(app) here - we'll do it later

    print("TEST: This should appear in the logs")

    # Add function to initialize Mail when credentials are available
    def init_mail_with_credentials():
        """Initialize Flask-Mail with current database credentials"""
        global mail
        if mail is None:
            from flask_mail import Mail
            mail = Mail(app)
            print("Flask-Mail initialized with database credentials")
        return mail
    
    # Make the initialization function available
    app.init_mail = init_mail_with_credentials

    init_blueprints(app)
    return app
