# Authentication Verification Guide

This document provides step-by-step instructions to configure and verify authentication for the Poker Therapist application using your organization-managed accounts.

## Overview

The Poker Therapist application supports multiple authentication methods to accommodate different platforms and organizational requirements:

1. **Microsoft Azure AD** - For Windows accounts and institutional SSO (e.g., @ctstate.edu)
2. **Google OAuth 2.0** - For Gmail accounts and Google Cloud Platform integration
3. **Apple Sign-In** - For iCloud accounts on iOS/macOS/watchOS

## Authorized Email Addresses

The following email addresses are pre-authorized as VIP users with full access to all features:

- **m.fanelli1@icloud.com** - Apple iCloud account
- **maurofanellijr@gmail.com** - Google Gmail account  
- **mauro.fanelli@ctstate.edu** - Institutional Microsoft account
- johndawalka@icloud.com - Apple iCloud account
- cooljack87@icloud.com - Apple iCloud account
- jdwalka@pm.me - ProtonMail account

## Quick Start: Streamlit Web Application

The Streamlit chatbot (`chatbot_app.py`) uses simple email-based authentication with a whitelist system. This does **not** require OAuth setup for basic usage.

### Step 1: Configure Authorized Emails

You can use the default authorized emails or add your own:

1. Copy `.env.example` to `.env.local`:
   ```bash
   cp .env.example .env.local
   ```

2. (Optional) Update `AUTHORIZED_EMAILS` in `.env.local`:
   ```bash
   # Leave empty to use defaults, or override with comma-separated list
   AUTHORIZED_EMAILS=m.fanelli1@icloud.com,maurofanellijr@gmail.com,mauro.fanelli@ctstate.edu
   ```

### Step 2: Run the Application

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the Streamlit app:
   ```bash
   streamlit run chatbot_app.py
   ```

3. Open your browser to `http://localhost:8501`

### Step 3: Test Email Authentication

1. In the sidebar, you'll see **"👤 Account Login"**
2. Choose **"Select from authorized"** 
3. Select one of the pre-authorized emails from the dropdown:
   - `m.fanelli1@icloud.com` (for iCloud testing)
   - `maurofanellijr@gmail.com` (for Gmail testing)
   - `mauro.fanelli@ctstate.edu` (for institutional testing)

4. You should see: **"✅ Logged in as: [email] 🎰 (Authorized User)"**

5. Verify VIP features are enabled:
   - You should see: **"🎰 VIP Access: Full voice and Rex personality features enabled"**
   - Voice features should be available in the interface

### Step 4: Test Custom Email

1. Choose **"Enter custom email"**
2. Enter any valid email address (e.g., `test@example.com`)
3. Click outside the text box
4. You should see: **"✅ Logged in as: test@example.com"** (without VIP badge)
5. Limited features will be available (no voice/Rex personality)

### Email Validation Logic

The application validates emails using a simple check:
- Email must contain `@` symbol
- Domain must contain at least one `.` (e.g., `@icloud.com`, `@gmail.com`, `@ctstate.edu`)

This allows any well-formed email address to access the basic chatbot functionality, while VIP features are reserved for authorized emails.

## Full OAuth Setup (iOS, Windows, Backend APIs)

For mobile and desktop applications that need full OAuth 2.0 / OpenID Connect authentication, follow the comprehensive setup guide.

### Prerequisites

- **Microsoft Azure account** - For @ctstate.edu institutional SSO
- **Google Cloud Platform account** - For @gmail.com OAuth and cloud storage
- **Apple Developer account** - For @icloud.com accounts and iOS apps
- **Access to institutional IT** - For Azure AD tenant configuration

### Microsoft Azure AD Setup (for @ctstate.edu)

This allows users to sign in with their organization-managed Windows accounts.

#### 1. Register Application in Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to: **Azure Active Directory** → **App registrations** → **New registration**
3. Configure:
   - **Name**: Poker Therapist
   - **Supported account types**: 
     - Select "Accounts in any organizational directory" (Multi-tenant)
     - Enable "Personal Microsoft accounts" if supporting @outlook.com/@hotmail.com
   - **Redirect URI**: 
     - Platform: Web
     - URI: `http://localhost:8501/auth/callback`

4. Click **Register**

#### 2. Configure Redirect URIs for All Platforms

After registration, go to **Authentication** and add:

