# Credential Configuration Guide

This guide provides step-by-step instructions to configure authentication for the Poker Therapist application using your organization-managed accounts and institutional credentials.

## ⚠️ Security Notice

**IMPORTANT**: This guide helps you configure authentication credentials following your organization's security policies. 

- **NEVER store raw credentials or passwords in this document or source control**
- All credentials must be stored in `.env.local` (which is excluded from git)
- Follow your institution's IT security policies and credential management guidelines
- Rotate credentials regularly as per your organization's security requirements
- Use separate credentials for development, staging, and production environments

## Prerequisites

Before starting, ensure you have:

1. **Institutional Email Account**: Your organization-managed account (e.g., `your.name@ctstate.edu`)
2. **Microsoft Azure Access**: Access to your organization's Azure AD tenant (or ability to create one)
3. **Google Account**: A Google account for GCP services (can be institutional or personal)
4. **Development Environment**: Python 3.8+ and required dependencies installed

## Step 1: Initial Setup

### 1.1 Create Environment File

```bash
# Copy the example environment file
cp .env.example .env.local

# The .env.local file is automatically excluded from git
```

### 1.2 Verify .gitignore

**CRITICAL SECURITY STEP**: Ensure these files are in `.gitignore` before proceeding:

```bash
# Check that sensitive files are ignored
grep -E "\.env\.local|service-account.*\.json|\.p8$" .gitignore
```

If not present, add them immediately:

```bash
echo ".env.local" >> .gitignore
echo "*service-account*.json" >> .gitignore
echo "*.p8" >> .gitignore
echo "config/*.json" >> .gitignore
echo "config/*.p8" >> .gitignore
```

**Verify they're excluded**:
```bash
git status --ignored | grep -E "\.env\.local|service-account|\.p8"
# These files should show as ignored
```

## Step 2: Configure Microsoft Authentication (Institutional SSO)

This enables authentication using your organization-managed Microsoft Windows account.

### 2.1 Register Application in Azure AD

1. **Go to Azure Portal**: https://portal.azure.com
2. **Navigate to**: Azure Active Directory → App registrations → New registration
3. **Configure**:
   - **Name**: `Poker Therapist`
   - **Supported account types**: 
     - For single organization: "Accounts in this organizational directory only"
     - For institutional email (e.g., @ctstate.edu): Contact your IT department
   - **Redirect URI**: Add these (Platform: Web):
     - `http://localhost:8501/auth/callback` (for local testing)
     - `https://your-production-domain.com/auth/callback` (for production)

4. **Click**: Register

### 2.2 Get Credentials

From the Azure Portal app registration page:

1. **Copy Application (client) ID**: This is your `AZURE_CLIENT_ID`
2. **Copy Directory (tenant) ID**: This is your `AZURE_TENANT_ID`

### 2.3 Create Client Secret

1. **Go to**: Certificates & secrets → New client secret
2. **Description**: "Poker Therapist Backend"
3. **Expires**: Choose appropriate expiration (12-24 months recommended)
4. **Copy the Value**: This is your `AZURE_CLIENT_SECRET` 
   - ⚠️ **CRITICAL**: Copy immediately - it won't be shown again!

### 2.4 Configure API Permissions

1. **Go to**: API permissions → Add a permission
2. **Select**: Microsoft Graph → Delegated permissions
3. **Add**:
   - `User.Read`
   - `email`
   - `profile`
   - `openid`
   - `offline_access` (for refresh tokens)
4. **Click**: Grant admin consent (requires admin privileges or contact IT)

### 2.5 Configure Institutional SSO (if applicable)

If using institutional email (e.g., @ctstate.edu):

1. **Work with your IT department** to get the correct Tenant ID
2. **Update Authority URL** to use your specific tenant:
   ```
   https://login.microsoftonline.com/{your-institutional-tenant-id}
   ```
3. **Set institutional domain** in configuration

### 2.6 Update .env.local

Add to `.env.local`:

```bash
# Microsoft Azure AD Configuration
AZURE_TENANT_ID=your-tenant-id-from-step-2.2
AZURE_CLIENT_ID=your-client-id-from-step-2.2
AZURE_CLIENT_SECRET=your-client-secret-from-step-2.3
AZURE_AUTHORITY=https://login.microsoftonline.com/your-tenant-id
AZURE_SCOPES=User.Read email profile openid offline_access

# For institutional SSO (e.g., ctstate.edu)
INSTITUTIONAL_EMAIL_DOMAIN=ctstate.edu

# Redirect URIs
AZURE_REDIRECT_URI_WEB=http://localhost:8501/auth/callback
```

