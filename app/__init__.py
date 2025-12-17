from flask import Flask
from flask_login import LoginManager
from app.blueprints import init_app as init_blueprints
from app.models import User
import secrets
from datetime import timedelta

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    print(f"User loader called for ID: {user_id}")
    user = User.get(user_id)
    print(f"Loaded user: {user}")
    return user

def create_app():
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(32)

    app.config.update(
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(days=1),
        SESSION_COOKIE_PATH='/',
        SESSION_COOKIE_DOMAIN='68.183.137.189',
    )

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    print("TEST: This should appear in the logs")

    init_blueprints(app)
    return app
