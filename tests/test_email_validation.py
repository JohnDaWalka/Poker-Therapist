"""Test email validation logic for authentication"""

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False


def validate_email(email: str) -> bool:
    """
    Validate email format for authentication.
    
    This is the same validation logic used in chatbot_app.py.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid format, False otherwise
    """
    parts = email.split("@")
    return len(parts) == 2 and parts[0] and parts[1] and "." in parts[1]


class TestEmailValidation:
    """Test email validation for authentication"""
    
    def test_authorized_icloud_emails(self):
        """Test that iCloud emails are validated correctly"""
        emails = [
            "m.fanelli1@icloud.com",
            "johndawalka@icloud.com",
            "cooljack87@icloud.com",
        ]
        for email in emails:
            assert validate_email(email), f"{email} should be valid"
    
    def test_authorized_gmail_emails(self):
        """Test that Gmail emails are validated correctly"""
        emails = [
            "maurofanellijr@gmail.com",
        ]
        for email in emails:
            assert validate_email(email), f"{email} should be valid"
    
    def test_authorized_institutional_emails(self):
        """Test that institutional Microsoft emails are validated correctly"""
        emails = [
            "mauro.fanelli@ctstate.edu",
        ]
        for email in emails:
            assert validate_email(email), f"{email} should be valid"
    
    def test_other_authorized_emails(self):
        """Test other authorized email providers"""
        emails = [
            "jdwalka@pm.me",
        ]
        for email in emails:
            assert validate_email(email), f"{email} should be valid"
    
    def test_valid_email_formats(self):
        """Test various valid email formats"""
        valid_emails = [
            "test@example.com",
            "user@domain.co.uk",
            "name+tag@gmail.com",
            "first.last@company.com",
            "user123@test.org",
        ]
        for email in valid_emails:
            assert validate_email(email), f"{email} should be valid"
    
    def test_invalid_email_formats(self):
        """Test that invalid email formats are rejected"""
        invalid_emails = [
            "invalid.email",          # No @ symbol
            "@domain.com",            # No username
            "user@",                  # No domain
            "user@domain",            # No TLD
            "user@@domain.com",       # Double @
            "",                       # Empty string
            "user",                   # Just username
        ]
        for email in invalid_emails:
            assert not validate_email(email), f"{email} should be invalid"
    
    def test_all_default_authorized_emails(self):
        """Test that all default authorized emails pass validation"""
        authorized_emails = [
            "m.fanelli1@icloud.com",
            "johndawalka@icloud.com",
            "mauro.fanelli@ctstate.edu",
            "maurofanellijr@gmail.com",
            "cooljack87@icloud.com",
            "jdwalka@pm.me",
        ]
        for email in authorized_emails:
            assert validate_email(email), f"Authorized email {email} should be valid"


if __name__ == "__main__":
    # Run tests manually if pytest not available
    test = TestEmailValidation()
    
    print("Testing authorized iCloud emails...")
    test.test_authorized_icloud_emails()
    print("✅ Passed")
    
    print("Testing authorized Gmail emails...")
    test.test_authorized_gmail_emails()
    print("✅ Passed")
    
    print("Testing authorized institutional emails...")
    test.test_authorized_institutional_emails()
    print("✅ Passed")
    
    print("Testing other authorized emails...")
    test.test_other_authorized_emails()
    print("✅ Passed")
    
    print("Testing valid email formats...")
    test.test_valid_email_formats()
    print("✅ Passed")
    
    print("Testing invalid email formats...")
    test.test_invalid_email_formats()
    print("✅ Passed")
    
    print("Testing all default authorized emails...")
    test.test_all_default_authorized_emails()
    print("✅ Passed")
    
    print("\n✅ All email validation tests passed!")
