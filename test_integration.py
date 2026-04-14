#!/usr/bin/env python3
"""
Integration test for the encryption system within the Flask app context
"""

import sys
import os
import tempfile
import sqlite3
import pytest

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app.utils.encryption import encrypt_data, decrypt_data

@pytest.fixture(scope="module")
def db_connection():
    """Create a temporary database for testing"""
    db_path = tempfile.mktemp(suffix='.db')
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable named columns
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE email_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_address TEXT NOT NULL,
            email_password_encrypted TEXT NOT NULL,
            smtp_server TEXT NOT NULL,
            smtp_port INTEGER NOT NULL,
            smtp_use_tls BOOLEAN NOT NULL,
            smtp_use_ssl BOOLEAN NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    yield conn
    
    # Cleanup
    conn.close()
    if os.path.exists(db_path):
        os.remove(db_path)

def test_encryption_in_app_context():
    """Test encryption/decryption in the actual app context"""
    # Test data
    test_password = "my-test-password-123!"
    
    # Encrypt
    encrypted = encrypt_data(test_password)
    
    # Verify encryption produces different output
    assert encrypted != test_password, "Encrypted data should differ from original"
    assert isinstance(encrypted, str), "Encrypted data should be a string"
    assert len(encrypted) > 0, "Encrypted data should not be empty"
    
    # Decrypt
    decrypted = decrypt_data(encrypted)
    
    # Verify decryption
    assert decrypted == test_password, f"Decrypted password doesn't match. Expected: {test_password}, Got: {decrypted}"

def test_database_integration(db_connection):
    """Test that encrypted passwords work with the database"""
    cursor = db_connection.cursor()
    
    # Test data
    test_email = 'test@example.com'
    test_password = 'secure-password-123'
    
    # Encrypt and store
    encrypted_password = encrypt_data(test_password)
    cursor.execute('INSERT INTO email_settings (email_address, email_password_encrypted, smtp_server, smtp_port, smtp_use_tls, smtp_use_ssl) VALUES (?, ?, ?, ?, ?, ?)',
                  (test_email, encrypted_password, 'smtp.example.com', 587, True, False))
    db_connection.commit()
    
    # Retrieve and decrypt
    cursor.execute('SELECT email_address, email_password_encrypted FROM email_settings')
    row = cursor.fetchone()
    
    decrypted_password = decrypt_data(row['email_password_encrypted'])
    
    # Verify
    assert row['email_address'] == test_email, "Email address not stored correctly"
    assert decrypted_password == test_password, "Password decryption failed"
    assert encrypted_password != test_password, "Password should be encrypted, not stored in plaintext"

def test_multiple_records(db_connection):
    """Test storing and retrieving multiple encrypted records"""
    cursor = db_connection.cursor()
    
    # Test data - multiple records
    test_data = [
        ('user1@example.com', 'password1'),
        ('user2@example.com', 'password2'),
        ('user3@example.com', 'password3')
    ]
    
    # Store multiple records
    for email, password in test_data:
        encrypted_password = encrypt_data(password)
        cursor.execute('INSERT INTO email_settings (email_address, email_password_encrypted, smtp_server, smtp_port, smtp_use_tls, smtp_use_ssl) VALUES (?, ?, ?, ?, ?, ?)',
                      (email, encrypted_password, 'smtp.example.com', 587, True, False))
    db_connection.commit()
    
    # Retrieve and verify all records
    cursor.execute('SELECT email_address, email_password_encrypted FROM email_settings ORDER BY id')
    rows = cursor.fetchall()
    
    assert len(rows) == len(test_data), "Number of stored records doesn't match"
    
    for i, (email, password) in enumerate(test_data):
        decrypted_password = decrypt_data(rows[i]['email_password_encrypted'])
        assert rows[i]['email_address'] == email, f"Email mismatch for record {i}"
        assert decrypted_password == password, f"Password mismatch for record {i}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
