"""
Email authentication utilities for Poker Therapist.

This module provides shared email validation and authorization logic
used by the main application and test suites.
"""

import os


def validate_email(email: str) -> bool:
    """
    Validate email format for authentication.
    
    Checks that email has valid structure:
    - Contains exactly one @ symbol
    - Has non-empty username before @
    - Has non-empty domain after @
    - Domain contains at least one dot
    
    Note: This is intentionally simple validation suitable for the application's
    needs. It correctly validates all common email formats while remaining fast
    and dependency-free. For stricter RFC 5322 compliance, consider using the
    email-validator library, but that's typically unnecessary for this use case.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid format, False otherwise
        
    Examples:
        >>> validate_email("test@example.com")
        True
        >>> validate_email("user@domain.co.uk")
        True
        >>> validate_email("invalid.email")
        False
        >>> validate_email("@domain.com")
        False
    """
    parts = email.split("@")
    # Explicitly convert to bool to handle empty string case
    return bool(len(parts) == 2 and parts[0] and parts[1] and "." in parts[1])


def get_default_authorized_emails() -> list[str]:
    """
    Get the default list of authorized email addresses.
    
    These emails have VIP access with full voice and Rex personality features.
    
    Returns:
        List of authorized email addresses
    """
    return [
        "m.fanelli1@icloud.com",      # Apple iCloud
        "johndawalka@icloud.com",     # Apple iCloud
        "mauro.fanelli@ctstate.edu",  # Institutional Microsoft
        "maurofanellijr@gmail.com",   # Google Gmail
        "cooljack87@icloud.com",      # Apple iCloud
        "jdwalka@pm.me",              # ProtonMail
    ]


def load_authorized_emails() -> list[str]:
    """
    Load authorized emails from environment or use defaults.
    
    Checks the AUTHORIZED_EMAILS environment variable for a comma-separated
    list of email addresses. If not set, returns the default authorized list.
    
    Returns:
        List of authorized email addresses
        
    Example:
        >>> os.environ["AUTHORIZED_EMAILS"] = "test1@example.com,test2@example.com"
        >>> load_authorized_emails()
        ['test1@example.com', 'test2@example.com']
    """
    env_emails = os.getenv("AUTHORIZED_EMAILS", "").strip()
    if env_emails:
        return [email.strip() for email in env_emails.split(",") if email.strip()]
    
    return get_default_authorized_emails()


def is_authorized_email(email: str) -> bool:
    """
    Check if an email address is in the authorized VIP list.
    
    Args:
        email: Email address to check
        
    Returns:
        True if email is authorized, False otherwise
    """
    return email in load_authorized_emails()


def get_emails_by_provider() -> dict[str, list[str]]:
    """
    Group authorized emails by provider type.
    
    Returns:
        Dictionary mapping provider names to lists of email addresses
        
    Example:
        >>> emails = get_emails_by_provider()
        >>> emails['icloud']
        ['m.fanelli1@icloud.com', 'johndawalka@icloud.com', 'cooljack87@icloud.com']
    """
    authorized = load_authorized_emails()
    
    return {
        'icloud': [e for e in authorized if '@icloud.com' in e],
        'gmail': [e for e in authorized if '@gmail.com' in e],
        'institutional': [e for e in authorized if '@ctstate.edu' in e],
        'other': [e for e in authorized 
                  if not any(domain in e for domain in ['@icloud.com', '@gmail.com', '@ctstate.edu'])]
    }
