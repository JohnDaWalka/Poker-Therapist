# Authentication Quick Reference

Quick commands and references for authentication setup and troubleshooting.

## 🚀 Quick Start (5 minutes)

```bash
# 1. Copy environment template
cp .env.example .env.local

# 2. Edit with your credentials (see guides below)
nano .env.local  # or use your editor

# 3. Verify configuration
python scripts/verify_auth_config.py

# 4. Start backend
cd backend && uvicorn api.main:app --reload
```

## 📚 Documentation Quick Links

| Guide | Purpose | When to Use |
|-------|---------|-------------|
| [CREDENTIAL_CONFIGURATION_GUIDE.md](CREDENTIAL_CONFIGURATION_GUIDE.md) | **START HERE** - Step-by-step credential setup | First time setup |
| [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) | Detailed technical reference | Deep dive into auth |
| [GOOGLE_CLOUD_SETUP.md](GOOGLE_CLOUD_SETUP.md) | GCP-specific setup | Google Cloud integration |
| [AUTH_QUICKSTART.md](AUTH_QUICKSTART.md) | 5-minute quick start | Fast testing |
| [DEPLOYMENT_VERIFICATION.md](DEPLOYMENT_VERIFICATION.md) | End-to-end testing | Before deployment |

## 🔑 Required Credentials Checklist

### Microsoft (Institutional SSO / Windows Account)
```bash
AZURE_TENANT_ID=________________________________________
AZURE_CLIENT_ID=________________________________________
AZURE_CLIENT_SECRET=____________________________________
AZURE_AUTHORITY=https://login.microsoftonline.com/{tenant-id}
INSTITUTIONAL_EMAIL_DOMAIN=ctstate.edu  # or your domain
```

