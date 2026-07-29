import os
import json
import requests
from flask import current_app

# Configuration file path
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '../../app_config.json')

def load_config():
    """Load Mailgun configuration from JSON file"""
    if not os.path.exists(CONFIG_FILE):
        return {'mailgun_subdomain': 'noreply'}
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {'mailgun_subdomain': 'noreply'}

def save_config(config):
    """Save Mailgun configuration to JSON file"""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False

def get_mailgun_domain():
    """Construct full Mailgun domain from configuration"""
    config = load_config()
    subdomain = config.get('mailgun_subdomain', 'noreply')
    base_domain = current_app.config.get('MAILGUN_BASE_DOMAIN', 'bforwarder.mbarque.space')
    return f"{subdomain}.{base_domain}"

def get_from_address(name=None):
    """Construct from address for Mailgun"""
    domain = get_mailgun_domain()
    if name:
        return f"{name} <postmaster@{domain}>"
    return f"Andromeda <postmaster@{domain}>"

def send_mailgun_email(to, subject, text, from_name=None, attachments=None):
    """
    Send email via Mailgun HTTP API
    
    Args:
        to: Recipient email(s) - string or list
        subject: Email subject string
        text: Plain text body
        from_name: Sender name (optional)
        attachments: List of (filename, content) tuples
        
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    # Get API key from environment
    api_key = current_app.config.get('MAILGUN_API_KEY')
    if not api_key:
        return False, "MAILGUN_API_KEY environment variable not set"
    
    # Construct API URL
    domain = get_mailgun_domain()
    api_url = f"https://api.eu.mailgun.net/v3/{domain}/messages"
    
    # Construct from address
    from_addr = get_from_address(from_name)
    
    # Prepare request data
    data = {
        'from': from_addr,
        'to': to,
        'subject': subject,
        'text': text
    }
    
    # Prepare attachments
    files = []
    if attachments:
        for filename, content in attachments:
            if isinstance(content, str):
                content = content.encode('utf-8')
            files.append(('attachment', (filename, content)))
    
    # Send request
    try:
        response = requests.post(
            api_url,
            auth=('api', api_key),
            data=data,
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, None
        else:
            error_detail = response.text
            try:
                error_detail = response.json().get('message', response.text)
            except:
                pass
            return False, f"Mailgun API error {response.status_code}: {error_detail}"
            
    except requests.exceptions.Timeout:
        return False, "Mailgun API request timed out after 30 seconds"
    except requests.exceptions.RequestException as e:
        return False, f"Mailgun API request failed: {str(e)}"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"
