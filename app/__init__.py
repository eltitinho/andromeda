from flask import Flask
from flask_login import LoginManager
from app.blueprints import init_app as init_blueprints
from app.models import User
import secrets

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

    login_manager.init_app(app)

    init_blueprints(app)
    return app
