# Authentication Setup Guide

This guide explains how to configure authentication and SSO for the Poker Therapist application.

## Overview

The application supports multiple authentication methods:

1. **Microsoft Azure AD** - For Windows accounts and institutional SSO
2. **Google OAuth 2.0** - For Google accounts and GCP API access
3. **Institutional Email SSO** - For university/organization accounts (e.g., ctstate.edu)

## Prerequisites

- Microsoft Azure account (for Azure AD)
- Google Cloud account (for Google OAuth)
- Institutional email domain verified

## Microsoft Azure AD Setup

### Step 1: Register Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Enter details:
   - **Name**: Poker Therapist
   - **Supported account types**: "Accounts in any organizational directory"
   - **Redirect URI**: 
     - Type: Web
     - URL: `https://your-app.vercel.app/auth/callback/microsoft`
5. Click "Register"

### Step 2: Configure Authentication

1. Go to "Authentication" in your app registration
2. Under "Implicit grant and hybrid flows":
   - ✅ Enable "ID tokens"
3. Under "Supported account types":
   - Select "Accounts in any organizational directory (Any Azure AD directory - Multitenant)"
4. Click "Save"

### Step 3: Create Client Secret

1. Go to "Certificates & secrets"
2. Click "New client secret"
3. Description: "Poker Therapist API"
4. Expires: 24 months (recommended)
5. Click "Add"
6. **Copy the secret value immediately** (it won't be shown again)

### Step 4: Configure API Permissions

1. Go to "API permissions"
2. Add these Microsoft Graph permissions:
   - `User.Read` (Delegated)
   - `email` (Delegated)
   - `openid` (Delegated)
   - `profile` (Delegated)
3. Click "Grant admin consent" (if you're admin)

### Step 5: Get Configuration Values

You'll need these values from the Overview page:

- **Application (client) ID**: `12345678-1234-1234-1234-123456789abc`
- **Directory (tenant) ID**: `87654321-4321-4321-4321-cba987654321`
- **Client secret**: (from Step 3)

## Google OAuth Setup

### Step 1: Create OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project (or create one)
3. Go to "APIs & Services" → "Credentials"
4. Click "Create Credentials" → "OAuth client ID"

### Step 2: Configure OAuth Consent Screen

1. Click "Configure Consent Screen"
2. Select "External" user type
3. Fill in application information:
   - **App name**: Poker Therapist
   - **User support email**: Your email
   - **Developer contact**: Your email
4. Add scopes:
   - `openid`
   - `email`
   - `profile`
   - `https://www.googleapis.com/auth/cloud-platform` (for GCP API access)
5. Add test users (if in testing mode)
6. Click "Save and Continue"

### Step 3: Create OAuth Client

1. Application type: "Web application"
2. Name: "Poker Therapist Web"
3. Authorized redirect URIs:
   - `https://your-app.vercel.app/auth/callback/google`
   - `http://localhost:8000/auth/callback/google` (for development)
4. Click "Create"

### Step 4: Get Configuration Values

You'll receive:

- **Client ID**: `123456789-abc123.apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-abc123xyz`

## Environment Configuration

### Development (.env.local)

```bash
# Microsoft Azure AD
AZURE_TENANT_ID=87654321-4321-4321-4321-cba987654321
AZURE_CLIENT_ID=12345678-1234-1234-1234-123456789abc
AZURE_CLIENT_SECRET=your-azure-client-secret
AZURE_REDIRECT_URI=http://localhost:8000/auth/callback/microsoft

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=123456789-abc123.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-abc123xyz
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback/google

# Session Configuration
SESSION_SECRET_KEY=generate-with-python-secrets-token-hex-32
AUTHENTICATION_ENABLED=true

# Institutional Email Domains (comma-separated)
INSTITUTIONAL_EMAIL_DOMAINS=ctstate.edu,example.edu
```

### Production (Vercel)

Add these environment variables in Vercel dashboard:

1. Go to Project Settings → Environment Variables
2. Add each variable with production values:

```
AZURE_TENANT_ID=...
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...
AZURE_REDIRECT_URI=https://your-app.vercel.app/auth/callback/microsoft
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
GOOGLE_OAUTH_REDIRECT_URI=https://your-app.vercel.app/auth/callback/google
SESSION_SECRET_KEY=...
AUTHENTICATION_ENABLED=true
INSTITUTIONAL_EMAIL_DOMAINS=ctstate.edu
```

### Generate Session Secret

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Authentication Flow

### Microsoft SSO Flow

```
1. User clicks "Login with Microsoft"
   ↓
2. Redirect to Microsoft login page
   ↓
3. User enters institutional email (e.g., user@ctstate.edu)
   ↓
4. Microsoft authenticates user
   ↓
5. Redirect back to app with authorization code
   ↓
6. App exchanges code for access token
   ↓
7. App verifies institutional email domain
   ↓
8. App creates JWT token for user
   ↓
9. User is authenticated
```

### Google OAuth Flow

```
1. User clicks "Login with Google"
   ↓
2. Redirect to Google login page
   ↓
3. User selects Google account
   ↓
4. Google shows permission consent screen
   ↓
5. User grants permissions
   ↓
6. Redirect back to app with authorization code
   ↓
7. App exchanges code for access token
   ↓
8. App validates user email (authorized list or institutional domain)
   ↓
9. App creates JWT token for user
   ↓
10. User is authenticated with GCP API access
```

## Using Authentication in API Requests

### Frontend JavaScript Example

```javascript
// Login with Microsoft
async function loginMicrosoft() {
  window.location.href = '/auth/login/microsoft';
}

// Login with Google
async function loginGoogle() {
  window.location.href = '/auth/login/google';
}

// Make authenticated API request
async function makeAuthenticatedRequest() {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('/api/triage', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      emotion: 'frustrated',
      intensity: 7
    })
  });
  
  return response.json();
}

// Handle auth callback (after redirect)
async function handleAuthCallback() {
  const urlParams = new URLSearchParams(window.location.search);
  const accessToken = urlParams.get('access_token');
  
  if (accessToken) {
    localStorage.setItem('access_token', accessToken);
    window.location.href = '/dashboard';
  }
}
```

### Python/Streamlit Example

```python
import streamlit as st
import requests

# Login button
if st.button("Login with Microsoft"):
    st.markdown(f'<a href="/auth/login/microsoft">Click here to login</a>', 
                unsafe_allow_html=True)

# Make authenticated request
def make_authenticated_request(token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        'https://your-app.vercel.app/api/triage',
        headers=headers,
        json={
            'emotion': 'frustrated',
            'intensity': 7
        }
    )
    
    return response.json()
```

## Testing Authentication

### Test Microsoft SSO

```bash
# Start local server
uvicorn backend.api.main:app --reload --port 8000

# Open in browser
http://localhost:8000/auth/login/microsoft
```

### Test Google OAuth

```bash
# Open in browser
http://localhost:8000/auth/login/google
```

### Test Protected Endpoint

```bash
# Get token from login flow
TOKEN="your-jwt-token-here"

# Make authenticated request
curl -X POST http://localhost:8000/api/triage \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"emotion": "frustrated", "intensity": 7}'
```

## Security Considerations

### Token Management

- ✅ Store tokens securely (httpOnly cookies preferred)
- ✅ Use HTTPS in production
- ✅ Set token expiration (24 hours recommended)
- ✅ Implement token refresh mechanism
- ❌ Don't store tokens in localStorage (XSS vulnerable)

### Secret Management

- ✅ Use environment variables for all secrets
- ✅ Rotate secrets regularly (every 90 days)
- ✅ Use different secrets for dev/staging/prod
- ❌ Never commit secrets to Git
- ❌ Never share secrets in chat/email

### Permission Validation

- ✅ Verify email domains server-side
- ✅ Check user permissions on every request
- ✅ Implement rate limiting
- ✅ Log authentication attempts
- ❌ Don't trust client-side validation

## Disabling Authentication (Development)

For local development, you can disable authentication:

```bash
# In .env.local
AUTHENTICATION_ENABLED=false
```

This will allow all requests without authentication.

⚠️ **Never disable authentication in production!**

## Troubleshooting

### "Invalid redirect URI" Error

**Solution**: Make sure redirect URI in Azure/Google matches exactly (including https vs http).

### "Access Denied" Error

**Solution**: Check that user's email is in authorized list or matches institutional domain.

### "Token Expired" Error

**Solution**: Implement token refresh or have user re-authenticate.

### CORS Issues

**Solution**: Add your frontend URL to CORS allowed origins in `backend/api/main.py`.

## Multi-Factor Authentication (MFA)

Both Microsoft and Google support MFA:

### Microsoft Azure AD MFA

1. Go to Azure AD → "Security" → "MFA"
2. Enable MFA for your organization
3. Users will be prompted for second factor on login

### Google 2-Step Verification

1. Users enable it in their Google Account settings
2. They'll need to verify on each new device

## Single Sign-On (SSO) for Organizations

### For IT Administrators

To enable SSO for your organization:

1. **Microsoft**: Use Azure AD Connect to sync on-premises directory
2. **Google**: Use Google Workspace for centralized management
3. Configure conditional access policies
4. Set up group-based access control

### Institutional Email Domains

Add your organization's email domain to allowed list:

```bash
INSTITUTIONAL_EMAIL_DOMAINS=university.edu,school.edu,company.com
```

Only users with these email domains can authenticate via Microsoft SSO.

## Additional Resources

- [Microsoft Identity Platform Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

## Support

For authentication issues:
- Check application logs in Vercel
- Review Azure AD sign-in logs
- Check Google OAuth consent screen status
- Verify environment variables are set correctly
