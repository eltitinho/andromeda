from flask import Flask, render_template
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from invoicing import invoicing
from tracking import tracking

main_app = Flask(__name__)

@main_app.route('/')
def index():
    return render_template('index.html')

# Combine both apps to serve on the same port
application = DispatcherMiddleware(
    main_app
    , {
        '/invoicing': invoicing
        , '/tracking': tracking
    }
)

if __name__ == '__main__':
    run_simple('localhost', 5000, application)

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 5000, combined_app)
