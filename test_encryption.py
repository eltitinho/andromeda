#!/usr/bin/env python3
"""
Test script to verify the encryption system works correctly
"""

import sys
import os
import pytest

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app.utils.encryption import encrypt_data, decrypt_data, setup_keyring

@pytest.fixture(scope="module", autouse=True)
def setup_encryption():
    """Initialize keyring before tests run"""
    success = setup_keyring()
    assert success, "Failed to initialize keyring"

def test_encryption():
    """Test that encryption and decryption work correctly"""
    # Test data
    test_password = "my-secret-password-123!"
    
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

def test_empty_string():
    """Test that empty strings are handled correctly"""
    empty = ""
    encrypted = encrypt_data(empty)
    decrypted = decrypt_data(encrypted)
    
    assert decrypted == empty, "Empty string encryption/decryption failed"

def test_special_characters():
    """Test encryption with special characters"""
    special_password = "p@$$w0rd!#$%^&*()_+-=[]{}|;':",./<>?"
    encrypted = encrypt_data(special_password)
    decrypted = decrypt_data(encrypted)
    
    assert decrypted == special_password, "Special characters not handled correctly"

def test_unicode_characters():
    """Test encryption with unicode characters"""
    unicode_password = "parola-secreta-密码-пароль-🔒"
    encrypted = encrypt_data(unicode_password)
    decrypted = decrypt_data(encrypted)
    
    assert decrypted == unicode_password, "Unicode characters not handled correctly"

def test_long_password():
    """Test encryption with very long password"""
    long_password = "a" * 1000  # 1000 character password
    encrypted = encrypt_data(long_password)
    decrypted = decrypt_data(encrypted)
    
    assert decrypted == long_password, "Long password not handled correctly"
    assert len(encrypted) < len(long_password), "Encrypted data should be more compact than very long plaintext"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
