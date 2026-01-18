#!/usr/bin/env python3
"""
Manual test script to verify email authentication logic
Tests the same email validation and authorization used in chatbot_app.py
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Import shared email authentication utilities
from python_src.utils.email_auth import (
    validate_email,
    load_authorized_emails,
    get_emails_by_provider,
)


def test_authentication():
    """Test authentication flow for all authorized emails"""
    
    print("=" * 70)
    print("Poker Therapist - Email Authentication Test")
    print("=" * 70)
    
    authorized_emails = load_authorized_emails()
    
    print(f"\nLoaded {len(authorized_emails)} authorized emails:")
    print("-" * 70)
    
    # Get emails grouped by provider
    emails_by_provider = get_emails_by_provider()
    
    if emails_by_provider['icloud']:
        print("\n📱 Apple iCloud accounts:")
        for email in emails_by_provider['icloud']:
            print(f"   - {email}")
    
    if emails_by_provider['gmail']:
        print("\n✉️  Google Gmail accounts:")
        for email in emails_by_provider['gmail']:
            print(f"   - {email}")
    
    if emails_by_provider['institutional']:
        print("\n🏫 Institutional Microsoft accounts:")
        for email in emails_by_provider['institutional']:
            print(f"   - {email}")
    
    if emails_by_provider['other']:
        print("\n📧 Other email providers:")
        for email in emails_by_provider['other']:
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
    emails_by_provider = get_emails_by_provider()
    print(f"   - Apple iCloud accounts: {len(emails_by_provider['icloud'])}")
    print(f"   - Google Gmail accounts: {len(emails_by_provider['gmail'])}")
    print(f"   - Institutional accounts: {len(emails_by_provider['institutional'])}")
    print(f"   - Other providers: {len(emails_by_provider['other'])}")
    
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
