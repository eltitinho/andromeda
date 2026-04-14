#!/usr/bin/env python3
"""
Encryption utilities for Andromeda using keyring for server-safe storage
"""

import keyring
import keyring.backends
from cryptography.fernet import Fernet
import logging
import os
import sys

logger = logging.getLogger(__name__)

SERVICE_NAME = "andromeda"
KEY_NAME = "encryption_key"
KEY_FILE = os.path.expanduser("~/.andromeda/encryption_key")

def setup_keyring():
    """
    Configure keyring to use the best available backend.
    """
    try:
        # Get the current keyring - it should already be configured
        current_backend = keyring.get_keyring()
        logger.info(f"Using keyring backend: {current_backend} (priority: {current_backend.priority})")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize keyring: {e}")
        return False

def get_encryption_key():
    """
    Get encryption key from keyring or file, creating one if it doesn't exist.
    Returns Fernet key as bytes.
    """
    # Try keyring first
    try:
        if setup_keyring():
            key = keyring.get_password(SERVICE_NAME, KEY_NAME)
            if key:
                logger.debug("Loaded encryption key from keyring")
                return key.encode()
            
            # Create and store new key in keyring
            new_key = Fernet.generate_key()
            keyring.set_password(SERVICE_NAME, KEY_NAME, new_key.decode())
            logger.info("Generated and stored new encryption key in keyring")
            return new_key
    except Exception as e:
        logger.debug(f"Keyring not available or locked, falling back to file: {e}")
    
    # Fall back to file storage
    try:
        # Create directory with restrictive permissions
        keyring_dir = os.path.dirname(KEY_FILE)
        os.makedirs(keyring_dir, mode=0o700, exist_ok=True)
        
        # Try to read existing key from file
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, 'rb') as f:
                key = f.read()
            logger.debug(f"Loaded encryption key from file {KEY_FILE}")
            return key
        
        # Generate and store new key in file
        new_key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            os.chmod(KEY_FILE, 0o400)  # Read-only for owner
            f.write(new_key)
        logger.info(f"Generated and stored new encryption key in file {KEY_FILE}")
        return new_key
        
    except Exception as e:
        logger.error(f"Failed to access encryption key file: {e}")
        raise RuntimeError(f"Could not access encryption key storage: {e}")

def encrypt_data(data: str) -> str:
    """
    Encrypt data using Fernet symmetric encryption.
    Returns base64-encoded encrypted string.
    """
    if not data:
        return ""
    
    fernet = Fernet(get_encryption_key())
    encrypted = fernet.encrypt(data.encode())
    return encrypted.decode()

def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt data using Fernet symmetric encryption.
    Returns original string.
    """
    if not encrypted_data:
        return ""
    
    fernet = Fernet(get_encryption_key())
    decrypted = fernet.decrypt(encrypted_data.encode())
    return decrypted.decode()

# Initialize keyring on module import
setup_keyring()