- **iOS**: `msauth.com.therapyrex.app://auth`
- **Windows**: `http://localhost:3000/auth/callback`
- **Web (Streamlit)**: `http://localhost:8501/auth/callback`
- **Production**: `https://your-domain.com/auth/callback`

#### 3. Create Client Secret

1. Go to **Certificates & secrets** → **New client secret**
2. Description: "Poker Therapist Backend"
3. Expiration: 24 months (maximum)
4. Click **Add**
5. **⚠️ CRITICAL**: Copy the secret value immediately - you cannot retrieve it later

#### 4. Configure API Permissions

1. Go to **API permissions** → **Add a permission**
2. Select **Microsoft Graph**
3. Choose **Delegated permissions**
4. Add these scopes:
   - `User.Read` - Read user profile
   - `email` - Read email address
   - `profile` - Read basic profile
   - `openid` - OpenID Connect authentication
   - `offline_access` - Refresh tokens

5. Click **Grant admin consent for [organization]** (requires admin role)

#### 5. Configure Institutional SSO

For @ctstate.edu accounts:

1. Contact your IT department and request:
   - **Tenant ID** for your organization's Azure AD
   - Permission to register the Poker Therapist app
   - Verification that app is properly configured in organizational Azure AD

2. Update your `.env.local`:
   ```bash
   # Use your organization's tenant ID for institutional accounts
   AZURE_TENANT_ID=your-organization-tenant-id
   AZURE_AUTHORITY=https://login.microsoftonline.com/{tenant-id}
   INSTITUTIONAL_EMAIL_DOMAIN=ctstate.edu
   ```

3. For multi-tenant support (both institutional and personal accounts):
   ```bash
   # Use 'common' for multi-tenant
   AZURE_AUTHORITY=https://login.microsoftonline.com/common
   ```

#### 6. Save Configuration Values

From Azure Portal **Overview** page, save:

```bash
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret-from-step-3
AZURE_AUTHORITY=https://login.microsoftonline.com/common
AZURE_SCOPES=User.Read email profile openid offline_access
```

### Google OAuth 2.0 Setup (for @gmail.com)

This allows users to sign in with their Google accounts and enables Google Cloud Platform integration.

#### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click **Select a project** → **New Project**
3. Project name: "Poker Therapist"
4. Click **Create**
5. Wait for project creation to complete

#### 2. Enable Required APIs

1. Navigate to **APIs & Services** → **Library**
2. Search for and enable:
   - **Google Identity Platform** - For OAuth
   - **Cloud Storage API** - For file storage
   - **Cloud Identity API** - For user management

#### 3. Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose user type:
   - **External** - For public apps and Gmail users
   - **Internal** - For G Suite/Workspace organizations only

3. Fill in application details:
   - **App name**: Poker Therapist
   - **User support email**: maurofanellijr@gmail.com (or your email)
   - **Developer contact**: maurofanellijr@gmail.com

4. Add scopes:
   - `openid`
   - `email`
   - `profile`
   - `.../auth/devstorage.read_write` (for Cloud Storage)

5. Add test users during development:
   - maurofanellijr@gmail.com
   - Add other Gmail addresses you want to test

6. Save and continue

#### 4. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**

3. **For Web Application**:
   - Application type: **Web application**
   - Name: "Poker Therapist Web"
   - Authorized JavaScript origins:
     - `http://localhost:8501`
     - `http://localhost:3000`
     - Your production domain (e.g., `https://your-domain.com`)
   - Authorized redirect URIs:
     - `http://localhost:8501/google/callback`
     - `http://localhost:3000/google/callback`
     - Your production callback (e.g., `https://your-domain.com/google/callback`)
   - Click **Create**

4. **For iOS Application** (if needed):
   - Application type: **iOS**
   - Name: "Poker Therapist iOS"
   - Bundle ID: `com.therapyrex.app`
   - Click **Create**

5. **Download the JSON** or copy Client ID and Client Secret

#### 5. Create Service Account for Backend

For server-side Google Cloud Storage access:

1. Go to **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Details:
   - Name: "poker-therapist-storage"
   - Description: "Service account for Poker Therapist Cloud Storage access"
4. Grant roles:
   - **Storage Object Admin** (for read/write access to storage buckets)
5. Click **Done**
6. Click on the service account name
7. Go to **Keys** tab → **Add Key** → **Create new key**
8. Select **JSON** format
9. Click **Create** - the JSON file will download automatically
10. **⚠️ IMPORTANT**: Save this file as `config/google-service-account.json`
11. **⚠️ NEVER commit this file to version control**

