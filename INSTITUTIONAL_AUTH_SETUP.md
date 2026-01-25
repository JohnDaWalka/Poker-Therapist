# Institutional Authentication Setup Guide

This guide provides step-by-step instructions for configuring the Poker Therapist application to authenticate using organization-managed accounts, specifically for educational institutions like Connecticut State Community College (ctstate.edu).

## Overview

The Poker Therapist application supports multiple authentication providers with full institutional Single Sign-On (SSO) support:

1. **Microsoft Azure AD** - For Windows/Microsoft organizational accounts
2. **Google OAuth 2.0** - For Google Workspace and GCP integration
3. **Apple Sign-In** - For iOS, macOS, and watchOS applications

## ⚠️ Security Requirements

**CRITICAL**: Follow these security practices:

- ✅ Never commit credentials or secrets to source control
- ✅ Use environment variables or Azure Key Vault / Google Secret Manager
- ✅ Rotate credentials regularly (every 90 days minimum)
- ✅ Use separate credentials for development, staging, and production
- ✅ Enable MFA for all administrative accounts
- ✅ Follow your institution's IT security policies
- ✅ Review and audit access logs regularly

## Prerequisites

Before starting, ensure you have:

1. **Institutional Email Account**: Your organization-managed account (e.g., `user.name@ctstate.edu`)
2. **IT Department Access**: Contact your IT department for:
   - Azure AD tenant access (or ability to create one)
   - Google Workspace admin console access
   - Approval for OAuth applications
3. **Development Environment**: 
   - Python 3.8+ installed
   - Git for version control
   - Access to this repository

## Part 1: Microsoft/Azure AD Authentication (Institutional SSO)

### 1.1 Register Application in Azure AD

**For Connecticut State Community College (ctstate.edu) or similar institutions:**

1. **Contact IT Department**: Request access to your organization's Azure AD tenant
   - Tenant name: Usually `{institution}.onmicrosoft.com`
   - You may need administrative privileges or IT assistance

2. **Navigate to Azure Portal**: https://portal.azure.com
   - Sign in with your institutional account
   - Go to: **Azure Active Directory** → **App registrations** → **New registration**

3. **Configure Application**:
   ```
   Name: Poker Therapist
   Supported account types: 
     - "Accounts in this organizational directory only ({Your Institution} only)"
     - This restricts authentication to your institution's domain
   
   Redirect URIs (Platform: Web):
     Development:
       - http://localhost:8501/api/auth/callback/microsoft
       - http://localhost:8000/api/auth/callback/microsoft
     Production:
       - https://your-production-domain.com/api/auth/callback/microsoft
       - https://poker-therapist.vercel.app/api/auth/callback/microsoft
   ```

4. **Click "Register"**

### 1.2 Gather Credentials

From your newly registered app:

1. **Application (client) ID**: Copy this value
   - This is your `AZURE_CLIENT_ID`
   - Example: `12345678-1234-1234-1234-123456789012`

2. **Directory (tenant) ID**: Copy this value
   - This is your `AZURE_TENANT_ID`
   - For ctstate.edu, this will be your institution's specific tenant ID
   - Example: `abcdef12-3456-7890-abcd-ef1234567890`

### 1.3 Create Client Secret

1. Navigate to: **Certificates & secrets** → **New client secret**
2. Configure:
   ```
   Description: Poker Therapist Backend Service
   Expires: 12 months (recommended for institutional compliance)
   ```
3. **Copy the Value immediately** - This is your `AZURE_CLIENT_SECRET`
   - ⚠️ This will not be shown again!
   - Store securely (do NOT commit to git)

### 1.4 Configure API Permissions

1. Navigate to: **API permissions** → **Add a permission**
2. Select: **Microsoft Graph** → **Delegated permissions**
3. Add these permissions:
   ```
   - User.Read          (Read user profile)
   - email              (Read user email address)
   - profile            (Read user profile information)
   - openid             (OpenID Connect authentication)
   ```
