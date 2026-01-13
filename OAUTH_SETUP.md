# OAuth/SSO Authentication Setup Guide

This guide explains how to configure OAuth 2.0 and OpenID Connect authentication for Poker Therapist, including support for:
- **Microsoft Azure AD / Windows Accounts** (Institutional SSO)
- **Google OAuth 2.0 / OpenID Connect**
- **Apple Sign In** (Optional)

## Overview

The Poker Therapist application now supports OAuth/SSO authentication through multiple identity providers. This enables secure authentication using your organization's Microsoft Windows account, Google account, or Apple ID instead of simple email-based authentication.

## Prerequisites

- Python 3.12+ with required dependencies installed
- Access to the respective developer portals for each provider you want to configure
- A publicly accessible redirect URI (or use localhost for development)

## Installation

Install the authentication dependencies:

```bash
pip install -r requirements.txt
```

The following OAuth libraries will be installed:
- `authlib` - OAuth/OIDC client library
- `msal` - Microsoft Authentication Library
- `google-auth` - Google authentication library
- `PyJWT` - JWT token handling

## Configuration

### 1. Microsoft Azure AD / Windows Account Setup

This is ideal for institutional SSO (e.g., ctstate.edu accounts).

#### Step 1: Register Application in Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Configure your app:
   - **Name**: Poker Therapist
   - **Supported account types**: 
     - Choose "Accounts in any organizational directory" for multi-tenant
     - Or "Accounts in this organizational directory only" for single-tenant (e.g., ctstate.edu only)
   - **Redirect URI**: 
     - Type: Web
     - URI: `http://localhost:8501/` (for development) or your production URL
5. Click **Register**

#### Step 2: Configure API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission** → **Microsoft Graph** → **Delegated permissions**
3. Add the following permissions:
   - `User.Read`
   - `openid`
   - `email`
   - `profile`
4. Click **Add permissions**
5. Click **Grant admin consent** (if you have admin rights)