#### 6. Create Cloud Storage Bucket

1. Go to **Cloud Storage** → **Buckets** → **Create**
2. Configure:
   - Name: `poker-therapist-data-{unique-suffix}` (must be globally unique)
   - Location type: **Region**
   - Location: **us-central1** (or closest to your users)
   - Storage class: **Standard**
   - Access control: **Uniform**
   - Protection tools: Enable as needed
3. Click **Create**

4. Grant service account access:
   - Select your bucket
   - Go to **Permissions** tab
   - Click **Grant Access**
   - Add your service account email: `poker-therapist-storage@your-project-id.iam.gserviceaccount.com`
   - Role: **Storage Object Admin**
   - Click **Save**

#### 7. Save Configuration Values

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_OAUTH_SCOPES=openid email profile https://www.googleapis.com/auth/devstorage.read_write

# Google Cloud Storage
GOOGLE_STORAGE_BUCKET_NAME=poker-therapist-data-{unique-suffix}
GOOGLE_STORAGE_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./config/google-service-account.json
```

### Apple Sign-In Setup (for @icloud.com)

This allows users to sign in with their Apple ID for iOS, macOS, and watchOS apps.

#### 1. Register App IDs

1. Go to [Apple Developer Portal](https://developer.apple.com/account)
2. Navigate to **Certificates, Identifiers & Profiles** → **Identifiers**
3. Click **+** to add new identifier

4. **Create iOS App ID**:
   - Select **App IDs** → **Continue**
   - Select **App** → **Continue**
   - Description: "Therapy Rex iOS"
   - Bundle ID: **Explicit** - `com.therapyrex.app`
   - Capabilities: Check **Sign in with Apple**
   - Click **Continue** → **Register**

5. **Create watchOS App ID**:
   - Repeat above steps
   - Description: "Therapy Rex Watch"
   - Bundle ID: `com.therapyrex.app.watchkitapp`
   - Capabilities: Check **Sign in with Apple**

#### 2. Create Services ID (for Web)

1. Click **+** → Select **Services IDs** → **Continue**
2. Description: "Therapy Rex Sign In"
3. Identifier: `com.therapyrex.signin`
4. Click **Continue** → **Register**

5. Click on your new Services ID
6. Check **Sign in with Apple**
7. Click **Configure**:
   - Primary App ID: Select `com.therapyrex.app`
   - Domains and Subdomains: `your-domain.com` (or `localhost` for testing)
   - Return URLs: 
     - `http://localhost:8501/auth/apple/callback`
     - `https://your-domain.com/auth/apple/callback`
   - Click **Save**

#### 3. Create Private Key

1. Navigate to **Keys** section
2. Click **+** to create new key
3. Key Name: "Therapy Rex Auth Key"
4. Check **Sign in with Apple**
5. Click **Configure** next to Sign in with Apple
6. Select Primary App ID: `com.therapyrex.app`
7. Click **Save** → **Continue** → **Register**

8. **⚠️ CRITICAL**: Download the .p8 file immediately
   - You **cannot** download it again
   - Save as `config/apple-auth-key.p8`
   - Note the **Key ID** displayed

#### 4. Collect Team ID

1. Go to **Membership** in Apple Developer portal
2. Copy your **Team ID** (10-character alphanumeric string)

#### 5. Save Configuration Values

```bash
APPLE_TEAM_ID=your-10-char-team-id
APPLE_SERVICES_ID=com.therapyrex.signin
APPLE_KEY_ID=your-key-id-from-step-3
APPLE_PRIVATE_KEY_PATH=./config/apple-auth-key.p8
APPLE_BUNDLE_ID_IOS=com.therapyrex.app
APPLE_BUNDLE_ID_WATCHOS=com.therapyrex.app.watchkitapp
```

## Complete Environment Configuration

Create `.env.local` file with all configuration values:

