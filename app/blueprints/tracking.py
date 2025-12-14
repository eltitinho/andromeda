# app/blueprints/tracking.py
from flask import request, render_template, redirect, url_for, Blueprint, jsonify
from flask_login import current_user
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
            return render_template('tracking/success.html',
                                tracking_number=tracking_number,
                                status=tracking_data['status'])
        else:
            return render_template('tracking/error.html')
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
            return render_template('tracking/success.html',
                                tracking_number=tracking_number,
                                status=tracking_data['status'])
        else:
            return render_template('tracking/error.html')
    return render_template('tracking/view.html')

def tracking_management():
    conn = sqlite3.connect('tracking.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM tracking')
    tracking_data = cursor.fetchall()

    conn.close()

    return render_template('tracking/management.html', tracking_data=tracking_data)

def delete_tracking(tracking_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tracking WHERE tracking_number = ?', (tracking_number,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'}), 200

def update_tracking_status(tracking_number, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE tracking SET status = ? WHERE tracking_number = ?', (new_status, tracking_number))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'}), 200

def create_tracking_number(tracking_number, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tracking (tracking_number, status) VALUES (?, ?)', (tracking_number, status))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'}), 201

# Create a blueprint for public tracking features
public_tracking_bp = Blueprint('public_tracking', __name__)

@public_tracking_bp.route('/view', methods=['GET', 'POST'])
def public_tracking_view():
    return tracking_view()

# Create a blueprint for private tracking features
tracking_bp = Blueprint('tracking', __name__)

@tracking_bp.before_request
def before_tracking_request():
    if not current_user.is_authenticated:
        return redirect(url_for('public.login', next=request.url))

@tracking_bp.route('/management')
def tracking_management_route():
    return tracking_management()

@tracking_bp.route('/details')
def tracking_details():
    return render_template('tracking/details.html')

@tracking_bp.route('/error')
def tracking_error():
    return render_template('tracking/error.html')

@tracking_bp.route('/success')
def tracking_success():
    return render_template('tracking/success.html')

@tracking_bp.route('/delete/<tracking_number>', methods=['DELETE'])
def delete_tracking_route(tracking_number):
    return delete_tracking(tracking_number)

@tracking_bp.route('/update_status/<tracking_number>', methods=['POST'])
def update_status_route(tracking_number):
    data = request.get_json()
    new_status = data.get('status')
    return update_tracking_status(tracking_number, new_status)

@tracking_bp.route('/create', methods=['POST'])
def create_tracking_route():
    data = request.get_json()
    tracking_number = data.get('tracking_number')
    status = data.get('status')
    return create_tracking_number(tracking_number, status)