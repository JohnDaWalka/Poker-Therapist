# Vercel Authentication Setup Guide

This guide explains how to configure authentication environment variables in Vercel for the Poker Therapist application.

## Prerequisites

Before deploying to Vercel, you must:

1. ✅ Complete local authentication configuration using `CREDENTIAL_CONFIGURATION_GUIDE.md`
2. ✅ Test authentication locally using `scripts/verify_auth_config.py`
3. ✅ Have production credentials ready (separate from development)
4. ✅ Update redirect URIs in Azure and Google consoles to include your Vercel domain

## Required Vercel Environment Variables

### Core API Keys

```bash
# Required for chatbot functionality
OPENAI_API_KEY=sk-...
XAI_API_KEY=xai-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
AUTHORIZED_EMAILS=email1@domain.com,email2@domain.com
```

### Authentication - JWT Configuration

```bash
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=your-production-jwt-secret-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### Authentication - Microsoft Azure AD

```bash
# From Azure Portal (https://portal.azure.com)
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_AUTHORITY=https://login.microsoftonline.com/your-tenant-id
AZURE_SCOPES=User.Read email profile openid offline_access
INSTITUTIONAL_EMAIL_DOMAIN=ctstate.edu
AZURE_REDIRECT_URI_WEB=https://your-domain.vercel.app/auth/callback
```

### Authentication - Google OAuth 2.0 & GCP

```bash
# From Google Cloud Console (https://console.cloud.google.com)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_REDIRECT_URI_WEB=https://your-domain.vercel.app/google/callback
GOOGLE_OAUTH_SCOPES=openid email profile https://www.googleapis.com/auth/devstorage.read_write
```

### Google Cloud Storage

```bash
# Cloud Storage configuration
GOOGLE_STORAGE_BUCKET_NAME=poker-therapist-production
GOOGLE_STORAGE_REGION=us-central1

# Service account credentials (paste full JSON as single line)
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}
```

### Authentication - Apple Sign-In (Optional)

```bash
# From Apple Developer Portal (https://developer.apple.com)
APPLE_TEAM_ID=your-team-id
APPLE_SERVICES_ID=com.therapyrex.signin
APPLE_KEY_ID=your-key-id
APPLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----
APPLE_BUNDLE_ID_IOS=com.therapyrex.app
```

### Security Settings

```bash
# Authentication configuration
ENABLE_MICROSOFT_AUTH=true
ENABLE_GOOGLE_AUTH=true
ENABLE_APPLE_AUTH=true
DEFAULT_AUTH_PROVIDER=microsoft
REQUIRE_AUTHENTICATION=true

# Security policies
FORCE_HTTPS=true
CORS_ALLOWED_ORIGINS=https://your-domain.vercel.app
RATE_LIMIT_PER_MINUTE=60
SESSION_TIMEOUT_HOURS=24
REFRESH_TOKEN_EXPIRATION_DAYS=30
```

## Setup Methods

### Method 1: Vercel CLI (Recommended)

Install Vercel CLI:
```bash
npm install -g vercel
```

Login to Vercel:
```bash
vercel login
```

Set environment variables:
```bash
# Core API keys
vercel env add OPENAI_API_KEY production
vercel env add XAI_API_KEY production
vercel env add ANTHROPIC_API_KEY production
vercel env add GOOGLE_API_KEY production
vercel env add AUTHORIZED_EMAILS production

# JWT
vercel env add JWT_SECRET_KEY production

# Microsoft Azure AD
vercel env add AZURE_TENANT_ID production
vercel env add AZURE_CLIENT_ID production
vercel env add AZURE_CLIENT_SECRET production

# Google OAuth
vercel env add GOOGLE_CLIENT_ID production
vercel env add GOOGLE_CLIENT_SECRET production
vercel env add GOOGLE_CLOUD_PROJECT_ID production

# Google Cloud Storage
vercel env add GOOGLE_STORAGE_BUCKET_NAME production
vercel env add GOOGLE_SERVICE_ACCOUNT_JSON production

# Optional: Apple Sign-In
vercel env add APPLE_TEAM_ID production
vercel env add APPLE_SERVICES_ID production
vercel env add APPLE_KEY_ID production
vercel env add APPLE_PRIVATE_KEY production

# Security
vercel env add ENABLE_MICROSOFT_AUTH production
vercel env add ENABLE_GOOGLE_AUTH production
vercel env add FORCE_HTTPS production
vercel env add CORS_ALLOWED_ORIGINS production
```

For each command, you'll be prompted to enter the value. Use `production` environment for live deployment, `preview` for staging branches, and `development` for local development.

### Method 2: Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add each variable:
   - **Name**: Variable name (e.g., `AZURE_CLIENT_ID`)
   - **Value**: The actual value
   - **Environment**: Select `Production`, `Preview`, or `Development`
5. Click **Save**

### Method 3: Import from .env File

Create a `.env.production` file (DO NOT commit this):

```bash
# Copy from .env.example and fill with production values
cp .env.example .env.production
# Edit .env.production with production credentials
```

Then import:
```bash
vercel env pull .env.vercel
# Manually copy values from .env.production to Vercel dashboard
```

## Vercel Secrets Configuration

For sensitive values, use Vercel Secrets (referenced in vercel.json):

```bash
# Create secrets (only once per Vercel account)
vercel secrets add xai_api_key "xai-your-key"
vercel secrets add openai_api_key "sk-your-key"
vercel secrets add anthropic_api_key "sk-ant-your-key"
vercel secrets add google_api_key "AIza-your-key"
vercel secrets add authorized_emails "email1@domain.com,email2@domain.com"

