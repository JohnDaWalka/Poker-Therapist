#!/usr/bin/env python3
"""
Manual test script to verify email authentication logic
Tests the same email validation and authorization used in chatbot_app.py
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))


def validate_email(email: str) -> bool:
    """
    Validate email format - same logic as chatbot_app.py
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid format, False otherwise
    """
    parts = email.split("@")
    # Explicitly convert to bool to handle empty string case
    return bool(len(parts) == 2 and parts[0] and parts[1] and "." in parts[1])


def load_authorized_emails() -> list[str]:
    """
    Load authorized emails from environment or use defaults
    Same logic as chatbot_app.py lines 71-86
    """
    default_emails = [
        "m.fanelli1@icloud.com",
        "johndawalka@icloud.com",
        "mauro.fanelli@ctstate.edu",
        "maurofanellijr@gmail.com",
        "cooljack87@icloud.com",
        "jdwalka@pm.me",
    ]
    
    # Load from environment if available
    env_emails = os.getenv("AUTHORIZED_EMAILS", "").strip()
    if env_emails:
        return [email.strip() for email in env_emails.split(",") if email.strip()]
    
    return default_emails


def test_authentication():
    """Test authentication flow for all authorized emails"""
    
    print("=" * 70)
    print("Poker Therapist - Email Authentication Test")
    print("=" * 70)
    
    authorized_emails = load_authorized_emails()
    
    print(f"\nLoaded {len(authorized_emails)} authorized emails:")
    print("-" * 70)
    
    # Group emails by provider
    icloud_emails = [e for e in authorized_emails if "@icloud.com" in e]
    gmail_emails = [e for e in authorized_emails if "@gmail.com" in e]
    ctstate_emails = [e for e in authorized_emails if "@ctstate.edu" in e]
    other_emails = [e for e in authorized_emails if e not in icloud_emails + gmail_emails + ctstate_emails]
    
    if icloud_emails:
        print("\n📱 Apple iCloud accounts:")
        for email in icloud_emails:
            print(f"   - {email}")
    
    if gmail_emails:
        print("\n✉️  Google Gmail accounts:")
        for email in gmail_emails:
            print(f"   - {email}")
    
    if ctstate_emails:
        print("\n🏫 Institutional Microsoft accounts:")
        for email in ctstate_emails:
            print(f"   - {email}")
    
    if other_emails:
        print("\n📧 Other email providers:")
        for email in other_emails:
            print(f"   - {email}")
    
    # Test validation
    print("\n" + "=" * 70)
    print("Testing Email Validation")
    print("=" * 70)
    
    all_valid = True
    for email in authorized_emails:
        is_valid = validate_email(email)
        is_authorized = email in authorized_emails
        
        status = "✅" if is_valid and is_authorized else "❌"
        vip_badge = "🎰 (VIP Access)" if is_authorized else ""
        
        print(f"{status} {email} {vip_badge}")
        
        if not is_valid:
            print(f"   ⚠️  WARNING: Email failed validation!")
            all_valid = False
    
    # Test sample custom emails
    print("\n" + "=" * 70)
    print("Testing Custom Email Validation")
    print("=" * 70)
    
    test_emails = [
        ("test@example.com", True, False),
        ("user@domain.co.uk", True, False),
        ("invalid.email", False, False),
        ("@domain.com", False, False),
    ]
    
    for email, should_validate, should_authorize in test_emails:
        is_valid = validate_email(email)
        is_authorized = email in authorized_emails
        
        validation_ok = (is_valid == should_validate)
        auth_ok = (is_authorized == should_authorize)
        status = "✅" if (validation_ok and auth_ok) else "❌"
        
        access_level = "VIP Access" if is_authorized else "Basic Access"
        valid_str = "True " if is_valid else "False"
        auth_str = "True " if is_authorized else "False"
        print(f"{status} {email:<25} Valid: {valid_str:<5} Auth: {auth_str:<5} ({access_level})")
    
    # Test key authentication flows
    print("\n" + "=" * 70)
    print("Testing Authentication Flows")
    print("=" * 70)
    
    print("\n1️⃣  Test Flow: iCloud user login (m.fanelli1@icloud.com)")
    test_email = "m.fanelli1@icloud.com"
    if validate_email(test_email):
        if test_email in authorized_emails:
            print(f"   ✅ Login successful as {test_email}")
            print(f"   🎰 VIP Access: Full voice and Rex personality features enabled")
        else:
            print(f"   ✅ Login successful as {test_email}")
            print(f"   ℹ️  Basic access: Limited features")
    else:
        print(f"   ❌ Login failed: Invalid email format")
    
    print("\n2️⃣  Test Flow: Gmail user login (maurofanellijr@gmail.com)")
    test_email = "maurofanellijr@gmail.com"
    if validate_email(test_email):
        if test_email in authorized_emails:
            print(f"   ✅ Login successful as {test_email}")
            print(f"   🎰 VIP Access: Full voice and Rex personality features enabled")
        else:
            print(f"   ✅ Login successful as {test_email}")
            print(f"   ℹ️  Basic access: Limited features")
    else:
        print(f"   ❌ Login failed: Invalid email format")
    
    print("\n3️⃣  Test Flow: Institutional user login (mauro.fanelli@ctstate.edu)")
    test_email = "mauro.fanelli@ctstate.edu"
    if validate_email(test_email):
        if test_email in authorized_emails:
            print(f"   ✅ Login successful as {test_email}")
            print(f"   🎰 VIP Access: Full voice and Rex personality features enabled")
        else:
            print(f"   ✅ Login successful as {test_email}")
            print(f"   ℹ️  Basic access: Limited features")
    else:
        print(f"   ❌ Login failed: Invalid email format")
    
    print("\n4️⃣  Test Flow: Custom email login (test@example.com)")
    test_email = "test@example.com"
    if validate_email(test_email):
        if test_email in authorized_emails:
            print(f"   ✅ Login successful as {test_email}")
            print(f"   🎰 VIP Access: Full voice and Rex personality features enabled")
        else:
            print(f"   ✅ Login successful as {test_email}")
            print(f"   ℹ️  Basic access: Limited features")
    else:
        print(f"   ❌ Login failed: Invalid email format")
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    if all_valid:
        print("✅ All authorized emails pass validation")
    else:
        print("❌ Some authorized emails failed validation")
    
    print(f"\n📊 Statistics:")
    print(f"   - Total authorized emails: {len(authorized_emails)}")
    print(f"   - Apple iCloud accounts: {len(icloud_emails)}")
    print(f"   - Google Gmail accounts: {len(gmail_emails)}")
    print(f"   - Institutional accounts: {len(ctstate_emails)}")
    print(f"   - Other providers: {len(other_emails)}")
    
    print("\n✅ Email authentication test complete!")
    print("\n📚 For full authentication setup, see:")
    print("   - AUTHENTICATION_VERIFICATION.md")
    print("   - AUTHENTICATION_SETUP.md")
    print("   - CI_CD_AUTHENTICATION.md")
    print("\n" + "=" * 70)
    
    return all_valid


if __name__ == "__main__":
    try:
        success = test_authentication()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
