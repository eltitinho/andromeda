from flask import Flask, render_template, request, redirect, url_for
import sqlite3

tracking = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('tracking.db')
    conn.row_factory = sqlite3.Row
    return conn

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