**Get from**: [Azure Portal](https://portal.azure.com) → Azure AD → App registrations

### Google (OAuth 2.0 / GCP APIs)
```bash
GOOGLE_CLOUD_PROJECT_ID=________________________________
GOOGLE_CLIENT_ID=_______________________________________.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=___________________________________
GOOGLE_STORAGE_BUCKET_NAME=_____________________________
GOOGLE_APPLICATION_CREDENTIALS=./config/google-service-account.json
```

**Get from**: [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Credentials

### Apple Sign-In (Optional - iOS/macOS/watchOS)
```bash
APPLE_TEAM_ID=__________
APPLE_SERVICES_ID=com.therapyrex.signin
APPLE_KEY_ID=__________
APPLE_PRIVATE_KEY_PATH=./config/apple-auth-key.p8
```

**Get from**: [Apple Developer Portal](https://developer.apple.com/account) → Certificates, IDs & Profiles

### JWT & Security
```bash
# Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=_________________________________________
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

## 🧪 Testing Commands

### Verify Configuration
```bash
# Check all authentication settings
python scripts/verify_auth_config.py
```

### Test Microsoft Auth
```bash
# Start backend
cd backend && uvicorn api.main:app --reload

# Open authorization URL (or use curl)
curl http://localhost:8000/auth/microsoft/authorize
```

### Test Google Auth
```bash
# Get Google authorization URL
curl http://localhost:8000/auth/google/authorize
```

### Test Cloud Storage
```bash
# Quick Python test
python -c "
from backend.cloud.google_storage import GoogleCloudStorage
storage = GoogleCloudStorage()
print(f'✓ Bucket exists: {storage.bucket_exists()}')
print(f'✓ Project: {storage.project_id}')
print(f'✓ Bucket: {storage.bucket_name}')
"
```

## 🔧 Common Issues & Fixes

### "No .env.local file found"
```bash
# Solution: Create from template
cp .env.example .env.local
```

### "AZURE_CLIENT_ID must be set"
```bash
# Solution: Check variable is set in .env.local
grep AZURE_CLIENT_ID .env.local

# Make sure it doesn't contain "your-" or "-here"
```

### "redirect_uri_mismatch" (Google)
```bash
# Solution: Exact match required in Google Console
# 1. Go to: https://console.cloud.google.com/apis/credentials
# 2. Edit OAuth 2.0 Client ID
# 3. Add: http://localhost:8501/google/callback (exact match)
```

### "Service account credentials not found"
```bash
# Solution: Verify file exists and path is correct
ls -la config/google-service-account.json

# Check environment variable
grep GOOGLE_APPLICATION_CREDENTIALS .env.local
```

### "Invalid signature" (Apple)
```bash
# Solution: Verify .p8 file and Key ID
# 1. Check file: ls -la config/apple-auth-key.p8
# 2. Verify APPLE_KEY_ID matches Apple Developer Portal
```

## 🔒 Security Checklist

Before deployment:

```bash
# 1. Verify no credentials in git
git grep -E "sk-|AIza|xai-" .env.local config/  # Should return nothing

# 2. Check .gitignore
grep -E "\.env\.local|service-account.*\.json|\.p8" .gitignore

# 3. Verify JWT secret strength
python -c "
import os
from dotenv import load_dotenv
load_dotenv('.env.local')
secret = os.getenv('JWT_SECRET_KEY', '')
print(f'JWT Secret length: {len(secret)} chars')
print('✓ Strong' if len(secret) >= 32 else '✗ Too weak')
"
```

## 📊 Verification Script Output

Expected output when everything is configured:

```
✓ Loaded environment from .env.local

Microsoft Azure AD / Windows Authentication
===========================================
✓ All Microsoft credentials configured
✓ Microsoft authentication provider initialized
✓ Microsoft authorization URL generation works

Google OAuth 2.0 / GCP Authentication
=====================================
✓ All Google credentials configured
✓ Google authentication provider initialized
✓ Google authorization URL generation works

Google Cloud Storage
====================
✓ All Google Cloud Storage variables configured
✓ Service account JSON file found
✓ Google Cloud Storage client initialized
✓ Cloud Storage bucket is accessible

Verification Summary
====================
✓ JWT Configuration: PASSED
✓ Microsoft Authentication: PASSED
✓ Google Authentication: PASSED
✓ Google Cloud Storage: PASSED
✓ Security Settings: PASSED

Results: 5/5 checks passed

✓ All authentication providers configured correctly! 🎉
```

## 🚢 Deployment

### Environment-Specific Credentials

**Development** (`.env.local`)
```bash
AZURE_REDIRECT_URI_WEB=http://localhost:8501/auth/callback
GOOGLE_REDIRECT_URI_WEB=http://localhost:8501/google/callback
FORCE_HTTPS=false
```

**Production** (Hosting platform environment variables)
```bash
AZURE_REDIRECT_URI_WEB=https://your-domain.com/auth/callback
GOOGLE_REDIRECT_URI_WEB=https://your-domain.com/google/callback
FORCE_HTTPS=true
CORS_ALLOWED_ORIGINS=https://your-domain.com
```

### Platform Commands

**Vercel**
```bash
# Set via dashboard or CLI
vercel env add AZURE_CLIENT_ID
vercel env add AZURE_CLIENT_SECRET
vercel env add GOOGLE_CLIENT_ID
# ... etc
```

**Azure App Service**
```bash
az webapp config appsettings set \
  --name <app-name> \
  --resource-group <group> \
  --settings \
  AZURE_CLIENT_ID=<value> \
  GOOGLE_CLIENT_ID=<value>
```

**Google Cloud Run**
```bash
gcloud run deploy poker-therapist \
  --set-env-vars AZURE_CLIENT_ID=<value>,GOOGLE_CLIENT_ID=<value>
```

## 📞 Get Help

1. Run verification: `python scripts/verify_auth_config.py`
2. Check documentation: `CREDENTIAL_CONFIGURATION_GUIDE.md`
3. Review logs: Backend server shows detailed error messages
4. Provider docs:
   - [Microsoft MSAL](https://docs.microsoft.com/azure/active-directory/develop/)
   - [Google Identity](https://developers.google.com/identity)
   - [Apple Sign-In](https://developer.apple.com/sign-in-with-apple/)

## 🎯 One-Command Setup (After credentials added to .env.local)

```bash
# Verify, install deps, and start server
python scripts/verify_auth_config.py && \
pip install -r backend/requirements.txt && \
cd backend && uvicorn api.main:app --reload
```

---

**Remember**: Never commit credentials to git. Use `.env.local` for local development and environment variables for deployment.