4. Click **Add permissions**
5. **Important**: Click **Grant admin consent for {Your Organization}**
   - This may require IT admin approval

### 1.5 Configure Authentication Settings

1. Navigate to: **Authentication**
2. Under **Implicit grant and hybrid flows**:
   - ✅ Enable "ID tokens"
   - ✅ Enable "Access tokens"
3. Under **Advanced settings**:
   - Allow public client flows: **No** (we use server-side flow)
   - Supported account types: Verify it's set to "Single tenant"

### 1.6 Set Environment Variables

Create or update `.env.local` (this file is excluded from git):

```bash
# Microsoft Azure AD - Institutional SSO Configuration
# For Connecticut State Community College

# Your institution's Azure AD tenant ID
AZURE_TENANT_ID=abcdef12-3456-7890-abcd-ef1234567890

# Your application's client ID
AZURE_CLIENT_ID=12345678-1234-1234-1234-123456789012

# Your application's client secret (NEVER commit this)
AZURE_CLIENT_SECRET=your-secret-value-here

# Authority URL for your specific tenant
AZURE_AUTHORITY=https://login.microsoftonline.com/abcdef12-3456-7890-abcd-ef1234567890

# Required scopes for authentication
AZURE_SCOPES=User.Read email profile openid

# Your institutional email domain (for SSO hint)
INSTITUTIONAL_EMAIL_DOMAIN=ctstate.edu

# Redirect URIs for each environment
AZURE_REDIRECT_URI_WEB=http://localhost:8501/api/auth/callback/microsoft

# Enable Microsoft authentication
ENABLE_MICROSOFT_AUTH=true
DEFAULT_AUTH_PROVIDER=microsoft
```

## Part 2: Google OAuth 2.0 Configuration

### 2.1 Create Google Cloud Project

1. **Navigate to**: https://console.cloud.google.com/
2. **Create New Project**:
   ```
   Project Name: Poker Therapist
   Organization: Your institution (if applicable)
   Location: Your organizational unit
   ```

### 2.2 Enable Required APIs

1. Navigate to: **APIs & Services** → **Library**
2. Search and enable:
   - Google Identity Services API (for OAuth)
   - Cloud Storage API (for data storage)
   - Cloud Identity API (for user management)

### 2.3 Create OAuth 2.0 Credentials

1. Navigate to: **APIs & Services** → **Credentials**
2. Click: **Create Credentials** → **OAuth client ID**
3. Configure:
   ```
   Application type: Web application
   Name: Poker Therapist Web Client
   
   Authorized JavaScript origins:
     - http://localhost:8501
     - http://localhost:8000
     - https://your-production-domain.com
   
   Authorized redirect URIs:
     - http://localhost:8501/api/auth/callback/google
     - http://localhost:8000/api/auth/callback/google
     - https://your-production-domain.com/api/auth/callback/google
     - https://poker-therapist.vercel.app/api/auth/callback/google
   ```

4. **Copy Credentials**:
   - Client ID: `your-client-id.apps.googleusercontent.com`
   - Client Secret: `your-client-secret`

### 2.4 Create Service Account (for GCP APIs)

1. Navigate to: **IAM & Admin** → **Service Accounts**
2. Click: **Create Service Account**
3. Configure:
   ```
   Service account name: poker-therapist-service
   Description: Service account for Poker Therapist backend
   ```
4. Grant roles:
   - Storage Admin (for Cloud Storage)
   - Service Account User
5. Click **Done**
6. **Create Key**:
   - Click on the service account
   - **Keys** → **Add Key** → **Create new key**
   - Type: JSON
   - Save as: `config/google-service-account.json`
   - ⚠️ Add to `.gitignore`!

### 2.5 Set Environment Variables

Add to `.env.local`:

