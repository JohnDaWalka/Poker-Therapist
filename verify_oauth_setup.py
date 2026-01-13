#!/usr/bin/env python3
"""
OAuth Authentication Verification Script

This script tests the OAuth authentication implementation to ensure it's working correctly.
Run this after setting up OAuth providers to verify the configuration.

Usage:
    python verify_oauth_setup.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from python_src.services.auth_service import AuthenticationService, AuthConfig, UserInfo
import secrets


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def print_success(text: str):
    """Print success message."""
    print(f"✅ {text}")


def print_warning(text: str):
    """Print warning message."""
    print(f"⚠️  {text}")


def print_error(text: str):
    """Print error message."""
    print(f"❌ {text}")


def test_imports():
    """Test that all required modules can be imported."""
    print_header("Testing Imports")
    
    try:
        from python_src.services.auth_service import (
            AuthenticationService,
            AuthConfig,
            UserInfo,
            MicrosoftAuthService,
            GoogleAuthService,
            AppleAuthService,
        )
        print_success("auth_service module imports successfully")
        return True
    except ImportError as e:
        print_error(f"Failed to import auth_service: {e}")
        return False


def test_config():
    """Test configuration loading."""
    print_header("Testing Configuration")
    
    try:
        config = AuthConfig.from_env()
        print_success("AuthConfig loaded from environment")
        
        if config.jwt_secret:
            print_success(f"JWT secret configured (length: {len(config.jwt_secret)})")
        else:
            print_warning("JWT secret not configured - using auto-generated secret")
            config.jwt_secret = secrets.token_urlsafe(32)
        
        print_success(f"JWT algorithm: {config.jwt_algorithm}")
        print_success(f"Session timeout: {config.session_timeout_minutes} minutes")
        
        return config
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        return None


def test_providers(config: AuthConfig):
    """Test OAuth provider configuration."""
    print_header("Testing OAuth Providers")
    
    auth = AuthenticationService(config)
    providers = auth.get_available_providers()
    
    if providers:
        print_success(f"Available providers: {', '.join(providers)}")
    else:
        print_warning("No OAuth providers configured")
        print("         To configure providers, set environment variables:")
        print("         - Microsoft: MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET")
        print("         - Google: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET")
        print("         - Apple: APPLE_CLIENT_ID, APPLE_TEAM_ID, APPLE_KEY_ID")
    
    # Test Microsoft
    if auth.microsoft:
        print_success("Microsoft OAuth configured")
        try:
            url, state = auth.microsoft.get_authorization_url()
            print_success(f"  - Authorization URL generated (length: {len(url)})")
            print_success(f"  - State token: {state[:20]}...")
        except Exception as e:
            print_error(f"  - Failed to generate auth URL: {e}")
    else:
        print_warning("Microsoft OAuth not configured")
    
    # Test Google
    if auth.google:
        print_success("Google OAuth configured")
        try:
            url, state = auth.google.get_authorization_url()
            print_success(f"  - Authorization URL generated (length: {len(url)})")
            print_success(f"  - State token: {state[:20]}...")
        except Exception as e:
            print_error(f"  - Failed to generate auth URL: {e}")
    else:
        print_warning("Google OAuth not configured")
    
    # Test Apple
    if auth.apple:
        print_success("Apple Sign In configured")
        try:
            url, state = auth.apple.get_authorization_url()
            print_success(f"  - Authorization URL generated (length: {len(url)})")
            print_success(f"  - State token: {state[:20]}...")
        except Exception as e:
            print_error(f"  - Failed to generate auth URL: {e}")
    else:
        print_warning("Apple Sign In not configured")
    
    return auth, len(providers) > 0


def test_jwt_tokens(auth: AuthenticationService):
    """Test JWT token generation and verification."""
    print_header("Testing JWT Token Operations")
    
    # Create test user
    user = UserInfo(
        provider='test',
        email='test@example.com',
        name='Test User',
        user_id='12345'
    )
    print_success(f"Test user created: {user.email}")
    
    # Generate token
    try:
        token = auth.create_session_token(user)
        print_success(f"JWT token generated: {token[:40]}...")
    except Exception as e:
        print_error(f"Failed to generate token: {e}")
        return False
    
    # Verify token
    try:
        payload = auth.verify_session_token(token)
        if payload:
            print_success("Token verified successfully!")
            print_success(f"  - Email: {payload['email']}")
            print_success(f"  - Provider: {payload['provider']}")
            print_success(f"  - Name: {payload.get('name', 'N/A')}")
            print_success(f"  - User ID: {payload.get('user_id', 'N/A')}")
            return True
        else:
            print_error("Token verification returned None")
            return False
    except Exception as e:
        print_error(f"Failed to verify token: {e}")
        return False


def test_invalid_token(auth: AuthenticationService):
    """Test handling of invalid tokens."""
    print_header("Testing Invalid Token Handling")
    
    try:
        payload = auth.verify_session_token("invalid_token_xyz_123")
        if payload is None:
            print_success("Invalid token correctly rejected (returned None)")
            return True
        else:
            print_error("Invalid token was accepted (security issue!)")
            return False
    except Exception as e:
        print_success(f"Invalid token correctly rejected with exception: {type(e).__name__}")
        return True


def print_summary(results: dict):
    """Print test summary."""
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, test_passed in results.items():
        if test_passed:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print("\n" + "-" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("All tests passed!")
        print("\n📚 Next steps:")
        print("   1. Configure OAuth providers (see OAUTH_QUICKSTART.md)")
        print("   2. Test authentication in Streamlit app: streamlit run chatbot_app.py")
        print("   3. Test backend API: cd backend && uvicorn api.main:app --reload")
        return True
    else:
        print_warning(f"{total - passed} test(s) did not pass (may be expected)")
        print("\n📚 See documentation:")
        print("   - OAUTH_SETUP.md for detailed setup instructions")
        print("   - OAUTH_QUICKSTART.md for quick start guide")
        print("   - OAUTH_TESTING.md for testing procedures")
        
        # If only provider configuration failed, that's expected in unconfigured environment
        if passed >= total - 1 and not results.get("Provider configuration", True):
            print("\n✅ Core functionality tests passed!")
            print("⚠️  OAuth providers not configured (expected for initial setup)")
            return True
        
        return False


def main():
    """Run all verification tests."""
    print_header("OAuth Authentication Verification")
    print("This script verifies the OAuth authentication implementation.")
    print("Version: 1.0.0")
    
    results = {}
    
    # Test imports
    if not test_imports():
        print_error("Import test failed. Cannot continue.")
        sys.exit(1)
    results["Import test"] = True
    
    # Test configuration
    config = test_config()
    if not config:
        print_error("Configuration test failed. Cannot continue.")
        sys.exit(1)
    results["Configuration test"] = True
    
    # Test providers
    auth, providers_configured = test_providers(config)
    results["Provider configuration"] = providers_configured
    
    # Test JWT tokens
    jwt_test_passed = test_jwt_tokens(auth)
    results["JWT token generation"] = jwt_test_passed
    
    # Test invalid token
    invalid_token_test_passed = test_invalid_token(auth)
    results["Invalid token handling"] = invalid_token_test_passed
    
    # Print summary
    all_passed = print_summary(results)
    
    if all_passed:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
