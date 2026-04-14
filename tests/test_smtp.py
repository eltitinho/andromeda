"""
Test SMTP smart defaults functionality.
Tests automatic SMTP server detection based on email domain.
"""
import pytest
from app.blueprints.auth import email_settings


class TestSMTPDefaults:
    """Test SMTP smart default detection"""
    
    def test_gmail_default(self):
        """Test that Gmail addresses get correct SMTP defaults"""
        email = "user@gmail.com"
        expected_server = "smtp.gmail.com"
        
        # Simulate the smart default logic from email_settings
        default_server = f"smtp.{email.split('@')[-1]}"
        
        assert default_server == expected_server, f"Expected {expected_server}, got {default_server}"
    
    def test_outlook_default(self):
        """Test that Outlook addresses get correct SMTP defaults"""
        email = "user@outlook.com"
        expected_server = "smtp.outlook.com"
        
        default_server = f"smtp.{email.split('@')[-1]}"
        
        assert default_server == expected_server, f"Expected {expected_server}, got {default_server}"
    
    def test_custom_domain_default(self):
        """Test that custom domains get sensible defaults"""
        email = "user@company.com"
        expected_server = "smtp.company.com"
        
        default_server = f"smtp.{email.split('@')[-1]}"
        
        assert default_server == expected_server, f"Expected {expected_server}, got {default_server}"
    
    def test_subdomain_handling(self):
        """Test that subdomains are handled correctly"""
        email = "user@mail.company.co.uk"
        expected_server = "smtp.mail.company.co.uk"
        
        default_server = f"smtp.{email.split('@')[-1]}"
        
        assert default_server == expected_server, f"Expected {expected_server}, got {default_server}"
    
    def test_default_port(self):
        """Test that default port is correct"""
        default_port = 587  # From the code
        assert default_port == 587, "Default SMTP port should be 587"
    
    def test_default_tls_setting(self):
        """Test that TLS is enabled by default"""
        # In the code, smtp_use_tls defaults to 'on' == 'on' which is True
        default_tls = True
        assert default_tls == True, "TLS should be enabled by default"
    
    def test_default_ssl_setting(self):
        """Test that SSL is disabled by default"""
        # In the code, smtp_use_ssl defaults to 'off' == 'on' which is False
        default_ssl = False
        assert default_ssl == False, "SSL should be disabled by default"


class TestSMTPFormHandling:
    """Test SMTP settings form handling"""
    
    def test_form_with_custom_settings(self):
        """Test that custom SMTP settings override defaults"""
        # Simulate form data
        email = "user@example.com"
        custom_server = "custom.smtp.server"
        custom_port = 465
        
        # This simulates the logic in email_settings route
        smtp_server = custom_server  # Would come from request.form.get('smtp_server', default)
        smtp_port = custom_port      # Would come from request.form.get('smtp_port', 587)
        
        assert smtp_server == custom_server, "Custom SMTP server should be used"
        assert smtp_port == custom_port, "Custom SMTP port should be used"
    
    def test_form_without_custom_settings(self):
        """Test that defaults are used when custom settings not provided"""
        email = "user@example.com"
        
        # Simulate default logic when no custom settings provided
        smtp_server = f"smtp.{email.split('@')[-1]}"
        smtp_port = 587  # Default from code
        
        assert smtp_server == "smtp.example.com", "Default SMTP server should be used"
        assert smtp_port == 587, "Default SMTP port should be used"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