# Authentication secrets
vercel secrets add jwt_secret_key "your-jwt-secret"
vercel secrets add azure_tenant_id "your-tenant-id"
vercel secrets add azure_client_id "your-client-id"
vercel secrets add azure_client_secret "your-client-secret"
vercel secrets add google_client_id "your-client-id.apps.googleusercontent.com"
vercel secrets add google_client_secret "your-client-secret"
vercel secrets add google_cloud_project_id "your-project-id"
vercel secrets add google_storage_bucket_name "poker-therapist-production"
vercel secrets add google_service_account_json '{"type":"service_account",...}'
```

**Note**: Secrets are account-wide. Use environment variables for project-specific configuration.

## Update Provider Redirect URIs

### Microsoft Azure AD

1. Go to https://portal.azure.com
2. Navigate to **Azure Active Directory** → **App registrations** → Your app
3. Go to **Authentication** → **Platform configurations** → **Web**
4. Add redirect URI: `https://your-domain.vercel.app/auth/callback`
5. Click **Save**

### Google Cloud Platform

1. Go to https://console.cloud.google.com
2. Navigate to **APIs & Services** → **Credentials**
3. Click your OAuth 2.0 Client ID
4. Under **Authorized redirect URIs**, add: `https://your-domain.vercel.app/google/callback`
5. Click **Save**

### Apple Developer Portal

1. Go to https://developer.apple.com/account
2. Navigate to **Certificates, Identifiers & Profiles** → **Identifiers** → Your Services ID
3. Configure **Sign in with Apple** → **Return URLs**
4. Add: `https://your-domain.vercel.app/apple/callback`
5. Click **Save**

## Deployment Process

### Initial Deployment

```bash
# Deploy to production
vercel --prod

# Or deploy with environment variables inline (not recommended for secrets)
vercel --prod -e OPENAI_API_KEY=sk-...
```

### Continuous Deployment

1. Connect your GitHub repository to Vercel
2. Vercel will auto-deploy on push to `main` branch
3. Preview deployments created for pull requests
4. Environment variables inherited based on branch

### Verify Deployment

After deployment:

```bash
# Check deployment URL
curl https://your-domain.vercel.app/api/health

# Test authentication endpoints
curl https://your-domain.vercel.app/auth/microsoft/authorize
curl https://your-domain.vercel.app/auth/google/authorize
```

## Troubleshooting

### "Environment Variable references Secret that does not exist"

**Problem**: Vercel can't find a referenced secret

**Solution**: Create the secret first
```bash
vercel secrets add xai_api_key "your-key"
```

### "redirect_uri_mismatch" errors

**Problem**: Redirect URI not configured in provider console

**Solution**: 
1. Copy the exact redirect URI from the error message
2. Add it to the provider console (Azure/Google/Apple)
3. Ensure exact match (http/https, trailing slash, etc.)

### "Invalid credentials" errors

**Problem**: Environment variables not set or incorrect

**Solution**:
```bash
# List all environment variables
vercel env ls

# Check specific variable
vercel env pull .env.check
cat .env.check | grep AZURE_CLIENT_ID
```

### "Service account not found" errors

**Problem**: `GOOGLE_SERVICE_ACCOUNT_JSON` not set correctly

**Solution**:
1. Get the JSON from Google Cloud Console
2. Minify it (remove newlines): `cat service-account.json | jq -c`
3. Copy the single-line JSON
4. Set as environment variable in Vercel dashboard (paste the entire JSON)

### "CORS errors" in browser

**Problem**: CORS origins not configured

**Solution**:
```bash
vercel env add CORS_ALLOWED_ORIGINS production
# Value: https://your-domain.vercel.app
```

## Security Checklist

Before going live:

- [ ] All credentials are production-grade (not development)
- [ ] JWT_SECRET_KEY is strong and unique (at least 32 characters)
- [ ] FORCE_HTTPS=true is set
- [ ] CORS_ALLOWED_ORIGINS is restrictive (no `*`)
- [ ] Rate limiting is enabled
- [ ] Service account has minimal required permissions
- [ ] All secrets are stored in Vercel Secrets or Environment Variables (not in code)
- [ ] Redirect URIs are configured for production domain
- [ ] .env files with credentials are in .gitignore
- [ ] Production credentials are separate from development

## Monitoring

After deployment, monitor:

1. **Vercel Dashboard** → Your project → **Logs**
   - Check for authentication errors
   - Monitor API requests
   - Review error rates

2. **Azure Portal** → Your app → **Authentication logs**
   - Monitor sign-in attempts
   - Check for failed authentications

3. **Google Cloud Console** → **Logging** → **Logs Explorer**
   - Monitor OAuth requests
   - Check Cloud Storage access

4. **Vercel Analytics** (if enabled)
   - Track user sessions
   - Monitor authentication success rates

## Related Documentation

- [CREDENTIAL_CONFIGURATION_GUIDE.md](CREDENTIAL_CONFIGURATION_GUIDE.md) - Local setup
- [AUTH_REFERENCE.md](AUTH_REFERENCE.md) - Quick reference
- [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) - Technical details
- [GOOGLE_CLOUD_SETUP.md](GOOGLE_CLOUD_SETUP.md) - GCP integration
- [DEPLOYMENT_VERIFICATION.md](DEPLOYMENT_VERIFICATION.md) - Testing checklist

## Support

For deployment issues:
- Vercel docs: https://vercel.com/docs
- Vercel support: https://vercel.com/support

For authentication issues:
- Run `python scripts/verify_auth_config.py` locally first
- Check provider documentation:
  - Microsoft: https://docs.microsoft.com/azure/active-directory/develop/
  - Google: https://developers.google.com/identity
  - Apple: https://developer.apple.com/sign-in-with-apple/