## Step 3: Configure Google OAuth 2.0 (GCP Integration)

This enables OAuth 2.0/OpenID Connect with Google for accessing GCP APIs.

### 3.1 Create GCP Project

1. **Go to**: https://console.cloud.google.com
2. **Click**: Select a project → New Project
3. **Name**: "Poker Therapist"
4. **Click**: Create
5. **Note**: Your Project ID (you'll need this)

### 3.2 Enable Required APIs

1. **Go to**: APIs & Services → Library
2. **Enable these APIs**:
   - Google Identity Platform
   - Cloud Storage API
   - Cloud Identity API

### 3.3 Configure OAuth Consent Screen

1. **Go to**: APIs & Services → OAuth consent screen
2. **User Type**: 
   - External (for public access)
   - Internal (if using Google Workspace/G Suite organization)
3. **App Information**:
   - App name: "Poker Therapist"
   - User support email: Your email
   - Developer email: Your email
4. **Scopes**: Add these scopes:
   - `openid`
   - `email`
   - `profile`
   - `https://www.googleapis.com/auth/devstorage.read_write` (for Cloud Storage)
5. **Test Users**: Add your email for testing

### 3.4 Create OAuth 2.0 Credentials

1. **Go to**: APIs & Services → Credentials
2. **Click**: Create Credentials → OAuth client ID
3. **Application type**: Web application
4. **Name**: "Poker Therapist Web"
5. **Authorized JavaScript origins**:
   - `http://localhost:8501`
   - Your production domain
6. **Authorized redirect URIs**:
   - `http://localhost:8501/google/callback`
   - `https://your-production-domain.com/google/callback`
7. **Click**: Create
8. **Copy**: 
   - Client ID → `GOOGLE_CLIENT_ID`
   - Client Secret → `GOOGLE_CLIENT_SECRET`

### 3.5 Create Service Account (for Cloud Storage)

1. **Go to**: IAM & Admin → Service Accounts
2. **Click**: Create Service Account
3. **Name**: "poker-therapist-storage"
4. **Description**: "Service account for Poker Therapist Cloud Storage access"
5. **Click**: Create and Continue
6. **Grant role**: Storage Object Admin (or Storage Admin for full access)
7. **Click**: Create and Continue
8. **Grant role**: Storage Object Admin (or Storage Admin for full access)
9. **Click**: Done
10. **Click on the service account** → Keys → Add Key → Create new key
11. **Key type**: JSON
12. **Click**: Create
13. **Save the JSON file** to: `config/google-service-account.json`
    - ⚠️ **CRITICAL**: Keep this file secure and NEVER commit to git
    - ⚠️ **Verify**: Run `git status` - file should NOT appear (should be ignored)
    - ⚠️ **If it appears**: Check `.gitignore` includes `*service-account*.json` and `config/*.json`

### 3.6 Create Cloud Storage Bucket

1. **Go to**: Cloud Storage → Buckets → Create
2. **Name**: `poker-therapist-data-{your-unique-id}` (must be globally unique)
3. **Location**: Choose closest to your users (e.g., `us-central1`)
4. **Storage class**: Standard
5. **Access control**: Uniform
6. **Click**: Create

### 3.7 Update .env.local

Add to `.env.local`:

```bash
# Google Cloud Platform Configuration
GOOGLE_CLOUD_PROJECT_ID=your-project-id-from-step-3.1
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-from-step-3.4
GOOGLE_OAUTH_SCOPES=openid email profile https://www.googleapis.com/auth/devstorage.read_write

# Google Cloud Storage
GOOGLE_STORAGE_BUCKET_NAME=poker-therapist-data-{your-unique-id}
GOOGLE_STORAGE_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./config/google-service-account.json

# Google Redirect URIs
GOOGLE_REDIRECT_URI_WEB=http://localhost:8501/google/callback
```

## Step 4: Configure Apple Sign-In (Optional - iOS/macOS/watchOS)

This step is **optional** and only required if you're deploying to iOS, macOS, or watchOS.

### 4.1 Register App IDs

1. **Go to**: https://developer.apple.com/account
2. **Navigate to**: Certificates, Identifiers & Profiles → Identifiers
3. **Create App ID**:
   - Description: "Therapy Rex iOS"
   - Bundle ID: `com.therapyrex.app`
   - Capabilities: Enable "Sign in with Apple"

### 4.2 Create Services ID

1. **Click**: + → Services IDs
2. **Description**: "Therapy Rex Sign In"
3. **Identifier**: `com.therapyrex.signin`
4. **Enable**: Sign in with Apple
5. **Configure**:
   - Primary App ID: Select your iOS App ID
   - Website URLs: Add your domain and return URLs

### 4.3 Create Private Key

1. **Go to**: Keys → +
2. **Key Name**: "Therapy Rex Sign In Key"
3. **Enable**: Sign in with Apple
4. **Configure**: Select your primary App ID
5. **Click**: Continue → Register
6. **Download**: The .p8 file
   - ⚠️ **CRITICAL**: Save to `config/apple-auth-key.p8`
   - ⚠️ **CRITICAL**: You cannot download it again - save securely
   - ⚠️ **Verify**: Run `git status` - file should NOT appear (should be ignored)
   - ⚠️ **If it appears**: Check `.gitignore` includes `*.p8` and `config/*.p8`
7. **Note**: The Key ID (you'll need this)

### 4.4 Update .env.local

Add to `.env.local`:

```bash
# Apple Sign-In Configuration (Optional)
APPLE_TEAM_ID=your-team-id
APPLE_SERVICES_ID=com.therapyrex.signin
APPLE_KEY_ID=your-key-id-from-step-4.3
APPLE_PRIVATE_KEY_PATH=./config/apple-auth-key.p8
APPLE_BUNDLE_ID_IOS=com.therapyrex.app
```

## Step 5: Configure JWT and Security Settings

### 5.1 Generate JWT Secret

Generate a secure random secret for JWT token signing:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and add to `.env.local`:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-generated-secret-from-above
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### 5.2 Configure Security Settings

Add to `.env.local`:

```bash
# Security Settings
REQUIRE_AUTHENTICATION=true
ENABLE_MICROSOFT_AUTH=true
ENABLE_GOOGLE_AUTH=true
ENABLE_APPLE_AUTH=false  # Set to true if you configured Apple Sign-In

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:8501,http://localhost:3000

# HTTPS (set to true in production)
FORCE_HTTPS=false

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

## Step 6: Verify Configuration

### 6.1 Run Verification Script

```bash
# Install dependencies if not already installed
pip install -r backend/requirements.txt

# Run verification script
python scripts/verify_auth_config.py
```

The script will check:
- ✓ All required environment variables are set
- ✓ Credentials are properly formatted
- ✓ Authentication providers can be initialized
- ✓ Google Cloud Storage is accessible
- ✓ Security settings are configured

### 6.2 Expected Output

```
Authentication Configuration Verification
==========================================

✓ Loaded environment from .env.local

Microsoft Azure AD / Windows Authentication
===========================================

✓ All Microsoft credentials configured
✓ Microsoft authentication provider initialized
✓ Microsoft authorization URL generation works
ℹ Authority: https://login.microsoftonline.com/{tenant-id}
ℹ Tenant ID: {your-tenant-id}

Google OAuth 2.0 / GCP Authentication
======================================

✓ All Google credentials configured
✓ Google authentication provider initialized
✓ Google authorization URL generation works
ℹ Project ID: {your-project-id}

...

Verification Summary
====================

✓ JWT Configuration: PASSED
✓ Microsoft Authentication: PASSED
✓ Google Authentication: PASSED
✓ Google Cloud Storage: PASSED
✓ Security Settings: PASSED

Results: 5/6 checks passed

✓ All authentication providers configured correctly! 🎉
```

## Step 7: Test End-to-End

### 7.1 Start Backend Server

```bash
cd backend
uvicorn api.main:app --reload
```

The server should start without errors on `http://localhost:8000`

### 7.2 Test Microsoft Authentication

1. **Open**: `http://localhost:8000/auth/microsoft/authorize` (or use API endpoint)
2. **Sign in**: With your Microsoft/institutional account
3. **Grant permissions**: If prompted
4. **Verify**: Successful redirect with authorization code
5. **Check**: Token exchange and user profile retrieval work

### 7.3 Test Google Authentication

1. **Open**: `http://localhost:8000/auth/google/authorize` (or use API endpoint)
2. **Sign in**: With your Google account
3. **Grant permissions**: For required scopes
4. **Verify**: Successful authentication and token generation

### 7.4 Test Cloud Storage

```bash
# Test using Python
python -c "
from backend.cloud.google_storage import GoogleCloudStorage
storage = GoogleCloudStorage()
print(f'Bucket exists: {storage.bucket_exists()}')
print(f'Project: {storage.project_id}')
print(f'Bucket: {storage.bucket_name}')
"
```

Expected output:
```
Bucket exists: True
Project: your-project-id
Bucket: poker-therapist-data-{your-id}
```

## Step 8: Deploy to Test Environment

### 8.1 Prepare for Deployment

1. **Create separate credentials** for test/staging environment
2. **Update redirect URIs** in Azure and Google consoles for test domain
3. **Set environment variables** in your hosting platform (Vercel, Azure, GCP, etc.)
4. **Never include** `.env.local` or credential files in deployment

### 8.2 Deployment Platforms

**Vercel**:
```bash
# Set environment variables in Vercel dashboard
# See: https://vercel.com/docs/concepts/projects/environment-variables
```

**Azure App Service**:
```bash
az webapp config appsettings set --name <app-name> \
  --resource-group <group-name> \
  --settings \
  AZURE_CLIENT_ID=<value> \
  AZURE_CLIENT_SECRET=<value>
```

**Google Cloud Run**:
```bash
gcloud run deploy poker-therapist \
  --set-env-vars GOOGLE_CLOUD_PROJECT_ID=<value>
```

### 8.3 Verify Deployment

Follow the checklist in `DEPLOYMENT_VERIFICATION.md`:

- [ ] All authentication flows work in test environment
- [ ] Tokens are generated and validated correctly
- [ ] Cloud Storage is accessible
- [ ] API calls are properly authenticated
- [ ] No credentials exposed in client-side code
- [ ] Logs don't contain sensitive information

## Troubleshooting

### Common Issues

**"AZURE_CLIENT_ID must be set in environment"**
- Ensure `.env.local` is in the project root
- Verify the variable name is exactly `AZURE_CLIENT_ID` (case-sensitive)
- Check for typos or extra spaces

**"redirect_uri_mismatch" from Google**
- Exact match required in Google Cloud Console
- Check http vs https
- Verify port numbers match

**"Service account credentials not found"**
- Ensure JSON file is at the path specified in `GOOGLE_APPLICATION_CREDENTIALS`
- Check file permissions (should be readable)
- Verify JSON file is valid (not corrupted)

**"Bucket does not exist or is not accessible"**
- Verify bucket name is correct
- Check service account has "Storage Object Admin" role
- Ensure bucket is in the correct project

### Getting Help

1. **Review documentation**:
   - `AUTHENTICATION_SETUP.md` - Detailed setup guide
   - `GOOGLE_CLOUD_SETUP.md` - GCP-specific guide
   - `DEPLOYMENT_VERIFICATION.md` - Testing checklist

2. **Check provider documentation**:
   - [Microsoft MSAL docs](https://docs.microsoft.com/azure/active-directory/develop/)
   - [Google Sign-In docs](https://developers.google.com/identity)
   - [Apple Sign-In docs](https://developer.apple.com/sign-in-with-apple/)

3. **Contact support**:
   - For institutional SSO: Contact your IT department
   - For Azure issues: Microsoft support
   - For GCP issues: Google Cloud support

## Security Checklist

Before going to production:

- [ ] All credentials stored in `.env.local` or secure vault
- [ ] No credentials in source code or git history
- [ ] `.gitignore` properly configured
- [ ] Separate credentials for dev/test/prod
- [ ] HTTPS enabled in production (`FORCE_HTTPS=true`)
- [ ] CORS properly configured (no `*` in production)
- [ ] Rate limiting enabled
- [ ] JWT secret is strong and unique
- [ ] Service account has minimal required permissions
- [ ] Regular credential rotation scheduled
- [ ] Monitoring and logging enabled
- [ ] Backup and recovery procedures in place

## Summary

You have now configured:

1. ✅ **Microsoft Authentication** - Organization-managed Windows account and institutional SSO
2. ✅ **Google OAuth 2.0** - OpenID Connect for GCP API access
3. ✅ **Google Cloud Storage** - Cloud storage for application data
4. ✅ **Apple Sign-In** - (Optional) For iOS/macOS/watchOS apps
5. ✅ **JWT Tokens** - Secure token-based authentication
6. ✅ **Security Settings** - CORS, HTTPS, rate limiting

**Next Steps**:

1. Run `python scripts/verify_auth_config.py` to verify configuration
2. Start the backend server and test authentication flows
3. Deploy to test environment and verify end-to-end
4. Review `DEPLOYMENT_VERIFICATION.md` for complete testing
5. Configure production credentials when ready to deploy

For detailed implementation and troubleshooting, refer to:
- `AUTHENTICATION_SETUP.md`
- `GOOGLE_CLOUD_SETUP.md`
- `DEPLOYMENT_VERIFICATION.md`
- `AUTH_QUICKSTART.md`
