from flask import render_template, request, redirect, url_for, session
from app.decorators import login_required
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('tracking.db')
    conn.row_factory = sqlite3.Row
    return conn

def tracking_view():
    if request.method == 'POST':
        tracking_number = request.form['tracking_number']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tracking WHERE tracking_number = ?', (tracking_number,))
        tracking_data = cursor.fetchone()
        conn.close()
        if tracking_data:
            # Pass both tracking_number and status to the template
            return render_template('tracking_success.html',
                                tracking_number=tracking_number,
                                status=tracking_data['status'])
        else:
            return render_template('tracking_error.html')
    # Handle GET request with tracking_number parameter
    tracking_number = request.args.get('tracking_number')
    if tracking_number:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tracking WHERE tracking_number = ?', (tracking_number,))
        tracking_data = cursor.fetchone()
        conn.close()
        if tracking_data:
            # Pass both tracking_number and status to the template
            return render_template('tracking_success.html',
                                tracking_number=tracking_number,
                                status=tracking_data['status'])
        else:
            return render_template('tracking_error.html')
    return render_template('tracking_view.html')

def tracking_management():
    conn = sqlite3.connect('tracking.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM tracking')
    tracking_data = cursor.fetchall()

    conn.close()

    return render_template('tracking_management.html', tracking_data=tracking_data)