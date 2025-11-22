from flask import Flask, render_template, request, redirect, url_for
import sqlite3

tracking = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('tracking.db')
    conn.row_factory = sqlite3.Row
    return conn

@tracking.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        option = request.form['option']
        if option == '1':
            return redirect(url_for('login'))
        elif option == '2':
            return redirect(url_for('tracking_view'))
    return render_template('home.html')

@tracking.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        tracking_number = request.form['tracking_number']
        return redirect(url_for('track', tracking_number=tracking_number))
    return render_template('login.html')

@tracking.route('/tracking_view', methods=['GET', 'POST'])
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

@tracking.route('/tracking_management')
def tracking_management():
    # Connect to the database
    conn = sqlite3.connect('tracking.db')  # Using the same database as other routes
    cursor = conn.cursor()

    # Fetch data from the database
    cursor.execute('SELECT * FROM tracking')  # Using the same table as other routes
    tracking_data = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Render the template with the fetched data
    return render_template('tracking_management.html', tracking_data=tracking_data)

if __name__ == '__main__':
    tracking.run(debug=True)
