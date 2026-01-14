# Vercel Environment Variables Setup Guide

Quick reference for setting up all required environment variables in Vercel.

## How to Add Environment Variables in Vercel

### Via Vercel Dashboard (Recommended)
1. Go to your project in [Vercel Dashboard](https://vercel.com/dashboard)
2. Click on "Settings" tab
3. Navigate to "Environment Variables" section
4. Click "Add New"
5. Enter variable name, value, and select environments (Production, Preview, Development)
6. Click "Save"
7. Redeploy for changes to take effect

### Via Vercel CLI
```bash
# Add a single variable for all environments
vercel env add VARIABLE_NAME

# Add for specific environment
vercel env add VARIABLE_NAME production
vercel env add VARIABLE_NAME preview
vercel env add VARIABLE_NAME development

# Pull environment variables to local
vercel env pull .env.local
```

## Required Environment Variables

### 1. AI Provider API Keys

```bash
# xAI (Grok) - Required
vercel env add XAI_API_KEY
# Value: xai-your-api-key-here
# Get from: https://x.ai/api

# OpenAI (ChatGPT) - Required
vercel env add OPENAI_API_KEY
# Value: sk-your-openai-api-key-here
# Get from: https://platform.openai.com/api-keys

# Anthropic (Claude) - Optional
vercel env add ANTHROPIC_API_KEY
# Value: sk-ant-your-api-key-here
# Get from: https://console.anthropic.com/

# Google AI (Gemini) - Optional
vercel env add GOOGLE_AI_API_KEY
# Value: your-google-ai-api-key
# Get from: https://makersuite.google.com/app/apikey

# Perplexity AI - Optional
vercel env add PERPLEXITY_API_KEY
# Value: your-perplexity-api-key
# Get from: https://www.perplexity.ai/settings/api
```

### 2. Authentication & Authorization

```bash
# JWT Secret Key - Required
# Generate with: openssl rand -base64 32
vercel env add JWT_SECRET_KEY
# Value: your-secure-random-32-byte-string

# Authorized User Emails - Required
vercel env add AUTHORIZED_EMAILS
# Value: user1@example.com,user2@example.com,mauro.fanelli@ctstate.edu
# Comma-separated list, no spaces
```

### 3. Microsoft Azure AD (Windows/Institutional SSO)

```bash
# Azure Tenant ID - Required for Microsoft auth
vercel env add AZURE_TENANT_ID
# Value: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
# Get from: Azure Portal → Azure AD → Properties → Directory ID

# Azure Client ID - Required for Microsoft auth
vercel env add AZURE_CLIENT_ID
# Value: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
# Get from: Azure Portal → App registrations → Your app → Application ID

# Azure Client Secret - Required for Microsoft auth
vercel env add AZURE_CLIENT_SECRET
# Value: your-client-secret-value-here
# Get from: Azure Portal → App registrations → Certificates & secrets
# IMPORTANT: Copy immediately after creation, shown only once!

# Azure Authority URL - Required for Microsoft auth
vercel env add AZURE_AUTHORITY
# Value for multi-tenant: https://login.microsoftonline.com/common
# Value for single tenant: https://login.microsoftonline.com/{tenant-id}
# Value for institutional SSO: https://login.microsoftonline.com/{tenant-id}

# Institutional Email Domain - Optional
vercel env add INSTITUTIONAL_EMAIL_DOMAIN
# Value: ctstate.edu
# Leave empty to allow all Microsoft accounts
```

### 4. Google Cloud Platform (OAuth & Storage)

```bash
# Google Cloud Project ID - Required for Google services
vercel env add GOOGLE_CLOUD_PROJECT_ID
# Value: your-project-id
# Get from: GCP Console → Project dashboard

# Google OAuth Client ID - Required for Google auth
vercel env add GOOGLE_CLIENT_ID
# Value: your-client-id.apps.googleusercontent.com
# Get from: GCP Console → APIs & Services → Credentials

# Google OAuth Client Secret - Required for Google auth
vercel env add GOOGLE_CLIENT_SECRET
# Value: your-client-secret
# Get from: GCP Console → APIs & Services → Credentials

# Google Cloud Storage Bucket Name - Required
vercel env add GOOGLE_STORAGE_BUCKET_NAME
# Value: poker-therapist-prod
# Must be globally unique
# Get from: GCP Console → Cloud Storage → Buckets

# Google Service Account Credentials - Required
# This one requires special handling - see below
vercel env add GOOGLE_APPLICATION_CREDENTIALS
# Value: base64-encoded service account JSON
```

#### How to Prepare Google Service Account Credentials:

**Step 1: Download service account JSON**
1. Go to GCP Console → IAM & Admin → Service Accounts
2. Select your service account
3. Click "Keys" → "Add Key" → "Create new key" → JSON
4. Save the file (e.g., `service-account.json`)

**Step 2: Convert to base64**
```bash
# On macOS/Linux:
base64 -i service-account.json | tr -d '\n' > service-account-base64.txt

# On Windows (PowerShell):
[Convert]::ToBase64String([System.IO.File]::ReadAllBytes("service-account.json")) | Out-File -FilePath service-account-base64.txt

# On Windows (Git Bash):
base64 -w 0 service-account.json > service-account-base64.txt
```

**Step 3: Copy the base64 string**
```bash
# On macOS/Linux:
cat service-account-base64.txt | pbcopy

# Or manually copy from the file
cat service-account-base64.txt
```

**Step 4: Add to Vercel**
- Paste the entire base64 string as the value for `GOOGLE_APPLICATION_CREDENTIALS`
- No spaces, no line breaks, just the base64 string

### 5. Apple Sign-In (Optional - For iOS/macOS/watchOS)

```bash
# Apple Team ID - Required for Apple Sign-In
vercel env add APPLE_TEAM_ID
# Value: YOUR_TEAM_ID
# Get from: Apple Developer Portal → Membership

# Apple Services ID - Required for Apple Sign-In
vercel env add APPLE_SERVICES_ID
# Value: com.therapyrex.signin
# Get from: Apple Developer Portal → Identifiers → Services IDs

# Apple Key ID - Required for Apple Sign-In
vercel env add APPLE_KEY_ID
# Value: YOUR_KEY_ID
# Get from: Apple Developer Portal → Keys

# Apple Private Key - Required for Apple Sign-In
# Similar to Google service account, needs base64 encoding
vercel env add APPLE_PRIVATE_KEY_PATH
# Value: base64-encoded .p8 file content
```

#### How to Prepare Apple Private Key:

**Step 1: Download .p8 file**
1. Go to Apple Developer Portal → Keys
2. Select your Sign in with Apple key
3. Download .p8 file (can only download once!)

**Step 2: Convert to base64**
```bash
# On macOS/Linux:
base64 -i AuthKey_XXXXXXXXXX.p8 | tr -d '\n' > apple-key-base64.txt

# On Windows:
certutil -encode AuthKey_XXXXXXXXXX.p8 apple-key-base64.txt
```

**Step 3: Add to Vercel**
- Copy the base64 string and add as `APPLE_PRIVATE_KEY_PATH` value

## Verification Script

After adding all variables, you can verify they're set correctly:

```bash
# Using Vercel CLI
vercel env ls

# Expected output should list all your variables
# (values are hidden for security)
```

## Environment-Specific Variables

### Production Only
Set these for production environment only:
- All authentication credentials (use production values)
- Production API keys
- Production domain URLs

### Preview/Development
Set these for preview/development:
- Test API keys (if available)
- Development authentication credentials
- localhost redirect URIs

## Bulk Add Script

Create a file named `add-vercel-env.sh`:

```bash
#!/bin/bash

# AI Provider Keys
vercel env add XAI_API_KEY production
vercel env add OPENAI_API_KEY production
vercel env add ANTHROPIC_API_KEY production
vercel env add GOOGLE_AI_API_KEY production
vercel env add PERPLEXITY_API_KEY production

# Authentication
vercel env add JWT_SECRET_KEY production
vercel env add AUTHORIZED_EMAILS production

# Microsoft Azure
vercel env add AZURE_TENANT_ID production
vercel env add AZURE_CLIENT_ID production
vercel env add AZURE_CLIENT_SECRET production
vercel env add AZURE_AUTHORITY production
vercel env add INSTITUTIONAL_EMAIL_DOMAIN production

# Google Cloud
vercel env add GOOGLE_CLOUD_PROJECT_ID production
vercel env add GOOGLE_CLIENT_ID production
vercel env add GOOGLE_CLIENT_SECRET production
vercel env add GOOGLE_STORAGE_BUCKET_NAME production
vercel env add GOOGLE_APPLICATION_CREDENTIALS production

# Apple (optional)
# vercel env add APPLE_TEAM_ID production
# vercel env add APPLE_SERVICES_ID production
# vercel env add APPLE_KEY_ID production
# vercel env add APPLE_PRIVATE_KEY_PATH production

echo "Environment variables added. Redeploy your application for changes to take effect."
```

Make it executable and run:
```bash
chmod +x add-vercel-env.sh
./add-vercel-env.sh
```

## Common Issues

### Issue: "Environment variable not found"
**Solution:** 
- Verify variable name is correct (case-sensitive)
- Check variable is set for correct environment (Production/Preview/Development)
- Redeploy after adding variables

### Issue: "Invalid service account JSON"
**Solution:**
- Verify base64 encoding is correct
- Ensure no line breaks in the base64 string
- Check original JSON file is valid
- Try encoding again

### Issue: "Authentication fails in production"
**Solution:**
- Verify all auth-related variables are set
- Check redirect URIs match production domain
- Ensure secrets are copied correctly (no extra spaces)
- Check Vercel logs for specific error messages

### Issue: "Base64 encoding fails"
**Solution:**
- Install base64 utility if missing
- Use platform-specific commands (see above)
- Manually copy JSON and use online base64 encoder as last resort

## Security Best Practices

1. **Never commit `.env` files** - Always use `.gitignore`
2. **Use Vercel secrets for sensitive data** - Prefix with `@` in vercel.json
3. **Rotate credentials regularly** - Set reminders every 6-12 months
4. **Use different credentials per environment** - Don't reuse production credentials
5. **Limit access** - Only give team members access they need
6. **Enable 2FA** - On Vercel and all provider accounts
7. **Monitor usage** - Check Vercel logs and provider audit logs
8. **Document everything** - Keep secure notes of what each credential is for

## Quick Reference Commands

```bash
# List all environment variables
vercel env ls

# Pull variables to local .env file
vercel env pull .env.local

# Remove a variable
vercel env rm VARIABLE_NAME production

# Update a variable (remove and re-add)
vercel env rm VARIABLE_NAME production
vercel env add VARIABLE_NAME production

# Redeploy with new environment variables
vercel --prod
```

## Next Steps

After setting up environment variables:
1. See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for full deployment guide
2. See [VERCEL_DEPLOYMENT_CHECKLIST.md](VERCEL_DEPLOYMENT_CHECKLIST.md) for verification
3. See [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) for provider configuration
4. Test all authentication flows
5. Monitor logs for any issues

## Support

If you need help:
- Check [Vercel documentation](https://vercel.com/docs/concepts/projects/environment-variables)
- Review provider documentation for credential generation
- Open an issue on GitHub with specific error messages
- Contact team lead or administrator