#### Step 3: Create Client Secret

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Add a description (e.g., "Poker Therapist Production")
4. Choose an expiration period
5. Click **Add**
6. **Important**: Copy the secret **Value** immediately (you won't be able to see it again)

#### Step 4: Configure Environment Variables

Add to your `.env` or `.env.local` file:

```bash
# Microsoft Azure AD Configuration
MICROSOFT_CLIENT_ID=your-application-id-from-overview-page
MICROSOFT_CLIENT_SECRET=your-client-secret-value
MICROSOFT_TENANT_ID=common
# For institutional SSO, use your organization's tenant ID:
# MICROSOFT_TENANT_ID=12345678-1234-1234-1234-123456789abc
MICROSOFT_REDIRECT_URI=http://localhost:8501/
```

**Finding your Tenant ID:**
- For single-tenant (institutional): Copy the **Directory (tenant) ID** from the app's Overview page
- For multi-tenant: Use `common`
- For ctstate.edu: Contact your IT department or find it in your Azure AD settings

### 2. Google OAuth 2.0 Setup

This enables sign-in with Google accounts and access to Google Cloud Platform APIs.

#### Step 1: Create OAuth 2.0 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth client ID**
5. If prompted, configure the OAuth consent screen first:
   - User Type: External (for public access) or Internal (for organization only)
   - App name: Poker Therapist
   - Support email: Your email
   - Scopes: Add `userinfo.email`, `userinfo.profile`, and `openid`
   - Test users: Add your email addresses
6. Create OAuth client ID:
   - Application type: **Web application**
   - Name: Poker Therapist
   - Authorized redirect URIs: `http://localhost:8501/` (for development)

#### Step 2: Download Credentials

1. After creating the OAuth client, copy the **Client ID** and **Client Secret**
2. Alternatively, download the JSON file for reference

#### Step 3: Configure Environment Variables

Add to your `.env` or `.env.local` file:

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8501/
```

### 3. Apple Sign In Setup (Optional)

This enables sign-in with Apple ID.

**⚠️ PRODUCTION WARNING**: The current implementation decodes Apple ID tokens without signature verification. This is acceptable for development and testing but **must be enhanced** for production use by implementing proper JWT signature verification using Apple's public keys. See the TODO comment in `python_src/services/auth_service.py` for details.

#### Step 1: Configure App ID and Service ID

1. Go to [Apple Developer Portal](https://developer.apple.com)
2. Navigate to **Certificates, Identifiers & Profiles**
3. Create an **App ID**:
   - Description: Poker Therapist
   - Bundle ID: com.yourcompany.pokertherapist
   - Enable **Sign In with Apple**
4. Create a **Services ID**:
   - Description: Poker Therapist Web
   - Identifier: com.yourcompany.pokertherapist.web
   - Enable **Sign In with Apple**
   - Configure:
     - Primary App ID: Select your App ID from step 3
     - Domains: Your domain (or localhost for testing)
     - Return URLs: `http://localhost:8501/`

#### Step 2: Create Private Key

1. Go to **Keys** in the developer portal
2. Click **+** to create a new key
3. Name: Poker Therapist Sign In
4. Enable **Sign In with Apple**
5. Configure: Select your Primary App ID
6. Click **Continue** and **Register**
7. **Download** the `.p8` private key file (you can only download once)
8. Note the **Key ID**

#### Step 3: Configure Environment Variables

Add to your `.env` or `.env.local` file:

```bash
# Apple Sign In Configuration
APPLE_CLIENT_ID=com.yourcompany.pokertherapist.web
APPLE_TEAM_ID=your-team-id-from-membership-page
APPLE_KEY_ID=your-key-id-from-step-2
APPLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
your-private-key-content-here
-----END PRIVATE KEY-----"
APPLE_REDIRECT_URI=http://localhost:8501/
```

### 4. JWT Session Configuration

Generate a secure secret key for JWT token signing:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add to your `.env` or `.env.local` file:

```bash
# JWT Session Configuration
JWT_SECRET_KEY=your-generated-secure-random-key
SESSION_TIMEOUT_MINUTES=60
```

## Usage

### In Streamlit Application

The authentication is automatically integrated into the chatbot application. When you run the app:

```bash
streamlit run chatbot_app.py
```

Users will see OAuth login buttons for each configured provider. The authentication flow:

1. User clicks "Sign in with Microsoft/Google/Apple"
2. User is redirected to the provider's login page
3. User authenticates and grants permissions
4. User is redirected back to the application
5. Application receives and validates the OAuth token
6. User information is stored in session
7. User can access the application features

### Programmatic Usage

You can also use the authentication service programmatically:

```python
from python_src.services.auth_service import AuthenticationService, AuthConfig

# Initialize with environment variables
auth_service = AuthenticationService()

# Or with custom configuration
config = AuthConfig(
    microsoft_client_id="your-client-id",
    microsoft_client_secret="your-secret",
    # ... other configuration
)
auth_service = AuthenticationService(config)

# Get available providers
providers = auth_service.get_available_providers()
print(f"Available providers: {providers}")

# Microsoft authentication example
if auth_service.microsoft:
    auth_url, state = auth_service.microsoft.get_authorization_url()
    print(f"Microsoft login URL: {auth_url}")
    
    # After user authenticates and you receive the code:
    user_info = auth_service.microsoft.get_user_info(auth_code)
    if user_info:
        # Create session token
        session_token = auth_service.create_session_token(user_info)
        print(f"Session token: {session_token}")
```

## Production Deployment

### Security Considerations

1. **Use HTTPS**: Always use HTTPS in production for redirect URIs
2. **Secure Secrets**: Never commit secrets to version control
3. **Environment Variables**: Use secure secret management (e.g., Azure Key Vault, AWS Secrets Manager)
4. **Token Validation**: JWT tokens are validated on each request
5. **Session Timeout**: Configure appropriate session timeout (default: 60 minutes)

### Redirect URI Configuration

For production deployment, update redirect URIs in all provider portals:

**Microsoft Azure:**
- Go to **Authentication** in your app registration
- Add your production URL (e.g., `https://poker-therapist.vercel.app/`)

**Google Cloud:**
- Go to **Credentials** → Edit your OAuth client
- Add authorized redirect URI (e.g., `https://poker-therapist.vercel.app/`)

**Apple:**
- Go to your Services ID configuration
- Update Return URLs with your production URL

### Vercel Deployment

If deploying to Vercel, add environment variables in the Vercel dashboard:

1. Go to your project settings
2. Navigate to **Environment Variables**
3. Add all OAuth configuration variables
4. Redeploy your application

## Troubleshooting

### "OAuth provider not configured" error

**Cause**: Environment variables are not set correctly.

**Solution**: Verify that you've set the required environment variables for at least one provider.

### "Invalid redirect URI" error

**Cause**: The redirect URI in your code doesn't match the one registered in the provider portal.

**Solution**: Ensure the redirect URIs match exactly (including trailing slashes).

### "Invalid state parameter" error

**Cause**: State parameter mismatch, possible CSRF attack or session expired.

**Solution**: This is a security feature. Clear your browser session and try again.

### Microsoft: "AADSTS50011: The reply URL does not match"

**Cause**: Redirect URI mismatch.

**Solution**: 
1. Check the error message for the actual redirect URI being used
2. Add this exact URI to your app registration in Azure Portal
3. Ensure no extra characters or different protocols (http vs https)

### Google: "redirect_uri_mismatch"

**Cause**: Redirect URI not authorized.

**Solution**:
1. Go to Google Cloud Console → Credentials
2. Edit your OAuth client
3. Add the exact redirect URI shown in the error

### Apple: "invalid_client" error

**Cause**: Client secret generation failed or expired.

**Solution**:
1. Verify your Team ID, Key ID, and Private Key are correct
2. Ensure the private key file content is properly formatted
3. Check that the Services ID is correctly configured

## Testing

### Local Testing

1. Set up at least one OAuth provider (Microsoft or Google recommended)
2. Configure localhost redirect URI (`http://localhost:8501/`)
3. Run the application: `streamlit run chatbot_app.py`
4. Click the OAuth login button
5. Authenticate with your provider
6. Verify you're redirected back and logged in

### Test Users

For testing:
- **Microsoft**: Use test accounts in your organization
- **Google**: Add test users in the OAuth consent screen configuration
- **Apple**: Use your personal Apple ID or create a test account

## Integration with Existing Features

The OAuth authentication integrates seamlessly with existing features:

1. **Voice Features**: Authorized users (configured in `AUTHORIZED_EMAILS`) get full Rex voice features
2. **Chat History**: User sessions are tracked by OAuth email address
3. **VIP Access**: Map OAuth emails to VIP status based on email domain or specific addresses

## Support

For issues or questions:
1. Check this documentation first
2. Review provider-specific documentation:
   - [Microsoft Identity Platform](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
   - [Google Identity](https://developers.google.com/identity)
   - [Sign in with Apple](https://developer.apple.com/sign-in-with-apple/)
3. Open an issue on GitHub

## References

- [OAuth 2.0 Specification](https://oauth.net/2/)
- [OpenID Connect Specification](https://openid.net/connect/)
- [Microsoft Authentication Library (MSAL)](https://github.com/AzureAD/microsoft-authentication-library-for-python)
- [Authlib Documentation](https://docs.authlib.org/)
