import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Default admin credentials
    DEFAULT_ADMIN_USERNAME = 'admin'
    DEFAULT_ADMIN_PW_HASH = 'scrypt:32768:8:1$SHoVPERfUE624erv$09d08910ea9dbedc344f1d8fed69b75ab0973011bc7271312ebc0e559b4a03bda2765a6c8e7c9701c80ececef52f7bb6c10feb67f96208ab0a6afded8500b2ea'
