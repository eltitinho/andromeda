from werkzeug.serving import run_simple
from app import create_app

app = create_app()

if __name__ == '__main__':
    run_simple('localhost', 5000, app)

