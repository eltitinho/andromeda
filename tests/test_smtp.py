"""
Test SMTP smart defaults functionality.
Tests automatic SMTP server detection based on email domain.
"""
import pytest
from app.utils.smtp import (
    get_smtp_server, get_smtp_port, get_smtp_use_tls, 
    get_smtp_use_ssl, get_smtp_settings, SMTP_PROVIDERS, SMTP_PORTS
)


class TestSMTPProviders:
    """Test known email provider detection"""
    
    def test_gmail_detection(self):
        """Test that Gmail addresses get correct SMTP server"""
        email = "user@gmail.com"
        expected_server = "smtp.gmail.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_googlemail_detection(self):
        """Test that Googlemail addresses get correct SMTP server"""
        email = "user@googlemail.com"
        expected_server = "smtp.gmail.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_hotmail_detection(self):
        """Test that Hotmail addresses get correct SMTP server (Office 365)"""
        email = "user@hotmail.com"
        expected_server = "smtp.office365.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_outlook_detection(self):
        """Test that Outlook addresses get correct SMTP server (Office 365)"""
        email = "user@outlook.com"
        expected_server = "smtp.office365.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_live_detection(self):
        """Test that Live addresses get correct SMTP server (Office 365)"""
        email = "user@live.com"
        expected_server = "smtp.office365.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_msn_detection(self):
        """Test that MSN addresses get correct SMTP server (Office 365)"""
        email = "user@msn.com"
        expected_server = "smtp.office365.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_tuta_detection(self):
        """Test that Tuta addresses get correct SMTP server"""
        email = "user@tuta.com"
        expected_server = "m.pop.tuta.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_tutanota_detection(self):
        """Test that Tutanota addresses get correct SMTP server"""
        email = "user@tutanota.com"
        expected_server = "m.pop.tuta.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_yahoo_detection(self):
        """Test that Yahoo addresses get correct SMTP server"""
        email = "user@yahoo.com"
        expected_server = "smtp.mail.yahoo.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_ymail_detection(self):
        """Test that Ymail addresses get correct SMTP server"""
        email = "user@ymail.com"
        expected_server = "smtp.mail.yahoo.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_rocketmail_detection(self):
        """Test that Rocketmail addresses get correct SMTP server"""
        email = "user@rocketmail.com"
        expected_server = "smtp.mail.yahoo.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_icloud_detection(self):
        """Test that iCloud addresses get correct SMTP server"""
        email = "user@icloud.com"
        expected_server = "smtp.mail.me.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_me_detection(self):
        """Test that me.com addresses get correct SMTP server"""
        email = "user@me.com"
        expected_server = "smtp.mail.me.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_mac_detection(self):
        """Test that mac.com addresses get correct SMTP server"""
        email = "user@mac.com"
        expected_server = "smtp.mail.me.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_protonmail_detection(self):
        """Test that ProtonMail addresses get correct SMTP server"""
        email = "user@protonmail.com"
        expected_server = "smtp.protonmail.ch"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_proton_me_detection(self):
        """Test that proton.me addresses get correct SMTP server"""
        email = "user@proton.me"
        expected_server = "smtp.protonmail.ch"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_zoho_detection(self):
        """Test that Zoho addresses get correct SMTP server"""
        email = "user@zoho.com"
        expected_server = "smtp.zoho.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_aol_detection(self):
        """Test that AOL addresses get correct SMTP server"""
        email = "user@aol.com"
        expected_server = "smtp.aol.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_fastmail_detection(self):
        """Test that FastMail addresses get correct SMTP server"""
        email = "user@fastmail.com"
        expected_server = "smtp.fastmail.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_fastmail_fm_detection(self):
        """Test that fastmail.fm addresses get correct SMTP server"""
        email = "user@fastmail.fm"
        expected_server = "smtp.fastmail.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_mail_com_detection(self):
        """Test that mail.com addresses get correct SMTP server"""
        email = "user@mail.com"
        expected_server = "smtp.mail.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"


class TestCustomDomainFallback:
    """Test fallback behavior for custom domains"""
    
    def test_custom_domain_fallback(self):
        """Test that custom domains fall back to smtp.{domain}"""
        email = "user@company.com"
        expected_server = "smtp.company.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_subdomain_handling(self):
        """Test that subdomains are handled correctly"""
        email = "user@mail.company.co.uk"
        expected_server = "smtp.mail.company.co.uk"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"
    
    def test_case_insensitive_domain(self):
        """Test that domain matching is case insensitive"""
        email = "user@GMAIL.COM"
        expected_server = "smtp.gmail.com"
        
        server = get_smtp_server(email)
        assert server == expected_server, f"Expected {expected_server}, got {server}"


class TestSMTPPorts:
    """Test SMTP port configuration"""
    
    def test_office365_port(self):
        """Test that Office365 uses port 587"""
        port = get_smtp_port("smtp.office365.com")
        assert port == 587, f"Expected 587, got {port}"
    
    def test_gmail_port(self):
        """Test that Gmail uses port 587"""
        port = get_smtp_port("smtp.gmail.com")
        assert port == 587, f"Expected 587, got {port}"
    
    def test_tuta_port(self):
        """Test that Tuta uses port 587"""
        port = get_smtp_port("m.pop.tuta.com")
        assert port == 587, f"Expected 587, got {port}"
    
    def test_unknown_server_default_port(self):
        """Test that unknown servers use default port 587"""
        port = get_smtp_port("smtp.unknown.com")
        assert port == 587, f"Expected 587, got {port}"


