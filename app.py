from flask import Flask, render_template
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from invoicing import invoicing
from tracking import tracking

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

application = DispatcherMiddleware(
    app,
    {
        '/invoicing': invoicing,
        '/tracking': tracking
    }
)

if __name__ == '__main__':
    run_simple('localhost', 5000, application)