from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, is_admin=False):
        self.id = id
        self.username = username
        self.is_admin = is_admin

    @staticmethod
    def get(user_id):
        return User(id=user_id, username='admin', is_admin=True)