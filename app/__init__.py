from flask import Flask
from flask_login import LoginManager
from app.blueprints import init_app as init_blueprints
from app.models import User
import secrets

def create_app():
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(32)
    init_blueprints(app)
    return app
