import os
import tempfile
import sqlite3
import pytest
from flask import Flask
from flask_login import LoginManager
from app.blueprints.auth import private_bp, public_bp, get_user_db_connection
from app.models import User

# Create a test Flask app
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    # Set up user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)
    
    # Register both blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(private_bp)
    
    # Use a temporary database for testing
    app.config['USER_DB_PATH'] = tempfile.mktemp(suffix='.db')
    
    yield app
    
    # Cleanup: Remove the temporary database
    if os.path.exists(app.config['USER_DB_PATH']):
        os.remove(app.config['USER_DB_PATH'])

@pytest.fixture
def client(app):
    return app.test_client()

def test_email_settings_route(app, client):
    """Test the email settings route and password encryption."""

    # Mock the get_user_db_connection function to use the test database
    def mock_get_user_db_connection():
        conn = sqlite3.connect(app.config['USER_DB_PATH'])
        conn.row_factory = sqlite3.Row
        return conn
    
    # Replace the function in the blueprint
    with app.app_context():
        import app.blueprints.auth as auth_module
        auth_module.get_user_db_connection = mock_get_user_db_connection
    
    # Test data
    test_email = 'test@example.com'
    test_password = 'securepassword123'
    
    # Log in the user first
    with client:
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin'  # Using default admin credentials from config
        }, follow_redirects=True)
        
        # Submit the email settings form
        response = client.post('/email_settings', data={
            'email_address': test_email,
            'email_password': test_password
        }, follow_redirects=True)
    
    # Check that the response is successful
    assert response.status_code == 200
    
    # Verify the database was created and contains the encrypted password
    conn = sqlite3.connect(app.config['USER_DB_PATH'])
    cursor = conn.cursor()
    
    # Check that the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='email_settings'")
    table_exists = cursor.fetchone() is not None
    assert table_exists, "email_settings table was not created"
    
    # Check that the email settings were stored
    cursor.execute("SELECT email_address, email_password_encrypted FROM email_settings")
    row = cursor.fetchone()
    
    assert row is not None, "No data was stored in the database"
    assert row['email_address'] == test_email, "Email address was not stored correctly"
    
    # Verify the password was encrypted (not hashed)
    from app.utils.encryption import decrypt_data
    stored_encrypted = row['email_password_encrypted']
    decrypted_password = decrypt_data(stored_encrypted)
    assert decrypted_password == test_password, "Password was not encrypted/decrypted correctly"
    
    conn.close()

def test_password_not_stored_in_plaintext(app, client):
    """Test that the password is not stored in plaintext."""

    # Mock the get_user_db_connection function to use the test database
    def mock_get_user_db_connection():
        conn = sqlite3.connect(app.config['USER_DB_PATH'])
        conn.row_factory = sqlite3.Row
        return conn
    
    # Replace the function in the blueprint
    with app.app_context():
        import app.blueprints.auth as auth_module
        auth_module.get_user_db_connection = mock_get_user_db_connection
    
    # Test data
    test_email = 'test@example.com'
    test_password = 'securepassword123'
    
    # Log in the user first
    with client:
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin'
        }, follow_redirects=True)
        
        # Submit the form
        client.post('/email_settings', data={
            'email_address': test_email,
            'email_password': test_password
        }, follow_redirects=True)
    
    # Verify the password is not stored in plaintext
    conn = sqlite3.connect(app.config['USER_DB_PATH'])
    cursor = conn.cursor()
    
    cursor.execute("SELECT email_password_encrypted FROM email_settings")
    row = cursor.fetchone()
    
    stored_encrypted = row['email_password_encrypted']
    
    # The stored encrypted data should not be the same as the plaintext password
    assert stored_encrypted != test_password, "Password was stored in plaintext!"
    
    # Verify it can be decrypted correctly
    from app.utils.encryption import decrypt_data
    decrypted_password = decrypt_data(stored_encrypted)
    assert decrypted_password == test_password, "Decrypted password doesn't match original"
    
    conn.close()

def test_smtp_settings_storage(app, client):
    """Test that SMTP settings are stored correctly."""

    # Mock the get_user_db_connection function to use the test database
    def mock_get_user_db_connection():
        conn = sqlite3.connect(app.config['USER_DB_PATH'])
        conn.row_factory = sqlite3.Row
        return conn
    
    # Replace the function in the blueprint
    with app.app_context():
        import app.blueprints.auth as auth_module
        auth_module.get_user_db_connection = mock_get_user_db_connection
    
    # Test data with SMTP settings
    test_email = 'test@example.com'
    test_password = 'securepassword123'
    
    # Log in the user first
    with client:
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin'
        }, follow_redirects=True)
        
        # Submit the form with SMTP settings
        client.post('/email_settings', data={
            'email_address': test_email,
            'email_password': test_password,
            'smtp_server': 'smtp.example.com',
            'smtp_port': 587,
            'smtp_use_tls': 'on',
            'smtp_use_ssl': 'off'
        }, follow_redirects=True)
    
    # Verify SMTP settings were stored
    conn = sqlite3.connect(app.config['USER_DB_PATH'])
    cursor = conn.cursor()
    
    cursor.execute("SELECT smtp_server, smtp_port, smtp_use_tls, smtp_use_ssl FROM email_settings")
    row = cursor.fetchone()
    
    assert row is not None, "No SMTP settings were stored"
    assert row['smtp_server'] == 'smtp.example.com', "SMTP server not stored correctly"
    assert row['smtp_port'] == 587, "SMTP port not stored correctly"
    assert row['smtp_use_tls'] == True, "SMTP TLS setting not stored correctly"
    assert row['smtp_use_ssl'] == False, "SMTP SSL setting not stored correctly"
    
    conn.close()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
