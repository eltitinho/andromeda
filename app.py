from werkzeug.serving import run_simple
from flask_login import LoginManager
from app import create_app
from app.models import User

app = create_app()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

if __name__ == '__main__':
    run_simple('localhost', 5000, app)