```bash
# ============================================================================
# JWT CONFIGURATION
# ============================================================================
# Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=your-secure-random-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# ============================================================================
# AUTHORIZED EMAILS (for Streamlit VIP access)
# ============================================================================
AUTHORIZED_EMAILS=m.fanelli1@icloud.com,maurofanellijr@gmail.com,mauro.fanelli@ctstate.edu,johndawalka@icloud.com,cooljack87@icloud.com,jdwalka@pm.me

# ============================================================================
# MICROSOFT AZURE AD (for @ctstate.edu institutional SSO)
# ============================================================================
AZURE_TENANT_ID=your-tenant-id-from-azure-portal
AZURE_CLIENT_ID=your-client-id-from-azure-portal
AZURE_CLIENT_SECRET=your-client-secret-from-azure-portal
AZURE_AUTHORITY=https://login.microsoftonline.com/common
AZURE_SCOPES=User.Read email profile openid offline_access
INSTITUTIONAL_EMAIL_DOMAIN=ctstate.edu

# Redirect URIs for each platform
AZURE_REDIRECT_URI_IOS=msauth.com.therapyrex.app://auth
AZURE_REDIRECT_URI_WINDOWS=http://localhost:3000/auth/callback
AZURE_REDIRECT_URI_WEB=http://localhost:8501/auth/callback

# ============================================================================
# GOOGLE OAUTH 2.0 (for @gmail.com accounts and GCP)
# ============================================================================
GOOGLE_CLOUD_PROJECT_ID=your-project-id-from-gcp
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-from-gcp
GOOGLE_OAUTH_SCOPES=openid email profile https://www.googleapis.com/auth/devstorage.read_write

# Google Cloud Storage
GOOGLE_STORAGE_BUCKET_NAME=poker-therapist-data-unique-suffix
GOOGLE_STORAGE_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./config/google-service-account.json

# Redirect URIs
GOOGLE_REDIRECT_URI_IOS=com.googleusercontent.apps.your-client-id:/oauth2callback
GOOGLE_REDIRECT_URI_WINDOWS=http://localhost:3000/google/callback
GOOGLE_REDIRECT_URI_WEB=http://localhost:8501/google/callback

# ============================================================================
# APPLE SIGN-IN (for @icloud.com accounts)
# ============================================================================
APPLE_TEAM_ID=your-10-char-team-id
APPLE_SERVICES_ID=com.therapyrex.signin
APPLE_KEY_ID=your-key-id
APPLE_PRIVATE_KEY_PATH=./config/apple-auth-key.p8
APPLE_BUNDLE_ID_IOS=com.therapyrex.app
APPLE_BUNDLE_ID_WATCHOS=com.therapyrex.app.watchkitapp

# ============================================================================
# AUTHENTICATION SETTINGS
# ============================================================================
ENABLE_MICROSOFT_AUTH=true
ENABLE_GOOGLE_AUTH=true
ENABLE_APPLE_AUTH=true
DEFAULT_AUTH_PROVIDER=microsoft
REQUIRE_AUTHENTICATION=true
SESSION_TIMEOUT_HOURS=24
REFRESH_TOKEN_EXPIRATION_DAYS=30

# ============================================================================
# SECURITY SETTINGS
# ============================================================================
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8501
FORCE_HTTPS=false
RATE_LIMIT_PER_MINUTE=60
```

## End-to-End Verification

### Test 1: Streamlit Web Application

```bash
# 1. Start the application
streamlit run chatbot_app.py

# 2. Open browser to http://localhost:8501

# 3. Test authorized iCloud email
#    - Select "m.fanelli1@icloud.com" from dropdown
#    - Verify "✅ Logged in as: m.fanelli1@icloud.com 🎰 (Authorized User)"
#    - Verify "🎰 VIP Access: Full voice and Rex personality features enabled"

# 4. Test authorized Gmail email
#    - Select "maurofanellijr@gmail.com" from dropdown
#    - Verify VIP access badge appears

# 5. Test institutional email
#    - Select "mauro.fanelli@ctstate.edu" from dropdown
#    - Verify VIP access badge appears

# 6. Test custom email
#    - Choose "Enter custom email"
#    - Enter "test@example.com"
#    - Verify login succeeds but no VIP badge

# 7. Test chat functionality
#    - Send a message to the chatbot
#    - Verify response is generated
#    - Check that message history is saved
```

### Test 2: Backend OAuth APIs (Optional)

```bash
# 1. Start backend server
cd /home/runner/work/Poker-Therapist/Poker-Therapist
uvicorn backend.api.main:app --reload --port 8000

# 2. Test Microsoft OAuth
curl http://localhost:8000/auth/microsoft/authorize
# Should return authorization URL

# 3. Test Google OAuth
curl http://localhost:8000/auth/google/authorize
# Should return authorization URL

# 4. Test Apple OAuth
curl http://localhost:8000/auth/apple/authorize
# Should return authorization URL
```

