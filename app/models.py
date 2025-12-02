from flask_login import UserMixin
from werkzeug.security import check_password_hash
from config import Config

class User(UserMixin):
    def __init__(self, id, username, password_hash=None, is_admin=False):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get(user_id):
        user = User(
            id=user_id,
            username=Config.DEFAULT_ADMIN_USERNAME,
            password_hash=Config.DEFAULT_ADMIN_PW_HASH,
            is_admin=True
        )
        return user