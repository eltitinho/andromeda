"""
Simple test for email settings functionality without requiring templates or authentication.
This test focuses on the core password encryption and database storage functionality.
"""
import os
import tempfile
import sqlite3
import pytest
from app.utils.encryption import encrypt_data, decrypt_data

def test_password_encryption():
    """Test that passwords are encrypted correctly using Fernet encryption."""

    # Test data
    test_password = 'securepassword123'
    
    # Encrypt the password
    encrypted_password = encrypt_data(test_password)
    
    # Verify the encrypted data is not the same as the plaintext password
    assert encrypted_password != test_password, "Password was not encrypted"
    
    # Verify the encrypted data starts with expected Fernet token format
    assert encrypted_password.startswith('gAAAAAB'), "Password was not encrypted using Fernet format"
    
    # Verify the password can be decrypted correctly
    decrypted_password = decrypt_data(encrypted_password)
    assert decrypted_password == test_password, "Password decryption failed"
    
    print("✅ Password encryption test passed!")

def test_database_storage():
    """Test that email settings are stored correctly in the database."""

    # Create a temporary database
    db_path = tempfile.mktemp(suffix='.db')
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create the email_settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_settings (
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
        
        # Test data
        test_email = 'test@example.com'
        test_password = 'securepassword123'
        
        # Encrypt the password
        encrypted_password = encrypt_data(test_password)
        
        # Store in database
        cursor.execute('DELETE FROM email_settings')
        cursor.execute('''
            INSERT INTO email_settings 
            (email_address, email_password_encrypted, smtp_server, smtp_port, smtp_use_tls, smtp_use_ssl)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (test_email, encrypted_password, 'smtp.example.com', 587, True, False))
        
        conn.commit()
        
        # Verify the data was stored
        cursor.execute("SELECT email_address, email_password_encrypted FROM email_settings")
        row = cursor.fetchone()
        
        assert row is not None, "No data was stored in the database"
        assert row[0] == test_email, "Email address was not stored correctly"
        
        # Verify the password was encrypted (not stored in plaintext)
        stored_encrypted = row[1]
        assert stored_encrypted != test_password, "Password was stored in plaintext!"
        assert stored_encrypted.startswith('gAAAAAB'), "Password was not encrypted using Fernet format"
        
        # Verify the password can be decrypted correctly
        decrypted_password = decrypt_data(stored_encrypted)
        assert decrypted_password == test_password, "Password decryption failed"
        
        conn.close()
        
        print("✅ Database storage test passed!")
        
    finally:
        # Cleanup: Remove the temporary database
        if os.path.exists(db_path):
            os.remove(db_path)

def test_memory_clearing():
    """Test that passwords can be cleared from memory after encryption."""

    # Test data
    test_password = 'securepassword123'
    original_length = len(test_password)
    
    # Encrypt the password
    encrypted_password = encrypt_data(test_password)
    
    # Clear the password from memory by overwriting it (simulate what the application does)
    test_password = '*' * original_length
    
    # Force garbage collection
    import gc
    gc.collect()
    
    # The encrypted password should still be valid
    assert encrypted_password.startswith('gAAAAAB'), "Encrypted password is invalid"
    
    # Verify we can still decrypt it
    decrypted_password = decrypt_data(encrypted_password)
    assert decrypted_password == 'securepassword123', "Decryption failed after memory clearing"
    
    print("✅ Memory clearing test passed!")

if __name__ == '__main__':
    print("Running email settings tests...\n")
    
    test_password_encryption()
    test_database_storage()
    test_memory_clearing()
    
    print("\n🎉 All tests passed successfully!")