class TestTLSConfiguration:
    """Test TLS configuration"""
    
    def test_office365_use_tls(self):
        """Test that Office365 has TLS enabled"""
        use_tls = get_smtp_use_tls("smtp.office365.com")
        assert use_tls == True, f"Expected True, got {use_tls}"
    
    def test_gmail_use_tls(self):
        """Test that Gmail has TLS enabled"""
        use_tls = get_smtp_use_tls("smtp.gmail.com")
        assert use_tls == True, f"Expected True, got {use_tls}"
    
    def test_unknown_server_default_tls(self):
        """Test that unknown servers have TLS enabled by default"""
        use_tls = get_smtp_use_tls("smtp.unknown.com")
        assert use_tls == True, f"Expected True, got {use_tls}"


class TestSSLConfiguration:
    """Test SSL configuration"""
    
    def test_office365_use_ssl(self):
        """Test that Office365 has SSL disabled (uses STARTTLS)"""
        use_ssl = get_smtp_use_ssl("smtp.office365.com")
        assert use_ssl == False, f"Expected False, got {use_ssl}"
    
    def test_gmail_use_ssl(self):
        """Test that Gmail has SSL disabled (uses STARTTLS)"""
        use_ssl = get_smtp_use_ssl("smtp.gmail.com")
        assert use_ssl == False, f"Expected False, got {use_ssl}"
    
    def test_unknown_server_default_ssl(self):
        """Test that unknown servers have SSL disabled by default"""
        use_ssl = get_smtp_use_ssl("smtp.unknown.com")
        assert use_ssl == False, f"Expected False, got {use_ssl}"


class TestCompleteSettings:
    """Test complete SMTP settings retrieval"""
    
    def test_gmail_complete_settings(self):
        """Test complete settings for Gmail"""
        email = "user@gmail.com"
        settings = get_smtp_settings(email)
        
        assert settings['smtp_server'] == "smtp.gmail.com"
        assert settings['smtp_port'] == 587
        assert settings['smtp_use_tls'] == True
        assert settings['smtp_use_ssl'] == False
    
    def test_hotmail_complete_settings(self):
        """Test complete settings for Hotmail"""
        email = "user@hotmail.com"
        settings = get_smtp_settings(email)
        
        assert settings['smtp_server'] == "smtp.office365.com"
        assert settings['smtp_port'] == 587
        assert settings['smtp_use_tls'] == True
        assert settings['smtp_use_ssl'] == False
    
    def test_tuta_complete_settings(self):
        """Test complete settings for Tuta"""
        email = "user@tuta.com"
        settings = get_smtp_settings(email)
        
        assert settings['smtp_server'] == "m.pop.tuta.com"
        assert settings['smtp_port'] == 587
        assert settings['smtp_use_tls'] == True
        assert settings['smtp_use_ssl'] == False
    
    def test_custom_domain_complete_settings(self):
        """Test complete settings for custom domain"""
        email = "user@company.com"
        settings = get_smtp_settings(email)
        
        assert settings['smtp_server'] == "smtp.company.com"
        assert settings['smtp_port'] == 587
        assert settings['smtp_use_tls'] == True
        assert settings['smtp_use_ssl'] == False


class TestProviderMappings:
    """Test that all providers in the mapping are valid"""
    
    def test_all_providers_have_mapping(self):
        """Test that all known providers have valid SMTP servers"""
        for domain, smtp_server in SMTP_PROVIDERS.items():
            assert isinstance(smtp_server, str), f"Invalid SMTP server for {domain}"
            assert len(smtp_server) > 0, f"Empty SMTP server for {domain}"
    
    def test_all_ports_have_valid_config(self):
        """Test that all port configurations are valid tuples"""
        for smtp_server, config in SMTP_PORTS.items():
            assert isinstance(config, tuple), f"Invalid config for {smtp_server}"
            assert len(config) == 3, f"Config must have 3 elements for {smtp_server}"
            port, use_tls, use_ssl = config
            assert isinstance(port, int), f"Port must be int for {smtp_server}"
            assert isinstance(use_tls, bool), f"use_tls must be bool for {smtp_server}"
            assert isinstance(use_ssl, bool), f"use_ssl must be bool for {smtp_server}"


class TestFormHandling:
    """Test form handling behavior"""
    
    def test_form_with_custom_settings(self):
        """Test that custom SMTP settings override defaults"""
        # This simulates the logic in email_settings route
        email = "user@example.com"
        custom_server = "custom.smtp.server"
        custom_port = 465
        
        # Simulate form data with custom settings
        form_data = {'smtp_server': custom_server, 'smtp_port': str(custom_port)}
        if 'smtp_server' in form_data:
            smtp_server = form_data['smtp_server']
            smtp_port = int(form_data.get('smtp_port', 587))
        else:
            smtp_config = get_smtp_settings(email)
            smtp_server = smtp_config['smtp_server']
            smtp_port = smtp_config['smtp_port']
        
        assert smtp_server == custom_server, "Custom SMTP server should be used"
        assert smtp_port == 465, "Custom SMTP port should be used"
    
    def test_form_without_custom_settings(self):
        """Test that defaults are used when custom settings not provided"""
        email = "user@example.com"
        
        # Simulate form data without custom settings
        form_data = {}
        if 'smtp_server' in form_data:
            smtp_server = form_data['smtp_server']
            smtp_port = int(form_data.get('smtp_port', 587))
        else:
            smtp_config = get_smtp_settings(email)
            smtp_server = smtp_config['smtp_server']
            smtp_port = smtp_config['smtp_port']
        
        assert smtp_server == "smtp.example.com", "Default SMTP server should be used"
        assert smtp_port == 587, "Default SMTP port should be used"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

