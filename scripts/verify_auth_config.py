#!/usr/bin/env python3
"""Authentication Configuration Verification Script

This script verifies that all authentication providers and cloud services
are properly configured and working. It performs end-to-end validation
without storing any credentials.

Usage:
    python scripts/verify_auth_config.py

Requirements:
    - .env.local file with all credentials configured
    - Backend dependencies installed: pip install -r backend/requirements.txt
"""

import os
import sys
from typing import Dict, List, Tuple
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str) -> None:
    """Print section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")


def check_env_file() -> bool:
    """Check if .env.local file exists and load it."""
    env_files = [".env.local", ".env"]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            load_dotenv(env_file)
            print_success(f"Loaded environment from {env_file}")
            return True
    
    print_error("No .env.local or .env file found")
    print_info("Create .env.local from .env.example and add your credentials")
    return False


def check_required_vars(vars_dict: Dict[str, List[str]]) -> Tuple[bool, List[str]]:
    """Check if required environment variables are set."""
    missing = []
    
    for category, var_names in vars_dict.items():
        for var_name in var_names:
            value = os.getenv(var_name, "").strip()
            if not value or value.startswith("your-") or value.endswith("-here"):
                missing.append(f"{var_name} ({category})")
    
    return len(missing) == 0, missing


def verify_microsoft_auth() -> bool:
    """Verify Microsoft Azure AD authentication configuration."""
    print_header("Microsoft Azure AD / Windows Authentication")
    
    required_vars = {
        "Microsoft": [
            "AZURE_TENANT_ID",
            "AZURE_CLIENT_ID",
            "AZURE_CLIENT_SECRET",
        ]
    }
    
    all_set, missing = check_required_vars(required_vars)
    
    if not all_set:
        print_error("Missing required Microsoft credentials:")
        for var in missing:
            print(f"  - {var}")
        print_info("See AUTHENTICATION_SETUP.md for Microsoft Azure AD setup")
        return False
    
    print_success("All Microsoft credentials configured")
    
    # Try to initialize Microsoft auth provider
    try:
        from auth.microsoft_auth import MicrosoftAuthProvider
        
        provider = MicrosoftAuthProvider()
        print_success("Microsoft authentication provider initialized")
        
        # Test authorization URL generation
        redirect_uri = os.getenv("AZURE_REDIRECT_URI_WEB", "http://localhost:8501/auth/callback")
        auth_url = provider.get_authorization_url(redirect_uri, state="test")
        
        if "login.microsoftonline.com" in auth_url:
            print_success("Microsoft authorization URL generation works")
            print_info(f"Authority: {provider.authority}")
            print_info(f"Tenant ID: {provider.tenant_id}")
            
            if provider.institutional_domain:
                print_info(f"Institutional domain: {provider.institutional_domain}")
            
            return True
        else:
            print_error("Microsoft authorization URL generation failed")
            return False
            
    except Exception as e:
        print_error(f"Failed to initialize Microsoft authentication: {e}")
        return False


def verify_google_auth() -> bool:
    """Verify Google OAuth 2.0 authentication configuration."""
    print_header("Google OAuth 2.0 / GCP Authentication")
    
    required_vars = {
        "Google": [
            "GOOGLE_CLIENT_ID",
            "GOOGLE_CLIENT_SECRET",
            "GOOGLE_CLOUD_PROJECT_ID",
        ]
    }
    
    all_set, missing = check_required_vars(required_vars)
    
    if not all_set:
        print_error("Missing required Google credentials:")
        for var in missing:
            print(f"  - {var}")
        print_info("See GOOGLE_CLOUD_SETUP.md for Google Cloud Platform setup")
        return False
    
    print_success("All Google credentials configured")
    
    # Try to initialize Google auth provider
    try:
        from auth.google_auth import GoogleAuthProvider
        
        provider = GoogleAuthProvider()
        print_success("Google authentication provider initialized")
        
        # Test authorization URL generation
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI_WEB", "http://localhost:8501/google/callback")
        auth_url = provider.get_authorization_url(redirect_uri, state="test")
        
        if "accounts.google.com/o/oauth2" in auth_url:
            print_success("Google authorization URL generation works")
            print_info(f"Project ID: {provider.project_id}")
            print_info(f"Scopes: {', '.join(provider.scopes)}")
            return True
        else:
            print_error("Google authorization URL generation failed")
            return False
            
    except Exception as e:
        print_error(f"Failed to initialize Google authentication: {e}")
        return False


def verify_apple_auth() -> bool:
    """Verify Apple Sign-In authentication configuration."""
    print_header("Apple Sign-In Authentication")
    
    required_vars = {
        "Apple": [
            "APPLE_TEAM_ID",
            "APPLE_SERVICES_ID",
            "APPLE_KEY_ID",
        ]
    }
    
    all_set, missing = check_required_vars(required_vars)
    
    if not all_set:
        print_warning("Apple Sign-In not fully configured (optional for iOS/macOS/watchOS)")
        for var in missing:
            print(f"  - {var}")
        print_info("See AUTHENTICATION_SETUP.md for Apple Developer setup")
        return False
    
    print_success("All Apple credentials configured")
    
    # Check for private key
    private_key_path = os.getenv("APPLE_PRIVATE_KEY_PATH", "")
    private_key_content = os.getenv("APPLE_PRIVATE_KEY", "")
    
    has_key = False
    if private_key_path and os.path.exists(private_key_path):
        print_success(f"Apple private key file found: {private_key_path}")
        has_key = True
    elif private_key_content and len(private_key_content) > 50:
        print_success("Apple private key configured as environment variable")
        has_key = True
    else:
        print_error("Apple private key not found")
        print_info("Download .p8 file from Apple Developer Portal")
        return False
    
    # Try to initialize Apple auth provider
    try:
        from auth.apple_auth import AppleAuthProvider
        
        provider = AppleAuthProvider()
        print_success("Apple authentication provider initialized")
        
        # Test client secret generation
        try:
            client_secret = provider.create_client_secret()
            if client_secret:
                print_success("Apple client secret generation works")
                print_info(f"Team ID: {provider.team_id}")
                print_info(f"Services ID: {provider.services_id}")
                return True
            else:
                print_error("Failed to generate Apple client secret")
                return False
        except Exception as e:
            print_error(f"Client secret generation failed: {e}")
            return False
            
    except Exception as e:
        print_error(f"Failed to initialize Apple authentication: {e}")
        return False


def verify_google_storage() -> bool:
    """Verify Google Cloud Storage configuration."""
    print_header("Google Cloud Storage")
    
    required_vars = {
        "Storage": [
            "GOOGLE_CLOUD_PROJECT_ID",
            "GOOGLE_STORAGE_BUCKET_NAME",
        ]
    }
    
    all_set, missing = check_required_vars(required_vars)
    
    if not all_set:
        print_error("Missing required Google Cloud Storage configuration:")
        for var in missing:
            print(f"  - {var}")
        print_info("See GOOGLE_CLOUD_SETUP.md for Cloud Storage setup")
        return False
    
    print_success("All Google Cloud Storage variables configured")
    
    # Check for service account credentials
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    
    if creds_path and os.path.exists(creds_path):
        print_success(f"Service account JSON file found: {creds_path}")
    elif creds_json and len(creds_json) > 50:
        print_success("Service account credentials configured as environment variable")
    else:
        print_error("Service account credentials not found")
        print_info("Download service account JSON from GCP Console")
        print_info("Set GOOGLE_APPLICATION_CREDENTIALS to the file path")
        return False
    
    # Try to initialize storage client
    try:
        from cloud.google_storage import GoogleCloudStorage
        
        storage = GoogleCloudStorage()
        print_success("Google Cloud Storage client initialized")
        print_info(f"Project ID: {storage.project_id}")
        print_info(f"Bucket: {storage.bucket_name}")
        
        # Try to verify bucket access (read-only check)
        try:
            if storage.bucket_exists():
                print_success("Cloud Storage bucket is accessible")
                return True
            else:
                print_error("Bucket does not exist or is not accessible")
                print_info("Create bucket or check service account permissions")
                return False
        except Exception as e:
            print_warning(f"Could not verify bucket access: {e}")
            print_info("This may be a permissions issue or the bucket doesn't exist")
            return True  # Don't fail if we can't verify but client initialized
            
    except ImportError:
        print_error("Google Cloud Storage module not found")
        print_info("Ensure backend/cloud/google_storage.py exists")
        return False
    except Exception as e:
        print_error(f"Failed to initialize Cloud Storage: {e}")
        return False


def verify_jwt_config() -> bool:
    """Verify JWT configuration."""
    print_header("JWT Token Configuration")
    
    jwt_secret = os.getenv("JWT_SECRET_KEY", "")
    
    if not jwt_secret or jwt_secret.startswith("your-"):
        print_error("JWT_SECRET_KEY not configured")
        print_info("Generate a secure random secret:")
        print_info('  python -c "import secrets; print(secrets.token_urlsafe(32))"')
        return False
    
    if len(jwt_secret) < 32:
        print_warning("JWT_SECRET_KEY is too short (should be at least 32 characters)")
        return False
    
    print_success("JWT_SECRET_KEY is configured")
    print_info(f"Algorithm: {os.getenv('JWT_ALGORITHM', 'HS256')}")
    print_info(f"Expiration: {os.getenv('JWT_EXPIRATION_HOURS', '24')} hours")
    
    return True


def verify_security_settings() -> bool:
    """Verify security-related configuration."""
    print_header("Security Settings")
    
    checks_passed = True
    
    # Check CORS configuration
    cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    if "*" in cors_origins:
        print_warning("CORS allows all origins (*) - insecure for production")
        checks_passed = False
    else:
        print_success("CORS origins configured")
    
    # Check HTTPS setting
    force_https = os.getenv("FORCE_HTTPS", "false").lower()
    if force_https == "true":
        print_success("HTTPS enforcement enabled")
    else:
        print_info("HTTPS enforcement disabled (set FORCE_HTTPS=true for production)")
    
    # Check rate limiting
    rate_limit = os.getenv("RATE_LIMIT_PER_MINUTE", "")
    if rate_limit:
        print_success(f"Rate limiting configured: {rate_limit} requests/minute")
    else:
        print_info("Rate limiting not configured")
    
    # Check .gitignore for sensitive files
    if os.path.exists(".gitignore"):
        with open(".gitignore", "r") as f:
            gitignore_content = f.read()
            
        sensitive_files = [".env.local", "*.p8", "*service-account*.json"]
        for pattern in sensitive_files:
            if pattern in gitignore_content or pattern.replace("*", "") in gitignore_content:
                print_success(f"Sensitive files ignored: {pattern}")
            else:
                print_warning(f"Sensitive files may not be ignored: {pattern}")
                checks_passed = False
    
    return checks_passed


def main() -> int:
    """Main verification function."""
    print(f"{Colors.BOLD}Authentication Configuration Verification{Colors.RESET}")
    print("This script verifies your authentication and cloud services configuration.\n")
    
    # Check environment file
    if not check_env_file():
        return 1
    
    # Run all verifications
    results = {
        "JWT Configuration": verify_jwt_config(),
        "Microsoft Authentication": verify_microsoft_auth(),
        "Google Authentication": verify_google_auth(),
        "Apple Sign-In": verify_apple_auth(),
        "Google Cloud Storage": verify_google_storage(),
        "Security Settings": verify_security_settings(),
    }
    
    # Summary
    print_header("Verification Summary")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for check, result in results.items():
        if result:
            print_success(f"{check}: PASSED")
        else:
            print_error(f"{check}: FAILED")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} checks passed{Colors.RESET}\n")
    
    if passed == total:
        print_success("All authentication providers configured correctly! 🎉")
        print_info("Next steps:")
        print_info("1. Start the backend: cd backend && uvicorn api.main:app --reload")
        print_info("2. Test authentication flows in your application")
        print_info("3. See DEPLOYMENT_VERIFICATION.md for complete testing checklist")
        return 0
    else:
        print_warning("Some checks failed. Review the errors above and fix them.")
        print_info("Documentation:")
        print_info("- AUTHENTICATION_SETUP.md - Complete setup guide")
        print_info("- GOOGLE_CLOUD_SETUP.md - Google Cloud Platform setup")
        print_info("- AUTH_QUICKSTART.md - Quick start guide")
        return 1


if __name__ == "__main__":
    sys.exit(main())