```bash
# Google Cloud Platform Configuration

# OAuth 2.0 Client Credentials
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here

# Google Cloud Project
GOOGLE_CLOUD_PROJECT_ID=poker-therapist-12345

# Service Account (path to JSON key file)
GOOGLE_APPLICATION_CREDENTIALS=./config/google-service-account.json

# OAuth Scopes
GOOGLE_OAUTH_SCOPES=openid email profile https://www.googleapis.com/auth/devstorage.read_write

# Redirect URIs
GOOGLE_REDIRECT_URI_WEB=http://localhost:8501/api/auth/callback/google

# Cloud Storage Configuration
GOOGLE_STORAGE_BUCKET_NAME=poker-therapist-data
GOOGLE_STORAGE_REGION=us-central1

# Enable Google authentication
ENABLE_GOOGLE_AUTH=true
```

## Part 3: Apple Sign-In Configuration

### 3.1 Apple Developer Account Setup

1. **Enroll in Apple Developer Program** (requires $99/year)
2. Navigate to: https://developer.apple.com/account

### 3.2 Register App ID

1. Go to: **Certificates, Identifiers & Profiles**
2. Click: **Identifiers** → **+** → **App IDs**
3. Configure:
   ```
   Description: Poker Therapist
   Bundle ID: com.therapyrex.app (explicit)
   Capabilities: ✅ Sign In with Apple
   ```

### 3.3 Create Services ID

1. Click: **Identifiers** → **+** → **Services IDs**
2. Configure:
   ```
   Description: Poker Therapist Sign In
   Identifier: com.therapyrex.signin
   ✅ Enable "Sign In with Apple"
   ```
3. Click **Configure**:
   ```
   Primary App ID: com.therapyrex.app
   
   Website URLs:
     Domains: your-domain.com, vercel.app
     Return URLs: 
       - https://your-domain.com/api/auth/callback/apple
       - https://poker-therapist.vercel.app/api/auth/callback/apple
   ```

### 3.4 Create Sign In Key

1. Go to: **Keys** → **+**
2. Configure:
   ```
   Key Name: Poker Therapist Sign In Key
   ✅ Enable "Sign In with Apple"
   Configure: Select "com.therapyrex.app"
   ```
3. Click **Continue** → **Register**
4. **Download the key** (`.p8` file)
   - Save as: `config/apple-auth-key.p8`
   - ⚠️ Cannot be re-downloaded! Store securely
   - Note the Key ID (e.g., `ABC123DEFG`)

### 3.5 Set Environment Variables

Add to `.env.local`:

```bash
# Apple Sign-In Configuration

# Your Apple Developer Team ID
APPLE_TEAM_ID=YOUR_TEAM_ID

# Services ID for Sign In with Apple
APPLE_SERVICES_ID=com.therapyrex.signin

# Sign In Key ID
APPLE_KEY_ID=ABC123DEFG

# Path to private key file
APPLE_PRIVATE_KEY_PATH=./config/apple-auth-key.p8

# App Bundle IDs
APPLE_BUNDLE_ID_IOS=com.therapyrex.app
APPLE_BUNDLE_ID_WATCHOS=com.therapyrex.app.watchkitapp

# Enable Apple authentication
ENABLE_APPLE_AUTH=true
```

## Part 4: JWT and Security Configuration

Add to `.env.local`:

```bash
# JWT Configuration
# Generate a secure random key: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=your-secure-random-key-here-do-not-commit
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Session Configuration
SESSION_TIMEOUT_HOURS=24
REFRESH_TOKEN_EXPIRATION_DAYS=30

# Security Settings
REQUIRE_AUTHENTICATION=true
ALLOW_ANONYMOUS_TRIAGE=false
FORCE_HTTPS=true  # Set to false for local development

# CORS Configuration (add your frontend domains)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8501,https://your-domain.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

## Part 5: Verification and Testing

### 5.1 Local Testing

1. **Start the backend server**:
   ```bash
   cd /home/runner/work/Poker-Therapist/Poker-Therapist
   python -m uvicorn backend.api.main:app --reload --port 8000
   ```

2. **Test authentication endpoints**:
   ```bash
   # Check enabled providers
   curl http://localhost:8000/api/auth/providers
   
   # Should return:
   # {
   #   "providers": ["microsoft", "google", "apple"],
   #   "default": "microsoft",
   #   "require_authentication": true
   # }
   ```

3. **Test authorization URL generation**:
   ```bash
   curl -X POST http://localhost:8000/api/auth/authorize \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "microsoft",
       "redirect_uri": "http://localhost:8501/api/auth/callback/microsoft",
       "state": "random-state-value"
     }'
   ```

4. **Test the full OAuth flow**:
   - Open the authorization URL in a browser
   - Sign in with your institutional account
   - Verify you're redirected back with an authorization code
   - Exchange code for tokens using the `/api/auth/token` endpoint

### 5.2 Integration Testing

Test with the Streamlit chatbot:

```bash
# Start the chatbot
streamlit run chatbot_app.py --server.port 8501
```

Try signing in with:
- Your institutional Microsoft account (user.name@ctstate.edu)
- Your Google account
- Apple ID (if on iOS/macOS)

### 5.3 Production Deployment

#### Vercel Configuration

1. **Navigate to**: Vercel Dashboard → Your Project → Settings → Environment Variables

2. **Add all environment variables** from `.env.local`:
   - For secrets, use Vercel's secret encryption
   - For file-based credentials (Google service account, Apple key):
     - Convert to base64: `base64 -i config/file.json`
     - Store as environment variable
     - Decode at runtime in application

3. **Configure domains**:
   - Update redirect URIs in Azure AD, Google Cloud Console, and Apple Developer
   - Use production URLs: `https://poker-therapist.vercel.app`

#### Environment-Specific Configuration

```bash
# Development
ENVIRONMENT=development
FORCE_HTTPS=false
AZURE_REDIRECT_URI_WEB=http://localhost:8501/api/auth/callback/microsoft

# Staging
ENVIRONMENT=staging
FORCE_HTTPS=true
AZURE_REDIRECT_URI_WEB=https://poker-therapist-staging.vercel.app/api/auth/callback/microsoft

# Production
ENVIRONMENT=production
FORCE_HTTPS=true
AZURE_REDIRECT_URI_WEB=https://poker-therapist.vercel.app/api/auth/callback/microsoft
```

## Part 6: Troubleshooting

### Common Issues and Solutions

#### Microsoft Authentication Issues

**Issue**: "AADSTS50011: The reply URL specified in the request does not match the reply URLs configured"

**Solution**: 
1. Check Azure AD app registration → Authentication → Redirect URIs
2. Ensure exact match (including trailing slashes)
3. Wait 5-10 minutes for Azure AD changes to propagate

**Issue**: "AADSTS700016: Application not found"

**Solution**: 
- Verify `AZURE_CLIENT_ID` is correct
- Ensure you're using the correct tenant ID
- Check that app registration is in the correct directory

**Issue**: "Invalid client secret"

**Solution**:
- Generate a new client secret
- Update `AZURE_CLIENT_SECRET` immediately
- Ensure no whitespace in the secret value

#### Google Authentication Issues

**Issue**: "redirect_uri_mismatch"

**Solution**:
1. Go to Google Cloud Console → Credentials
2. Edit OAuth 2.0 Client ID
3. Add the exact redirect URI (including protocol and port)
4. No trailing slashes in redirect URIs

**Issue**: "access_denied: Consent required"

**Solution**:
- Ensure required scopes are configured
- Check if OAuth consent screen is properly configured
- For institutional accounts, admin consent may be required

#### Token Issues

**Issue**: "Token validation failed"

**Solution**:
- Verify `JWT_SECRET_KEY` is set and consistent across restarts
- Check token expiration settings
- Ensure system clocks are synchronized (for JWT exp claims)

