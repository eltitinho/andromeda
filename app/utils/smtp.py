"""SMTP server detection utilities"""
from typing import Optional, Dict, Tuple

# Known email providers and their SMTP servers
SMTP_PROVIDERS = {
    # Google
    'gmail.com': 'smtp.gmail.com',
    'googlemail.com': 'smtp.gmail.com',
    'google.com': 'smtp.gmail.com',
    
    # Microsoft
    'hotmail.com': 'smtp.office365.com',
    'outlook.com': 'smtp.office365.com',
    'live.com': 'smtp.office365.com',
    'msn.com': 'smtp.office365.com',
    'passport.com': 'smtp.office365.com',
    
    # Tuta
    'tuta.com': 'm.pop.tuta.com',
    'tutanota.com': 'm.pop.tuta.com',
    
    # Yahoo
    'yahoo.com': 'smtp.mail.yahoo.com',
    'ymail.com': 'smtp.mail.yahoo.com',
    'rocketmail.com': 'smtp.mail.yahoo.com',
    
    # iCloud
    'icloud.com': 'smtp.mail.me.com',
    'me.com': 'smtp.mail.me.com',
    'mac.com': 'smtp.mail.me.com',
    
    # ProtonMail
    'protonmail.com': 'smtp.protonmail.ch',
    'proton.me': 'smtp.protonmail.ch',
    
    # Zoho
    'zoho.com': 'smtp.zoho.com',
    'zohomail.com': 'smtp.zoho.com',
    
    # AOL
    'aol.com': 'smtp.aol.com',
    'aim.com': 'smtp.aol.com',
    
    # FastMail
    'fastmail.com': 'smtp.fastmail.com',
    'fastmail.fm': 'smtp.fastmail.com',
    
    # Mail.com
    'mail.com': 'smtp.mail.com',
}

# Known SMTP ports and security settings for providers
# Tuple format: (port, use_tls, use_ssl)
SMTP_PORTS = {
    # Microsoft prefers 587 with STARTTLS
    'smtp.office365.com': (587, True, False),
    
    # Gmail
    'smtp.gmail.com': (587, True, False),
    
    # Tuta uses 587
    'm.pop.tuta.com': (587, True, False),
    
    # Yahoo
    'smtp.mail.yahoo.com': (587, True, False),
    
    # iCloud
    'smtp.mail.me.com': (587, True, False),
    
    # ProtonMail uses 587
    'smtp.protonmail.ch': (587, True, False),
    
    # Zoho
    'smtp.zoho.com': (587, True, False),
    
    # AOL
    'smtp.aol.com': (587, True, False),
    
    # FastMail
    'smtp.fastmail.com': (587, True, False),
    
    # Mail.com
    'smtp.mail.com': (587, True, False),
}


def get_smtp_server(email_address: str) -> str:
    """
    Get the SMTP server for a given email address.
    
    Priority:
    1. Check if domain is a known provider
    2. Try to resolve MX records for the domain
    3. Fall back to smtp.{domain}
    
    Args:
        email_address: The email address to get SMTP server for
        
    Returns:
        The SMTP server hostname
    """
    domain = email_address.split('@')[-1].lower()
    
    # Check known providers first
    if domain in SMTP_PROVIDERS:
        return SMTP_PROVIDERS[domain]
    
    # Try to resolve MX records (optional dependency)
    try:
        import dns.resolver
        mx_records = dns.resolver.resolve(domain, 'MX')
        if mx_records:
            # Get the highest priority MX record
            mx_record = sorted(mx_records, key=lambda r: r.preference)[0]
            mx_host = str(mx_record.exchange)
            
            # Clean up the MX host (remove trailing dot if present)
            if mx_host.endswith('.'):
                mx_host = mx_host[:-1]
            
            return mx_host
    except (ImportError, Exception):
        # If dnspython not installed or DNS resolution fails, continue to fallback
        pass
    
    # Fallback to simple pattern
    return f'smtp.{domain}'


def get_smtp_port(smtp_server: str) -> int:
    """
    Get the recommended port for a given SMTP server.
    
    Args:
        smtp_server: The SMTP server hostname
        
    Returns:
        The recommended port number
    """
    if smtp_server in SMTP_PORTS:
        return SMTP_PORTS[smtp_server][0]
    return 587  # Default port for SMTP submission


def get_smtp_use_tls(smtp_server: str) -> bool:
    """
    Get the recommended TLS setting for a given SMTP server.
    
    Args:
        smtp_server: The SMTP server hostname
        
    Returns:
        True if TLS should be used
    """
    if smtp_server in SMTP_PORTS:
        return SMTP_PORTS[smtp_server][1]
    return True  # Default to TLS enabled


def get_smtp_use_ssl(smtp_server: str) -> bool:
    """
    Get the recommended SSL setting for a given SMTP server.
    
    Args:
        smtp_server: The SMTP server hostname
        
    Returns:
        True if SSL should be used
    """
    if smtp_server in SMTP_PORTS:
        return SMTP_PORTS[smtp_server][2]
    return False  # Default to SSL disabled (use STARTTLS instead)


def get_smtp_settings(email_address: str) -> Dict[str, any]:
    """
    Get complete SMTP settings for a given email address.
    
    Args:
        email_address: The email address
        
    Returns:
        Dictionary with smtp_server, smtp_port, smtp_use_tls, smtp_use_ssl
    """
    smtp_server = get_smtp_server(email_address)
    return {
        'smtp_server': smtp_server,
        'smtp_port': get_smtp_port(smtp_server),
        'smtp_use_tls': get_smtp_use_tls(smtp_server),
        'smtp_use_ssl': get_smtp_use_ssl(smtp_server),
    }
