from flask import Flask
from app.blueprints import init_app

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key_here'
    init_app(app)
    return app