### Test 3: Google Cloud Storage (Optional)

```bash
# Test service account access
python << 'EOF'
import os
from google.cloud import storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './config/google-service-account.json'
client = storage.Client()

# List buckets to verify access
buckets = list(client.list_buckets())
print(f"✅ Successfully authenticated! Found {len(buckets)} bucket(s)")
for bucket in buckets:
    print(f"  - {bucket.name}")
EOF
```

### Test 4: CI/CD and Automated Workflows

For deployment environments (staging, production), verify:

1. **Environment Variables Set**:
   - All credentials available as environment variables
   - No secrets in source code or committed files

2. **GitHub Actions Secrets** (if using GitHub):
   - Add repository secrets for each credential
   - Test workflow runs with authentication

3. **Container Deployments**:
   - Verify secret injection into containers
   - Test API endpoints with auth headers

4. **Vercel/Serverless Deployments**:
   - Add environment variables in deployment platform
   - Test authentication from deployed URLs

## Troubleshooting

### "Email validation failed"
- **Cause**: Email doesn't contain `@` or domain doesn't have `.`
- **Solution**: Use valid email format (user@domain.com)

### "Not authorized for VIP features"
- **Cause**: Email not in AUTHORIZED_EMAILS list
- **Solution**: 
  - Add email to `AUTHORIZED_EMAILS` in `.env.local`
  - Or modify `_DEFAULT_AUTHORIZED_EMAILS` in `chatbot_app.py`
  - Restart application

### "Microsoft OAuth redirect_uri mismatch"
- **Cause**: Redirect URI in code doesn't match Azure portal
- **Solution**: 
  - Check Azure Portal → App registration → Authentication
  - Ensure exact URI match (including http/https, port, path)
  - No trailing slashes

### "Google OAuth redirect_uri_mismatch"
- **Cause**: Redirect URI not added to Google Cloud Console
- **Solution**:
  - Go to GCP Console → APIs & Services → Credentials
  - Edit OAuth 2.0 Client ID
  - Add exact redirect URI to "Authorized redirect URIs"

### "Apple Sign-In invalid_client"
- **Cause**: Services ID not properly configured
- **Solution**:
  - Verify Services ID has Sign in with Apple enabled
  - Check return URLs match exactly
  - Ensure primary App ID is set correctly

### "Service account authentication failed"
- **Cause**: JSON file path incorrect or file invalid
- **Solution**:
  - Verify `GOOGLE_APPLICATION_CREDENTIALS` path is correct
  - Check JSON file exists and is valid
  - Ensure service account has proper IAM roles

### "Token expired immediately"
- **Cause**: System clock out of sync
- **Solution**:
  - Check system time is correct
  - Verify timezone settings
  - Check `JWT_EXPIRATION_HOURS` configuration

## Security Checklist

- [ ] All secrets stored in `.env.local` (NOT `.env`)
- [ ] `.env.local` added to `.gitignore`
- [ ] Service account JSON files NOT committed to git
- [ ] Private key files (.p8) NOT committed to git
- [ ] Strong JWT secret key generated
- [ ] Separate credentials for dev/staging/production
- [ ] Client secrets rotated every 12-24 months
- [ ] HTTPS enabled in production (`FORCE_HTTPS=true`)
- [ ] CORS properly configured (no wildcard `*` in production)
- [ ] Rate limiting enabled
- [ ] Admin consent granted for Microsoft scopes
- [ ] Google OAuth consent screen verified (for production)
- [ ] All test users removed from OAuth consent screen before production

## Support and Resources

### Official Documentation
- **Microsoft Identity Platform**: https://docs.microsoft.com/azure/active-directory/develop/
- **Google Sign-In**: https://developers.google.com/identity
- **Apple Sign-In**: https://developer.apple.com/sign-in-with-apple/
- **Google Cloud Storage**: https://cloud.google.com/storage/docs

### Internal Documentation
- `AUTHENTICATION_SETUP.md` - Detailed OAuth setup guide
- `AUTH_QUICKSTART.md` - Quick environment setup
- `.env.example` - Complete environment variable template
- `GOOGLE_CLOUD_SETUP.md` - GCP-specific guide

### Contact
For institutional SSO configuration (ctstate.edu), contact your IT department with this documentation.

For application-specific issues, refer to the repository maintainers.

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-18  
**Author**: Copilot Workspace  
**Purpose**: Authentication configuration and verification for Poker Therapist
