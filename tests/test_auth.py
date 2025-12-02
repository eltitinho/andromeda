import pytest
from flask import Flask, template_rendered
from flask_login import LoginManager
from app.blueprints.auth import public_bp, private_bp
from app.models import User

@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = 'test_secret_key'
    app.template_folder = '../app/templates'
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User(id=1, username='admin', is_admin=True) if user_id == 1 else None

    app.register_blueprint(public_bp)
    app.register_blueprint(private_bp, url_prefix='/private')

    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_login_with_good_credentials(client):
    # Send a POST request to /login with good credentials
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'password'
    }, follow_redirects=True)

    # Check if the response is successful
    assert response.status_code == 200

    # Verify we're on the home page after login
    assert b'Bienvenido' in response.data

    # Verify the user is logged in by checking for a logout link or similar
    assert 'Gestión de Rastreo'.encode('utf-8') in response.data

def test_login_with_bad_credentials(client):
    # Send a POST request to /login with bad credentials
    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpassword'
    }, follow_redirects=True)

    # Check if the response is successful
    assert response.status_code == 200

    # Verify we're still on the login page
    assert 'Iniciar Sesión'.encode('utf-8') in response.data

    # Verify error message is displayed
    assert b'Invalid username or password' in response.data
