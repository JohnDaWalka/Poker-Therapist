#!/usr/bin/env python3
"""
Manual Test: Authentication Configuration End-to-End

This script demonstrates how to manually test the authentication configuration
after setting up credentials. It provides step-by-step instructions for
verifying each authentication provider works correctly.

Usage:
    python tests/manual/test_auth_e2e.py

Prerequisites:
    - .env.local file configured with credentials
    - Backend dependencies installed
    - Backend server NOT running (tests will use direct API calls)
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from dotenv import load_dotenv
    load_dotenv(".env.local")
except ImportError:
    print("ERROR: python-dotenv not installed")
    sys.exit(1)


def test_microsoft_auth():
    """Test Microsoft Azure AD authentication."""
    print("\n" + "=" * 70)
    print("TEST: Microsoft Azure AD Authentication")
    print("=" * 70)
    
    try:
        from auth.microsoft_auth import MicrosoftAuthProvider
        
        provider = MicrosoftAuthProvider()
        print("✓ Microsoft auth provider initialized")
        
        # Generate authorization URL
        redirect_uri = "http://localhost:8501/auth/callback"
        state = "test-state-123"
        auth_url = provider.get_authorization_url(redirect_uri, state)
        
        print(f"✓ Authorization URL generated")
        print(f"\nTo test manually:")
        print(f"1. Open this URL in your browser:")
        print(f"   {auth_url}")
        print(f"2. Sign in with your Microsoft account")
        print(f"3. You'll be redirected with an authorization code")
        print(f"4. Copy the 'code' parameter from the redirect URL")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_google_auth():
    """Test Google OAuth 2.0 authentication."""
    print("\n" + "=" * 70)
    print("TEST: Google OAuth 2.0 Authentication")
    print("=" * 70)
    
    try:
        from auth.google_auth import GoogleAuthProvider
        
        provider = GoogleAuthProvider()
        print("✓ Google auth provider initialized")
        
        # Generate authorization URL
        redirect_uri = "http://localhost:8501/google/callback"
        state = "test-state-456"
        auth_url = provider.get_authorization_url(redirect_uri, state)
        
        print(f"✓ Authorization URL generated")
        print(f"\nTo test manually:")
        print(f"1. Open this URL in your browser:")
        print(f"   {auth_url}")
        print(f"2. Sign in with your Google account")
        print(f"3. Grant permissions for the requested scopes")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def main():
    """Run all manual tests."""
    print("=" * 70)
    print("Authentication Configuration End-to-End Manual Test")
    print("=" * 70)
    print("\nThis script tests the authentication configuration.")
    
    # Run all tests
    results = {
        "Microsoft Authentication": test_microsoft_auth(),
        "Google Authentication": test_google_auth(),
    }
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
