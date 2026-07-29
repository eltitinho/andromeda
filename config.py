import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Default admin credentials
    DEFAULT_ADMIN_USERNAME = 'admin'
    DEFAULT_ADMIN_PW_HASH = 'scrypt:32768:8:1$SHoVPERfUE624erv$09d08910ea9dbedc344f1d8fed69b75ab0973011bc7271312ebc0e559b4a03bda2765a6c8e7c9701c80ececef52f7bb6c10feb67f96208ab0a6afded8500b2ea'
    
    # Email server configuration (SMTP settings) - from environment variables
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ('true', '1', 't', 'y', 'yes')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ('true', '1', 't', 'y', 'yes')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Mailgun API Configuration (primary email method)
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    MAILGUN_BASE_DOMAIN = os.environ.get('MAILGUN_BASE_DOMAIN', 'bforwarder.mbarque.space')


