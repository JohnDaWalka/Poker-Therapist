# Authentication Setup Guide

This guide will help you configure authentication for the Poker Therapist application across all platforms (iOS, Windows, web) using Microsoft accounts, Google OAuth 2.0, and Apple Sign-In.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Microsoft Azure AD Setup](#microsoft-azure-ad-setup)
3. [Google Cloud Platform Setup](#google-cloud-platform-setup)
4. [Apple Developer Setup](#apple-developer-setup)
5. [Environment Configuration](#environment-configuration)
6. [Platform-Specific Setup](#platform-specific-setup)
7. [Testing Authentication](#testing-authentication)
8. [Security Best Practices](#security-best-practices)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have:

- Active Microsoft Azure account (for institutional SSO and Windows authentication)
- Google Cloud Platform account (for Google OAuth and cloud services)
- Apple Developer account (for iOS/macOS/watchOS apps)
- Access to your institution's IT department (for SSO configuration)

## Microsoft Azure AD Setup

### 1. Register Your Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations** → **New registration**
3. Fill in the application details:
   - **Name**: Poker Therapist
   - **Supported account types**: 
     - For institutional SSO only: "Accounts in this organizational directory only"
     - For multi-tenant: "Accounts in any organizational directory"
     - For personal Microsoft accounts: Include "Personal Microsoft accounts"
   - **Redirect URI**: 
     - Platform: Web, URI: `http://localhost:8501/auth/callback` (for Streamlit)
     - Platform: Single-page application, URI: `http://localhost:3000/auth/callback` (for Windows app)

4. Click **Register**

### 2. Configure Redirect URIs

After registration, go to **Authentication** and add all platform redirect URIs:

- **iOS**: `msauth.com.therapyrex.app://auth`
- **Windows Desktop**: `http://localhost:3000/auth/callback`
- **Web (Streamlit)**: `http://localhost:8501/auth/callback`
- **Production Web**: `https://your-domain.com/auth/callback`

For iOS, add the following to your app's **Info.plist**:
```xml
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>msauth.com.therapyrex.app</string>
        </array>
    </dict>
</array>
```

### 3. Create Client Secret

1. Go to **Certificates & secrets** → **New client secret**
2. Add a description: "Poker Therapist Backend"
3. Set expiration (recommended: 24 months maximum)
4. **IMPORTANT**: Copy the secret value immediately - it won't be shown again

### 4. Configure API Permissions

1. Go to **API permissions** → **Add a permission**
2. Select **Microsoft Graph**
3. Add the following **Delegated permissions**:
   - `User.Read`
   - `email`
   - `profile`
   - `openid`
   - `offline_access` (for refresh tokens)

4. Click **Grant admin consent** (requires admin privileges)

### 5. Configure Institutional SSO (if applicable)

If using institutional email (e.g., @ctstate.edu):

1. Work with your IT department to get the **Tenant ID**
2. Update the **Authority** URL to use your specific tenant:
   - `https://login.microsoftonline.com/{your-tenant-id}`
3. Ensure your app is registered in your organization's Azure AD

### 6. Collect Configuration Values

From the Azure Portal, collect:
- **Application (client) ID**: From Overview page
- **Directory (tenant) ID**: From Overview page
- **Client secret**: From step 3 (copy immediately)
- **Authority URL**: `https://login.microsoftonline.com/{tenant-id}`

Save these values - you'll need them for environment configuration.

## Google Cloud Platform Setup

### 1. Create a GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click **Select a project** → **New Project**
3. Name: "Poker Therapist"
4. Click **Create**

### 2. Enable Required APIs

1. Navigate to **APIs & Services** → **Library**
2. Enable the following APIs:
   - Google Identity Platform
   - Cloud Storage API
   - Cloud Identity API
   - (Optional) Cloud Speech-to-Text API
   - (Optional) Cloud Text-to-Speech API

### 3. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Configure the OAuth consent screen (if not done):
   - **User Type**: External (or Internal for G Suite/Workspace organizations)
   - **App name**: Poker Therapist
   - **User support email**: Your email
   - **Authorized domains**: Your domain(s)
   - **Scopes**: Add openid, email, profile
   - **Test users**: Add your email for testing

4. Create OAuth client ID for each platform:

   **For iOS:**
   - Application type: iOS
   - Name: Poker Therapist iOS
   - Bundle ID: `com.therapyrex.app`

   **For Web Application:**
   - Application type: Web application
   - Name: Poker Therapist Web
   - Authorized JavaScript origins: 
     - `http://localhost:8501`
     - `http://localhost:3000`
     - Your production domain
   - Authorized redirect URIs:
     - `http://localhost:8501/google/callback`
     - `http://localhost:3000/google/callback`
     - Your production callback URL

### 4. Create Service Account

For backend Google Cloud Storage access:

1. Go to **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Name: "poker-therapist-storage"
4. Grant roles:
   - Storage Admin (or Storage Object Admin for more restrictive access)
5. Click **Done**
6. Click on the service account → **Keys** → **Add Key** → **Create new key**
7. Choose **JSON** format
8. Save the JSON file securely (e.g., `config/google-service-account.json`)
9. **NEVER commit this file to version control**

### 5. Create Cloud Storage Bucket

1. Go to **Cloud Storage** → **Buckets** → **Create Bucket**
2. Name: `poker-therapist-data` (must be globally unique)
3. Location: Choose closest to your users (e.g., `us-central1`)
4. Storage class: Standard
5. Access control: Uniform
6. Protection tools: Enable as needed
7. Click **Create**

### 6. Configure Bucket Permissions

1. Select your bucket
2. Go to **Permissions**
3. Add your service account with **Storage Object Admin** role
4. Set uniform bucket-level access

### 7. Collect Configuration Values

Save these values:
- **Client ID** (for each platform)
- **Client Secret** (for web)
- **Project ID**: From project dashboard
- **Bucket Name**: From step 5
- **Service Account JSON**: File from step 4

## Apple Developer Setup

### 1. Register App IDs

1. Go to [Apple Developer Portal](https://developer.apple.com/account)
2. Navigate to **Certificates, Identifiers & Profiles** → **Identifiers**
3. Create App ID for iOS:
   - Description: Therapy Rex iOS
   - Bundle ID: `com.therapyrex.app`
   - Capabilities: Enable **Sign in with Apple**

4. Create App ID for watchOS:
   - Description: Therapy Rex Watch
   - Bundle ID: `com.therapyrex.app.watchkitapp`
   - Capabilities: Enable **Sign in with Apple**

### 2. Create Services ID

1. Click **+** → **Services IDs**
2. Description: Therapy Rex Sign In
3. Identifier: `com.therapyrex.signin`
4. Enable **Sign in with Apple**
5. Configure:
   - Primary App ID: Select your iOS App ID
   - Website URLs:
     - Domains: Your domain (e.g., `your-domain.com`)
     - Return URLs: Your callback URLs (e.g., `https://your-domain.com/auth/apple/callback`)

### 3. Create Private Key

1. Go to **Keys** → **+**
2. Key Name: Therapy Rex Sign In Key
3. Enable **Sign in with Apple**
4. Configure: Select your primary App ID
5. Click **Continue** → **Register**
6. **Download the .p8 file** - you cannot download it again
7. Note the **Key ID**

### 4. Collect Configuration Values

Save these values:
- **Team ID**: From membership page
- **Services ID**: From step 2
- **Key ID**: From step 3
- **Private Key (.p8 file)**: From step 3
- **Bundle IDs**: From step 1

## Environment Configuration

Create a `.env.local` file (copy from `.env.example`) and fill in your values:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secure-random-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Microsoft Azure AD
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_AUTHORITY=https://login.microsoftonline.com/{tenant-id}
AZURE_SCOPES=User.Read email profile openid
INSTITUTIONAL_EMAIL_DOMAIN=ctstate.edu

# Redirect URIs
AZURE_REDIRECT_URI_IOS=msauth.com.therapyrex.app://auth
AZURE_REDIRECT_URI_WINDOWS=http://localhost:3000/auth/callback
AZURE_REDIRECT_URI_WEB=http://localhost:8501/auth/callback

# Google Cloud Platform
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_OAUTH_SCOPES=openid email profile https://www.googleapis.com/auth/devstorage.read_write

# Google Cloud Storage
GOOGLE_STORAGE_BUCKET_NAME=poker-therapist-data
GOOGLE_STORAGE_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./config/google-service-account.json

# Apple Sign-In
APPLE_TEAM_ID=your-team-id
APPLE_SERVICES_ID=com.therapyrex.signin
APPLE_KEY_ID=your-key-id
APPLE_PRIVATE_KEY_PATH=./config/apple-auth-key.p8
APPLE_BUNDLE_ID_IOS=com.therapyrex.app
APPLE_BUNDLE_ID_WATCHOS=com.therapyrex.app.watchkitapp

# Authentication Settings
ENABLE_MICROSOFT_AUTH=true
ENABLE_GOOGLE_AUTH=true
ENABLE_APPLE_AUTH=true
DEFAULT_AUTH_PROVIDER=microsoft
REQUIRE_AUTHENTICATION=true
```

**Security Note**: Never commit `.env.local` to version control. The `.gitignore` file should already exclude it.

## Platform-Specific Setup

### iOS Setup

1. Install CocoaPods dependencies:
   ```bash
   cd ios
   pod install
   ```

2. Open workspace (not .xcodeproj):
   ```bash
   open TherapyRex.xcworkspace
   ```

3. Add configuration to Info.plist:
   ```xml
   <key>AZURE_CLIENT_ID</key>
   <string>your-client-id</string>
   <key>AZURE_AUTHORITY</key>
   <string>https://login.microsoftonline.com/common</string>
   <key>AZURE_REDIRECT_URI_IOS</key>
   <string>msauth.com.therapyrex.app://auth</string>
   <key>GOOGLE_CLIENT_ID</key>
   <string>your-client-id.apps.googleusercontent.com</string>
   ```

4. Configure URL schemes in Info.plist (for OAuth callbacks):
   ```xml
   <key>CFBundleURLTypes</key>
   <array>
       <dict>
           <key>CFBundleURLSchemes</key>
           <array>
               <string>msauth.com.therapyrex.app</string>
               <string>com.googleusercontent.apps.your-client-id</string>
           </array>
       </dict>
   </array>
   ```

5. Add Sign in with Apple capability in Xcode:
   - Select project → Target → Signing & Capabilities
   - Click + → Sign in with Apple

### Windows Desktop Setup

1. Install dependencies:
   ```bash
   cd windows
   pnpm install
   # or
   npm install
   ```

2. Create `.env` file in windows directory with configuration

3. Update electron/main.js to handle OAuth callbacks

### Backend Setup

1. Install Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

2. Place your Google service account JSON in `config/google-service-account.json`

3. Place your Apple private key (.p8) in `config/apple-auth-key.p8`

4. Ensure these files are in `.gitignore`

## Testing Authentication

### Test Microsoft Authentication

1. Start the backend server:
   ```bash
   uvicorn backend.api.main:app --reload
   ```

2. Test the authorization URL:
   ```bash
   curl http://localhost:8000/auth/microsoft/authorize
   ```

3. Open the URL in a browser and complete the sign-in flow

### Test Google Authentication

1. Test the Google authorization URL:
   ```bash
   curl http://localhost:8000/auth/google/authorize
   ```

2. Sign in with your Google account

### Test iOS App

1. Build and run on simulator or device
2. Tap sign-in buttons
3. Verify authentication flows complete successfully
4. Check that tokens are stored securely in Keychain

### Test Windows App

1. Run in development mode:
   ```bash
   cd windows
   pnpm run electron:dev
   ```

2. Test sign-in flows
3. Verify tokens are stored securely

## Security Best Practices

### Credential Management

1. **Never commit secrets to version control**
   - Use `.env.local` for local development
   - Use environment variables or secret managers in production
   - Keep `.gitignore` updated

2. **Rotate credentials regularly**
   - Azure client secrets: Every 12-24 months
   - Service account keys: Annually
   - JWT secret key: Periodically

3. **Use separate credentials for each environment**
   - Development: Separate Azure app registration
   - Staging: Separate credentials
   - Production: Production-only credentials

### Token Security

1. **Store tokens securely**
   - iOS: Use Keychain Services
   - Windows: Use electron's safeStorage
   - Web: HttpOnly cookies (not localStorage)

2. **Implement token refresh**
   - Use refresh tokens to get new access tokens
   - Refresh before expiration (not after)

3. **Validate tokens server-side**
   - Always verify JWT signatures
   - Check expiration
   - Validate issuer and audience

### Network Security

1. **Use HTTPS in production**
   - Set `FORCE_HTTPS=true`
   - Use SSL certificates

2. **Implement rate limiting**
   - Prevent brute force attacks
   - Configure `RATE_LIMIT_PER_MINUTE`

3. **Configure CORS properly**
   - Whitelist specific origins
   - Don't use `*` in production

## Troubleshooting

### Microsoft Authentication Issues

**Error: AADSTS50011 - The redirect URI specified in the request does not match**
- Solution: Ensure redirect URI in code exactly matches Azure portal configuration
- Check for trailing slashes
- Verify platform type (Web vs SPA vs iOS)

**Error: AADSTS65001 - User consent required**
- Solution: Grant admin consent in Azure portal
- Go to API permissions → Grant admin consent

**iOS: Error opening MSAL login page**
- Solution: Check Info.plist URL schemes
- Verify redirect URI format: `msauth.{bundle-id}://auth`

### Google Authentication Issues

**Error: redirect_uri_mismatch**
- Solution: Add exact redirect URI to Google Cloud Console
- Check for http vs https
- Verify port numbers

**Error: Access blocked: Authorization Error**
- Solution: Configure OAuth consent screen
- Add test users during development
- Complete verification for production

### Apple Sign-In Issues

**Error: Invalid client**
- Solution: Verify Services ID is properly configured
- Check that Sign in with Apple is enabled for App ID
- Ensure return URLs match exactly

**Error: Invalid signature**
- Solution: Verify private key (.p8 file) is correct
- Check Key ID matches
- Ensure algorithm is ES256

### General Issues

**Tokens expire immediately**
- Solution: Check system clock
- Verify timezone settings
- Check JWT expiration configuration

**Authentication works locally but fails in production**
- Solution: Update redirect URIs for production domain
- Check environment variables are set
- Verify SSL certificates

**iOS Keychain access denied**
- Solution: Check Keychain Sharing capability
- Verify app signing
- Reset simulator if testing

## Support

For additional help:
- Microsoft MSAL docs: https://docs.microsoft.com/azure/active-directory/develop/
- Google Sign-In docs: https://developers.google.com/identity
- Apple Sign-In docs: https://developer.apple.com/sign-in-with-apple/

For institutional SSO setup, contact your IT department with this documentation.
