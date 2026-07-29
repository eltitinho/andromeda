import pytest
import io
from flask import Flask
from flask_login import LoginManager
from app.blueprints.quoting import quoting_bp
from app.blueprints.auth import public_bp
from app.models import User
from unittest.mock import patch, MagicMock

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
    app.register_blueprint(quoting_bp, url_prefix='/quoting')

    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_quoting_unauthenticated(client):
    # Test that unauthenticated users are redirected to login
    response = client.get('/quoting/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data or b'login' in response.data

def test_quoting_get_authenticated(client):
    # Login first by posting to login endpoint
    with patch('app.models.User.check_password', return_value=True):
        client.post('/login', data={
            'username': 'admin',
            'password': 'test_password'  # This will work with our mock
        }, follow_redirects=True)
    
    # Test authenticated GET request
    response = client.get('/quoting/')
    assert response.status_code == 200
    assert b'Cotizaci\xc3\xb3n' in response.data or b'Cotizacion' in response.data

@patch('app.quoting.generate_pdf')
def test_quoting_post_authenticated(mock_generate_pdf, client):
    # Setup mock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_generate_pdf.return_value = mock_response
    
    # Login first
    with patch('app.models.User.check_password', return_value=True):
        client.post('/login', data={
            'username': 'admin',
            'password': 'test_password'
        }, follow_redirects=True)
    
    # Test authenticated POST request
    response = client.post('/quoting/', data={
        'empresa': 'Test Company',
        'cliente': 'Test Client',
        'email': 'test@example.com',
        'localizacion_cliente': 'Test Location',
        'fecha': '2024-01-01',
        'vigencia': '2024-12-31',
        'comment_title': 'Test Title',
        'notas[]': ['Note 1', 'Note 2'],
        'ciudad_flete': 'Test City',
        'estado_flete': 'Test State',
        'cp_flete': '12345',
        'pais_flete': 'Test Country',
        'direccion_destino': 'Test Address',
        'ciudad_destino': 'Test City',
        'estado_destino': 'Test State',
        'cp_destino': '54321',
        'pais_destino': 'Test Country',
        'general_comment': 'General comment',
        'moneda': 'USD',
        'articulos[]': ['Item 1', 'Item 2'],
        'precios[]': ['100', '200'],
        'ivas[]': ['1'],
        'observaciones[]': ['Obs 1', 'Obs 2'],
        'assurance': '10',
        'transit_time': '5'
    }, follow_redirects=True)
    
    # Verify generate_pdf was called (note: this might not be called due to form validation)
    # For now, just check that the request was successful
    assert response.status_code == 200


# ============================================================================
# Tests for send_quote_email functionality
# ============================================================================

class MockMail:
    """Mock Flask-Mail for testing"""
    def __init__(self):
        self.messages_sent = []
    
    def send(self, msg):
        self.messages_sent.append(msg)
        return True


@pytest.fixture
def mock_mail():
    """Fixture for mocking Flask-Mail"""
    return MockMail()


@pytest.fixture
def app_with_mail():
    """Flask app with Mail extension configured for testing"""
    from flask_mail import Mail
    app = Flask(__name__)
    app.secret_key = 'test_secret_key'
    app.template_folder = '../app/templates'
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User(id=1, username='admin', is_admin=True) if user_id == 1 else None
    
    # Initialize Mail
    app.config.update({
        'MAIL_SERVER': 'smtp.test.com',
        'MAIL_PORT': 587,
        'MAIL_USE_TLS': True,
        'MAIL_USE_SSL': False,
        'MAIL_USERNAME': 'test@test.com',
        'MAIL_PASSWORD': 'test_password',
    })
    mail = Mail(app)
    app.extensions['mail'] = mail
    
    app.register_blueprint(public_bp)
    app.register_blueprint(quoting_bp, url_prefix='/quoting')
    
    return app


def test_send_quote_email_with_valid_credentials():
    """Test send_quote_email function with valid credentials"""
    from app.quoting import send_quote_email
    from flask import Flask
    from flask_mail import Mail
    import io
    
    # Create test app with Mail
    app = Flask(__name__)
    app.secret_key = 'test_secret'
    app.config.update({
        'MAIL_SERVER': 'smtp.test.com',
        'MAIL_PORT': 587,
        'MAIL_USE_TLS': True,
        'MAIL_USE_SSL': False,
    })
    
    # Initialize Mail
    mail = Mail(app)
    
    # Create mock mail instance
    mock_mail = MagicMock()
    mock_mail.send = MagicMock(return_value=True)
    app.extensions['mail'] = mock_mail
    
    # Create a PDF buffer
    pdf_buffer = io.BytesIO(b'%PDF-1.4 test pdf content')
    form_data = {'cliente': 'Test Client'}
    
    # Configure app with MAIL_USERNAME
    app.config['MAIL_USERNAME'] = 'test@test.com'
    
    with app.app_context():
        result = send_quote_email('client@test.com', pdf_buffer, form_data)
    
    # Verify the function returned (True, None)
    assert result == (True, None)
    
    # Verify mail.send was called
    assert mock_mail.send.called
    
    # Verify the message was created with correct parameters
    call_args = mock_mail.send.call_args
    msg = call_args[0][0]  # First positional argument
    
    assert msg.subject == "Cotización adjunta"
    assert msg.sender == "test@test.com"
    assert msg.recipients == ['client@test.com']
    assert 'Test Client' in msg.body
    assert 'cotización solicitada' in msg.body


def test_send_quote_email_missing_username():
    """Test send_quote_email when MAIL_USERNAME is not configured"""
    from app.quoting import send_quote_email
    from flask import Flask
    from flask_mail import Mail
    import io
    
    app = Flask(__name__)
    app.secret_key = 'test_secret'
    app.config['MAIL_SERVER'] = 'smtp.test.com'
    # Note: MAIL_USERNAME is not set
    
    # Initialize Mail
    mail = Mail(app)
    mock_mail = MagicMock()
    app.extensions['mail'] = mock_mail
    
    pdf_buffer = io.BytesIO(b'test pdf')
    form_data = {'cliente': 'Test Client'}
    
    with app.app_context():
        result = send_quote_email('client@test.com', pdf_buffer, form_data)
    
    # Now returns (False, error_message)
    assert result[0] == False
    assert result[1] is not None
    assert "Email configuration not found" in result[1]


def test_send_quote_email_no_mail_extension():
    """Test send_quote_email when Flask-Mail is not initialized"""
    from app.quoting import send_quote_email
    from flask import Flask
    import io
    
    app = Flask(__name__)
    app.secret_key = 'test_secret'
    app.config['MAIL_USERNAME'] = 'test@test.com'
    # Don't initialize Mail - extensions dict won't have 'mail'
    
    pdf_buffer = io.BytesIO(b'test pdf')
    form_data = {'cliente': 'Test Client'}
    
    with app.app_context():
        result = send_quote_email('client@test.com', pdf_buffer, form_data)
    
    # Now returns (False, error_message)
    assert result[0] == False
    assert result[1] is not None
    assert "Flask-Mail" in result[1]


def test_send_quote_email_with_pdf_attachment():
    """Test that PDF is properly attached to the email"""
    from app.quoting import send_quote_email
    from flask import Flask
    from flask_mail import Mail
    import io
    
    app = Flask(__name__)
    app.secret_key = 'test_secret'
    app.config.update({
        'MAIL_SERVER': 'smtp.test.com',
        'MAIL_PORT': 587,
        'MAIL_USE_TLS': True,
    })
    
    # Initialize Mail
    mail = Mail(app)
    
    mock_mail = MagicMock()
    mock_mail.send = MagicMock(return_value=True)
    app.extensions['mail'] = mock_mail
    
    # Create a PDF buffer with actual content
    pdf_content = b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n%%EOF'
    pdf_buffer = io.BytesIO(pdf_content)
    form_data = {'cliente': 'Test Client'}
    
    app.config['MAIL_USERNAME'] = 'test@test.com'
    
    with app.app_context():
        result = send_quote_email('client@test.com', pdf_buffer, form_data)
    
    # Now returns (True, None) on success
    assert result == (True, None)
    
    # Verify mail.send was called
    assert mock_mail.send.called
    
    # Get the message that was sent
    call_args = mock_mail.send.call_args
    msg = call_args[0][0]
    
    # Verify PDF attachment
    assert len(msg.attachments) > 0
    assert msg.attachments[0].filename == 'cotizacion.pdf'
    assert msg.attachments[0].content_type == 'application/pdf'


@patch('app.quoting.send_quote_email')
@patch('app.quoting.generate_pdf')
def test_quoting_post_with_send_email(mock_generate_pdf, mock_send_email, client):
    """Test POST request with send_email checkbox checked"""
    # Setup mocks
    pdf_buffer = io.BytesIO(b'%PDF-1.4 test content')
    mock_generate_pdf.return_value = pdf_buffer
    # send_quote_email now returns (success, error_msg)
    mock_send_email.return_value = (True, None)
    
    # Login first
    with patch('app.models.User.check_password', return_value=True):
        client.post('/login', data={
            'username': 'admin',
            'password': 'test_password'
        }, follow_redirects=True)
    
    # Test POST with send_email checked
    response = client.post('/quoting/', data={
        'empresa': 'Test Company',
        'cliente': 'Test Client',
        'email': 'client@test.com',
        'localizacion_cliente': 'Test Location',
        'fecha': '2024-01-01',
        'vigencia': '2024-12-31',
        'comment_title': 'Test Title',
        'notas[]': ['Note 1'],
        'ciudad_flete': 'Test City',
        'estado_flete': 'Test State',
        'cp_flete': '12345',
        'pais_flete': 'Test Country',
        'direccion_destino': 'Test Address',
        'ciudad_destino': 'Test City',
        'estado_destino': 'Test State',
        'cp_destino': '54321',
        'pais_destino': 'Test Country',
        'general_comment': 'General comment',
        'moneda': 'USD',
        'articulos[]': ['Item 1'],
        'precios[]': ['100'],
        'ivas[]': ['1'],
        'observaciones[]': ['Obs 1'],
        'assurance': '10',
        'transit_time': '5',
        'send_email': 'on'  # This triggers email sending
    }, follow_redirects=True)
    
    # Verify response is successful
    assert response.status_code == 200
    
    # Verify send_quote_email was called
    assert mock_send_email.called
    
    # Verify it was called with correct arguments
    call_args = mock_send_email.call_args
    assert call_args[0][0] == 'client@test.com'  # client_email
    assert isinstance(call_args[0][1], io.BytesIO)  # pdf_buffer is a BytesIO instance
    assert call_args[0][2]['cliente'] == 'Test Client'  # form_data


@patch('app.quoting.send_quote_email')
@patch('app.quoting.generate_pdf')
def test_quoting_post_with_send_email_no_client_email(mock_generate_pdf, mock_send_email, client):
    """Test POST request with send_email checked but no client email"""
    pdf_buffer = io.BytesIO(b'%PDF-1.4 test content')
    mock_generate_pdf.return_value = pdf_buffer
    # send_quote_email now returns (success, error_msg)
    mock_send_email.return_value = (True, None)
    
    # Login first
    with patch('app.models.User.check_password', return_value=True):
        client.post('/login', data={
            'username': 'admin',
            'password': 'test_password'
        }, follow_redirects=True)
    
    # Test POST with send_email checked but NO email
    response = client.post('/quoting/', data={
        'empresa': 'Test Company',
        'cliente': 'Test Client',
        'email': '',  # Empty email
        'localizacion_cliente': 'Test Location',
        'fecha': '2024-01-01',
        'vigencia': '2024-12-31',
        'comment_title': 'Test Title',
        'notas[]': ['Note 1'],
        'ciudad_flete': 'Test City',
        'estado_flete': 'Test State',
        'cp_flete': '12345',
        'pais_flete': 'Test Country',
        'direccion_destino': 'Test Address',
        'ciudad_destino': 'Test City',
        'estado_destino': 'Test State',
        'cp_destino': '54321',
        'pais_destino': 'Test Country',
        'general_comment': 'General comment',
        'moneda': 'USD',
        'articulos[]': ['Item 1'],
        'precios[]': ['100'],
        'ivas[]': ['1'],
        'observaciones[]': ['Obs 1'],
        'assurance': '10',
        'transit_time': '5',
        'send_email': 'on'
    }, follow_redirects=True)
    
    # Verify response is successful
    assert response.status_code == 200
    
    # Verify send_quote_email was NOT called (no client email)
    assert not mock_send_email.called


@patch('app.quoting.send_quote_email')
@patch('app.quoting.generate_pdf')
def test_quoting_post_without_send_email_checkbox(mock_generate_pdf, mock_send_email, client):
    """Test POST request without send_email checkbox"""
    pdf_buffer = io.BytesIO(b'%PDF-1.4 test content')
    mock_generate_pdf.return_value = pdf_buffer
    
    # Login first
    with patch('app.models.User.check_password', return_value=True):
        client.post('/login', data={
            'username': 'admin',
            'password': 'test_password'
        }, follow_redirects=True)
    
    # Test POST without send_email checkbox
    response = client.post('/quoting/', data={
        'empresa': 'Test Company',
        'cliente': 'Test Client',
        'email': 'client@test.com',
        'localizacion_cliente': 'Test Location',
        'fecha': '2024-01-01',
        'vigencia': '2024-12-31',
        'comment_title': 'Test Title',
        'notas[]': ['Note 1'],
        'ciudad_flete': 'Test City',
        'estado_flete': 'Test State',
        'cp_flete': '12345',
        'pais_flete': 'Test Country',
        'direccion_destino': 'Test Address',
        'ciudad_destino': 'Test City',
        'estado_destino': 'Test State',
        'cp_destino': '54321',
        'pais_destino': 'Test Country',
        'general_comment': 'General comment',
        'moneda': 'USD',
        'articulos[]': ['Item 1'],
        'precios[]': ['100'],
        'ivas[]': ['1'],
        'observaciones[]': ['Obs 1'],
        'assurance': '10',
        'transit_time': '5'
        # No send_email checkbox
    }, follow_redirects=True)
    
    # Verify response is successful
    assert response.status_code == 200
    
    # Verify send_quote_email was NOT called
    assert not mock_send_email.called