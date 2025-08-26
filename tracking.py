# app.py
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

tracking = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('tracking.db')
    conn.row_factory = sqlite3.Row
    return conn

@tracking.route('/', methods=['GET', 'POST'])
def track_number():
    print("Request method:", request.method)
    if request.method == 'POST':
        tracking_number = request.form['tracking_number']
        return redirect(url_for('track', tracking_number=tracking_number))
    return render_template('tracking_number.html')

@tracking.route('/track/<tracking_number>')
def track(tracking_number):
    conn = get_db_connection()
    status = conn.execute('SELECT * FROM tracking WHERE tracking_number = ?',
                          (tracking_number,)).fetchone()
    conn.close()
    return render_template('tracking.html', status=status)

if __name__ == '__main__':
    tracking.run(debug=True)