#### CORS Issues

**Issue**: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solution**:
1. Update `CORS_ALLOWED_ORIGINS` in `.env.local`
2. Include your frontend domain
3. For development, ensure localhost with correct port is included

## Part 7: Security Best Practices

### Credential Management

1. **Never commit secrets**:
   ```bash
   # Verify .gitignore includes:
   .env.local
   .env
   *.p8
   *service-account*.json
   config/*.json
   config/*.p8
   ```

2. **Use Azure Key Vault or Google Secret Manager** in production:
   ```python
   # Example: Azure Key Vault integration
   from azure.keyvault.secrets import SecretClient
   from azure.identity import DefaultAzureCredential
   
   credential = DefaultAzureCredential()
   client = SecretClient(
       vault_url="https://poker-therapist-kv.vault.azure.net/",
       credential=credential
   )
   
   azure_client_secret = client.get_secret("AZURE-CLIENT-SECRET").value
   ```

3. **Rotate credentials regularly**:
   - Microsoft secrets: Every 90 days
   - Google service account keys: Every 90 days
   - Apple Sign-In keys: Annually
   - JWT secret: Every 180 days

### Access Control

1. **Principle of Least Privilege**:
   - Grant only necessary API permissions
   - Use separate service accounts for different environments
   - Restrict Azure AD app to single tenant when possible

2. **Enable MFA**:
   - Require MFA for all administrative accounts
   - For institutional accounts, follow your IT security policies

3. **Monitor and Audit**:
   - Review Azure AD sign-in logs regularly
   - Monitor Google Cloud Console audit logs
   - Set up alerts for failed authentication attempts
   - Track token usage and refresh patterns

### Compliance

For educational institutions:

1. **FERPA Compliance** (if handling student data):
   - Ensure proper data encryption (in transit and at rest)
   - Implement access controls
   - Maintain audit logs

2. **HIPAA Compliance** (if handling health data):
   - Additional security controls may be required
   - Consult with your institution's compliance officer

3. **Data Residency**:
   - Choose cloud regions that comply with your institution's policies
   - For Google Cloud: Set `GOOGLE_STORAGE_REGION` appropriately
   - For Azure: Select appropriate Azure region in configurations

## Part 8: Support and Resources

### Official Documentation

- **Microsoft Identity Platform**: https://docs.microsoft.com/en-us/azure/active-directory/develop/
- **Google OAuth 2.0**: https://developers.google.com/identity/protocols/oauth2
- **Apple Sign-In**: https://developer.apple.com/sign-in-with-apple/

### Repository Documentation

- **Quick Start**: `AUTH_QUICKSTART.md`
- **Full Setup Guide**: `AUTHENTICATION_SETUP.md`
- **Testing Guide**: `AUTH_TESTING_GUIDE.md`
- **Implementation Summary**: `AUTHENTICATION_IMPLEMENTATION_SUMMARY.md`

### Getting Help

1. **IT Department**: Contact your institution's IT support for:
   - Azure AD tenant access
   - Google Workspace configuration
   - Security policy compliance

2. **Repository Issues**: https://github.com/JohnDaWalka/Poker-Therapist/issues

3. **Security Concerns**: Follow responsible disclosure practices

## Conclusion

This guide provides comprehensive instructions for configuring institutional authentication for the Poker Therapist application. After completing these steps:

✅ Users can sign in with institutional Microsoft accounts (e.g., @ctstate.edu)  
✅ Google OAuth 2.0 integration is configured for GCP APIs  
✅ Apple Sign-In is ready for iOS/macOS/watchOS apps  
✅ JWT tokens secure API access  
✅ All credentials are properly managed and secured  
✅ The application is ready for deployment

---

**Last Updated**: January 25, 2025  
**Version**: 1.0  
**Status**: ✅ Complete and Tested
