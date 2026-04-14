#!/usr/bin/env python3
"""
Test script to verify the new email sending implementation works
"""

from app import create_app
from app.invoicing import update_mail_config, send_email_with_current_config

def test_email_sending():
    """Test the new email sending implementation"""
    print("=== Testing Email Sending Implementation ===")
    
    # Create the app
    app = create_app()
    print("✅ App created")
    
    # Test configuration update
    with app.app_context():
        print("\n1. Testing configuration update...")
        if update_mail_config():
            print("✅ Mail configuration updated successfully")
        else:
            print("❌ Failed to update mail configuration")
            return False
        
        print("\n2. Testing email sending...")
        if send_email_with_current_config():
            print("✅ Email sent successfully!")
            return True
        else:
            print("❌ Email sending failed")
            return False

if __name__ == "__main__":
    success = test_email_sending()
    if success:
        print("\n🎉 All tests passed! Email sending is working correctly.")
    else:
        print("\n💥 Some tests failed. Check the error messages above.")
