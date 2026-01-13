# Authentication Setup Guide

This guide provides step-by-step instructions for configuring authentication and identity providers for the Poker Therapist application in accordance with institutional security policies.

## Table of Contents
1. [Overview](#overview)
2. [Microsoft Windows Account / Azure AD](#microsoft-windows-account--azure-ad)
3. [Institutional SSO Configuration](#institutional-sso-configuration)
4. [Google Cloud Platform OAuth 2.0](#google-cloud-platform-oauth-20)
5. [Additional Identity Providers](#additional-identity-providers)
6. [Security Best Practices](#security-best-practices)
7. [Testing & Verification](#testing--verification)

## Overview

The Poker Therapist application supports multiple authentication mechanisms:
- **Microsoft Azure AD** - For organization-managed Windows accounts
- **Institutional SSO** - For .edu and enterprise accounts (e.g., ctstate.edu)
- **Google OAuth 2.0/OpenID Connect** - For GCP API integration
- **Apple Sign In** - For iOS/macOS users
- **Additional OAuth Providers** - GitHub, custom OAuth 2.0 providers

**⚠️ SECURITY NOTICE**: Never commit credentials, secrets, or API keys to source control. Always use environment variables and secure secrets management systems.

## Microsoft Windows Account / Azure AD

### Prerequisites
- Active Microsoft Azure subscription
- Organization Azure AD tenant access
- Permission to register applications in Azure AD

### Step 1: Register Application in Azure AD

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Go to **Azure Active Directory** > **App registrations** > **New registration**
3. Configure the application:
   - **Name**: Poker Therapist
   - **Supported account types**: 
     - Select "Accounts in this organizational directory only" for single-tenant
     - Or "Accounts in any organizational directory" for multi-tenant
   - **Redirect URI**: 
     - Platform: Web
     - URI: `http://localhost:8000/auth/callback/microsoft`
     - For production: `https://your-domain.com/auth/callback/microsoft`

4. Click **Register**

### Step 2: Configure Authentication

After registration:

1. Note your **Application (client) ID** and **Directory (tenant) ID**
2. Go to **Certificates & secrets** > **New client secret**
   - Description: "Poker Therapist Production"
   - Expires: Choose appropriate duration (recommended: 12-24 months)
   - **IMPORTANT**: Copy the secret value immediately (it won't be shown again)

3. Go to **API permissions** > **Add a permission**
   - Microsoft Graph > Delegated permissions
   - Add: `User.Read`, `email`, `profile`, `openid`
   - Click **Grant admin consent** (if you have permissions)

4. Go to **Authentication**
   - Enable "ID tokens" under Implicit grant and hybrid flows
   - Configure logout URL: `http://localhost:8000/auth/logout`

### Step 3: Update Environment Configuration

Update your `.env.local` file (never commit this file):

```bash
# Azure AD Configuration
AZURE_AD_TENANT_ID=your-actual-tenant-id-or-domain.onmicrosoft.com
AZURE_AD_CLIENT_ID=your-actual-client-id
AZURE_AD_CLIENT_SECRET=your-actual-client-secret
AZURE_AD_REDIRECT_URI=http://localhost:8000/auth/callback/microsoft
```

### Step 4: Verify Azure AD Integration

```bash
# Test authentication flow
python -c "
from msal import ConfidentialClientApplication
import os

app = ConfidentialClientApplication(
    os.getenv('AZURE_AD_CLIENT_ID'),
    authority=f'https://login.microsoftonline.com/{os.getenv(\"AZURE_AD_TENANT_ID\")}',
    client_credential=os.getenv('AZURE_AD_CLIENT_SECRET')
)
print('Azure AD configuration valid!' if app else 'Configuration failed!')
"
```

## Institutional SSO Configuration

### For Connecticut State University (ctstate.edu) or Similar Institutions

### Step 1: Coordinate with IT Department

Contact your institutional IT/security team:
- Request SSO integration for the application
- Provide them with:
  - Application name: Poker Therapist
  - Redirect/Callback URL: `https://your-domain.com/auth/callback/sso`
  - Required user attributes: email, name, institutional_id

### Step 2: Choose SSO Protocol

Most institutions support one of:
- **SAML 2.0** (most common for .edu institutions)
- **OAuth 2.0 / OpenID Connect**
- **Shibboleth** (common in higher education)

### Step 3: Configure SSO Provider

For Azure AD-based institutional SSO (common):

```bash
# SSO Configuration
SSO_PROVIDER=azure
INSTITUTIONAL_DOMAIN=ctstate.edu
SSO_METADATA_URL=https://login.microsoftonline.com/YOUR_TENANT/federationmetadata/2007-06/federationmetadata.xml

# Use the same Azure AD settings as above with institutional tenant
AZURE_AD_TENANT_ID=ctstate.onmicrosoft.com
```

For SAML 2.0 SSO:

```bash
SSO_PROVIDER=saml
INSTITUTIONAL_DOMAIN=ctstate.edu
SAML_IDP_METADATA_URL=https://sso.ctstate.edu/metadata
SAML_SP_ENTITY_ID=https://your-app.com/auth/saml/metadata
SAML_SP_ACS_URL=https://your-app.com/auth/saml/acs
```

### Step 4: Email Domain Validation

Update `AUTHORIZED_EMAILS` to include institutional domain pattern:

```bash
# Allow all users from institutional domain
AUTHORIZED_EMAIL_DOMAINS=ctstate.edu,yale.edu

# Or specific authorized emails
AUTHORIZED_EMAILS=user1@ctstate.edu,user2@ctstate.edu
```

## Google Cloud Platform OAuth 2.0

### For Accessing GCP APIs and Services

### Step 1: Create GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing: "Poker Therapist"
3. Enable required APIs:
   - Google+ API (for user profile)
   - Any additional APIs you need (Cloud Storage, etc.)

### Step 2: Configure OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Choose user type:
   - **Internal**: For Google Workspace users only
   - **External**: For any Google account (requires verification if requesting sensitive scopes)
3. Fill in application information:
   - App name: Poker Therapist
   - User support email: your-email@domain.com
   - Developer contact: your-email@domain.com
   - Authorized domains: your-domain.com
4. Add scopes:
   - `openid`
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`
   - Add any additional API scopes needed

### Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. Application type: **Web application**
4. Configure:
   - Name: Poker Therapist Web Client
   - Authorized JavaScript origins:
     - `http://localhost:8000`
     - `https://your-production-domain.com`
   - Authorized redirect URIs:
     - `http://localhost:8000/auth/callback/google`
     - `https://your-production-domain.com/auth/callback/google`
5. Click **Create**
6. **Download the JSON** credentials file or copy Client ID and Secret

### Step 4: Configure Environment

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback/google
GOOGLE_OAUTH_SCOPES=openid email profile

# For GCP API access (service account)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
GCP_PROJECT_ID=your-gcp-project-id
```

### Step 5: Service Account (for Server-to-Server)

For automated GCP API access:

1. Go to **IAM & Admin** > **Service Accounts**
2. Create service account: "poker-therapist-backend"
3. Grant necessary roles (e.g., Storage Admin, Cloud Functions Invoker)
4. Create and download JSON key
5. Store securely (never commit to git)

```bash
# Store in environment
export GOOGLE_APPLICATION_CREDENTIALS="/secure/path/to/service-account-key.json"
```

## Additional Identity Providers

### Apple Sign In

### Step 1: Apple Developer Configuration

1. Go to [Apple Developer Portal](https://developer.apple.com/account)
2. **Certificates, Identifiers & Profiles** > **Identifiers**
3. Register an **App ID** (if not exists)
4. Register a **Services ID**:
   - Identifier: `com.pokertherapist.signin`
   - Enable "Sign In with Apple"
   - Configure domains and redirect URLs
5. Create a **Key** for Sign in with Apple:
   - Download the .p8 key file
   - Note the Key ID

### Step 2: Configure Environment

```bash
# Apple Sign In Configuration
APPLE_CLIENT_ID=com.pokertherapist.signin
APPLE_TEAM_ID=YOUR_TEAM_ID
APPLE_KEY_ID=YOUR_KEY_ID
APPLE_PRIVATE_KEY_PATH=/secure/path/to/AuthKey_KEYID.p8
APPLE_REDIRECT_URI=https://your-domain.com/auth/callback/apple
```

### GitHub OAuth (Optional)

1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Create new OAuth App:
   - Application name: Poker Therapist
   - Homepage URL: `https://your-domain.com`
   - Authorization callback URL: `https://your-domain.com/auth/callback/github`
3. Note Client ID and generate Client Secret

```bash
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

## Security Best Practices

### 1. Credential Management

**DO:**
- ✅ Use environment variables for all credentials
- ✅ Store production secrets in secure vaults (Azure Key Vault, AWS Secrets Manager, Google Secret Manager)
- ✅ Rotate credentials regularly (every 3-6 months)
- ✅ Use different credentials for dev/staging/production
- ✅ Implement least privilege access
- ✅ Use `.env.local` for local development (add to `.gitignore`)

**DON'T:**
- ❌ Commit credentials to source control
- ❌ Share credentials via email or messaging
- ❌ Hardcode credentials in application code
- ❌ Use the same credentials across environments
- ❌ Store credentials in log files

### 2. Session Security

```bash
# Generate secure random keys (minimum 32 characters)
# On Linux/Mac:
openssl rand -hex 32

# Session Configuration
SESSION_SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### 3. HTTPS/TLS

- **Required for production**: All authentication flows must use HTTPS
- Obtain SSL/TLS certificates (Let's Encrypt, your institution, or commercial CA)
- Configure HSTS (HTTP Strict Transport Security)

```bash
ENABLE_HSTS=true
HSTS_MAX_AGE=31536000
```

### 4. CORS Configuration

```bash
# Development
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Production (be specific)
CORS_ALLOWED_ORIGINS=https://pokertherapist.com,https://www.pokertherapist.com
```

### 5. Rate Limiting

Protect authentication endpoints from brute force:

```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
AUTH_RATE_LIMIT_PER_MINUTE=5
```

### 6. Audit Logging

Log authentication events (successful and failed attempts):
- User login/logout
- Permission changes
- Failed authentication attempts
- Suspicious activity

```python
# Example logging
import logging

auth_logger = logging.getLogger('auth')
auth_logger.info(f"User {email} authenticated via {provider}")
```

### 7. Multi-Factor Authentication (MFA)

For high-security deployments:
- Enable MFA in Azure AD
- Require MFA for institutional SSO
- Implement TOTP (Time-based One-Time Password) as backup

## Testing & Verification

### Pre-Deployment Checklist

- [ ] All credentials configured in environment variables
- [ ] No credentials committed to source control
- [ ] HTTPS enabled for production
- [ ] CORS properly configured
- [ ] Session secrets are random and secure (32+ characters)
- [ ] Rate limiting enabled
- [ ] Audit logging configured
- [ ] Error messages don't leak sensitive information

### Test Authentication Flows

#### 1. Test Microsoft/Azure AD Authentication

```bash
# Start the application
python chatbot_app.py

# Test login flow:
# 1. Navigate to http://localhost:8000
# 2. Click "Sign in with Microsoft"
# 3. Authenticate with your organizational account
# 4. Verify redirect back to application
# 5. Confirm user email and profile displayed
```

#### 2. Test Institutional SSO

```bash
# Test with institutional email
# 1. Navigate to application
# 2. Enter email: username@ctstate.edu
# 3. Should redirect to institutional SSO
# 4. Authenticate with institutional credentials
# 5. Verify successful authentication and authorization
```

#### 3. Test Google OAuth

```bash
# Test GCP integration
python -c "
from google.oauth2 import service_account
from google.cloud import storage
import os

# Test service account
creds = service_account.Credentials.from_service_account_file(
    os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
)
print('Google credentials loaded successfully!')

# Test OAuth flow manually or via application UI
"
```

#### 4. Test Authorization

```bash
# Verify email-based authorization
# 1. Authenticate with authorized email (from AUTHORIZED_EMAILS)
# 2. Confirm full access to features
# 3. Authenticate with non-authorized email
# 4. Verify restricted access or denial
```

#### 5. Test CI/CD Integration

```bash
# Test GitHub Actions workflow
git push origin main

# Workflow should:
# 1. Checkout code successfully
# 2. Install dependencies with npm ci
# 3. Complete without exposing credentials
# 4. All secrets should be properly masked in logs
```

### Automated Test Script

A comprehensive test script is provided in the repository to verify your authentication configuration:

```bash
# Run the authentication configuration test
./test_auth_config.sh
```

This script will:
- Check for required environment variables
- Validate credential file security
- Verify secret key lengths
- Ensure credentials are not committed to git
- Test .gitignore configuration

Example output:

```
==================================
Authentication Configuration Test
==================================

Checking Authentication Environment Variables...
✅ AZURE_AD_TENANT_ID is configured
✅ GOOGLE_CLIENT_ID is configured
...

Security Checks:
✅ .env.local is not in version control
✅ No credential files found in repository

Test Summary
Passed:   15
Warnings: 2
Errors:   0

✅ All authentication configuration checks passed!
```

For the complete test script source code, see `test_auth_config.sh` in the repository root.

### Monitoring & Debugging

Enable debug logging during testing:

```bash
# Enable debug mode (development only)
DEBUG=true
LOG_LEVEL=DEBUG

# Start application with verbose logging
streamlit run chatbot_app.py --logger.level=debug
```

Check logs for:
- Authentication requests
- Token validation
- API calls
- Errors or exceptions

### Production Deployment

Before deploying to production:

1. **Environment-Specific Configuration**
   ```bash
   # Production environment
   export ENVIRONMENT=production
   export DEBUG=false
   export LOG_LEVEL=INFO
   
   # Use production URLs
   export AZURE_AD_REDIRECT_URI=https://pokertherapist.com/auth/callback/microsoft
   export GOOGLE_REDIRECT_URI=https://pokertherapist.com/auth/callback/google
   ```

2. **Secrets Management**
   - Transfer credentials to production secrets manager
   - Never copy-paste production credentials
   - Use deployment automation to inject secrets

3. **Test in Staging First**
   - Deploy to staging environment with production-like configuration
   - Run full authentication test suite
   - Verify all integrations work end-to-end
   - Load test authentication endpoints

4. **Monitor Production**
   - Set up alerts for authentication failures
   - Monitor rate limiting
   - Track unusual login patterns
   - Regular security audits

## Support & Troubleshooting

### Common Issues

**Issue: "Invalid client" error with Azure AD**
- Verify CLIENT_ID matches Azure portal
- Check TENANT_ID is correct
- Ensure client secret hasn't expired

**Issue: Google OAuth "redirect_uri_mismatch"**
- Verify redirect URI in GCP console exactly matches your config
- Check for trailing slashes
- Ensure protocol (http/https) matches

**Issue: "Unauthorized" with institutional SSO**
- Verify email domain in AUTHORIZED_EMAIL_DOMAINS
- Check SSO metadata URL is accessible
- Confirm with IT that application is registered

**Issue: Credentials not loading**
- Check .env.local file exists and has correct format
- Verify file permissions (should not be world-readable)
- Ensure application loads environment variables correctly

### Getting Help

- **Institutional IT Support**: For SSO and organizational authentication
- **Azure Support**: For Azure AD issues
- **Google Cloud Support**: For GCP/OAuth issues
- **Application Issues**: Create an issue on GitHub repository

## References

- [Microsoft Identity Platform Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Apple Sign In Documentation](https://developer.apple.com/sign-in-with-apple/)
- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [OpenID Connect Specification](https://openid.net/connect/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

**Last Updated**: 2026-01-13  
**Version**: 1.0.0
