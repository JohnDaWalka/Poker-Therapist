# End-to-End Authentication Testing Guide

This guide provides step-by-step instructions for testing authentication configuration end-to-end in a test environment.

## Prerequisites

Before starting end-to-end testing:

- [x] All authentication credentials configured in `.env.local`
- [x] Service account credentials downloaded and placed in `config/` directory
- [x] Backend dependencies installed: `pip install -r backend/requirements.txt`
- [x] Frontend dependencies installed (if testing web/desktop apps)
- [x] Development environment set up

## Step 1: Configuration Verification

### 1.1 Run Automated Verification Script

```bash
# Verify configuration
python scripts/verify_auth_config.py
```

**Expected Output:**
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

[... more checks ...]

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

### 1.2 Troubleshoot Configuration Issues

If verification fails, common issues:

**Missing Environment Variables:**
```bash
# Check which variables are missing
python -c "
from dotenv import load_dotenv
import os
load_dotenv('.env.local')
required = ['AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET', 'AZURE_TENANT_ID', 
            'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'JWT_SECRET_KEY']
for var in required:
    val = os.getenv(var, '')
    print(f'{var}: {\"✓\" if val and not val.startswith(\"your-\") else \"✗ MISSING\"}')"
```

**Invalid Credentials Format:**
- Ensure no extra spaces or quotes in `.env.local`
- Check for proper format (GUIDs, URLs, etc.)

**Service Account File Not Found:**
```bash
# Verify service account file exists and is readable
test -f config/google-service-account.json && echo "✓ File exists" || echo "✗ File missing"
python -c "import json; json.load(open('config/google-service-account.json'))" && echo "✓ Valid JSON" || echo "✗ Invalid JSON"
```

## Step 2: Backend API Testing

### 2.1 Start Backend Server

```bash
cd backend
uvicorn api.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2.2 Test Health Endpoint

```bash
# In a new terminal
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-22T13:40:00.000Z"
}
```

### 2.3 Test Authentication Endpoints

#### Microsoft Authentication Flow

```bash
# 1. Get authorization URL
curl -X GET "http://localhost:8000/auth/microsoft/authorize?redirect_uri=http://localhost:8501/auth/callback"
```

**Expected Response:**
```json
{
  "authorization_url": "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize?client_id=...&redirect_uri=...",
  "state": "random-state-string"
}
```

**Manual Test:**
1. Copy the `authorization_url` from the response
2. Open it in a browser
3. Sign in with your Microsoft/institutional account
4. Verify you're redirected to the callback URL
5. Note the authorization code in the callback URL

#### Google Authentication Flow

```bash
# 1. Get authorization URL
curl -X GET "http://localhost:8000/auth/google/authorize?redirect_uri=http://localhost:8501/google/callback"
```

**Expected Response:**
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...",
  "state": "random-state-string"
}
```

**Manual Test:**
1. Copy the `authorization_url` from the response
2. Open it in a browser
3. Sign in with your Google account
4. Grant permissions for requested scopes
5. Verify you're redirected to the callback URL
6. Note the authorization code in the callback URL

### 2.4 Test Token Exchange

After obtaining authorization codes:

```bash
# Exchange Microsoft authorization code for token
curl -X POST "http://localhost:8000/auth/microsoft/token" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "YOUR_AUTHORIZATION_CODE",
    "redirect_uri": "http://localhost:8501/auth/callback"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "...",
  "id_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "...",
    "email": "your.email@ctstate.edu",
    "name": "Your Name"
  }
}
```

### 2.5 Test Authenticated API Calls

```bash
# Use the access_token from previous step
curl -X GET "http://localhost:8000/api/user/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "id": "...",
  "email": "your.email@ctstate.edu",
  "name": "Your Name",
  "provider": "microsoft",
  "authenticated_at": "2024-01-22T13:40:00.000Z"
}
```

## Step 3: Google Cloud Storage Testing

### 3.1 Test Bucket Access

```bash
# Test bucket connectivity
python -c "
from backend.cloud.google_storage import GoogleCloudStorage
storage = GoogleCloudStorage()
print(f'✓ Connected to project: {storage.project_id}')
print(f'✓ Bucket exists: {storage.bucket_exists()}')
print(f'✓ Bucket name: {storage.bucket_name}')
"
```

### 3.2 Test File Upload/Download

```bash
# Create a test file
echo "Test content for authentication verification" > /tmp/test-upload.txt

# Upload test file
python -c "
from backend.cloud.google_storage import GoogleCloudStorage
storage = GoogleCloudStorage()
success = storage.upload_file('/tmp/test-upload.txt', 'test/auth-verification.txt')
print(f'Upload: {\"✓ Success\" if success else \"✗ Failed\"}')
"

# Download test file
python -c "
from backend.cloud.google_storage import GoogleCloudStorage
storage = GoogleCloudStorage()
success = storage.download_file('test/auth-verification.txt', '/tmp/test-download.txt')
print(f'Download: {\"✓ Success\" if success else \"✗ Failed\"}')
"

# Verify content matches
diff /tmp/test-upload.txt /tmp/test-download.txt && echo "✓ Content matches" || echo "✗ Content differs"

# Clean up
rm /tmp/test-upload.txt /tmp/test-download.txt
```

### 3.3 Test Signed URLs

```bash
python -c "
from backend.cloud.google_storage import GoogleCloudStorage
storage = GoogleCloudStorage()
url = storage.generate_signed_url('test/auth-verification.txt', expiration=3600)
print(f'Signed URL: {url}')
"
```

Test the signed URL in a browser or with curl - it should allow temporary access to the file.

## Step 4: Frontend Application Testing

### 4.1 Streamlit Chatbot (Python)

```bash
# Start Streamlit app
streamlit run chatbot_app.py
```

**Manual Testing:**
1. Open http://localhost:8501 in browser
2. Try signing in with Microsoft account (if authentication required)
3. Verify session is maintained
4. Test chatbot functionality
5. Check voice features (if enabled)

### 4.2 Windows Desktop App (Electron)

```bash
cd windows
pnpm install  # or npm install
pnpm run electron:dev  # or npm run electron:dev
```

**Manual Testing:**
1. App should launch successfully
2. Click "Sign in with Microsoft" button
3. Verify OAuth flow redirects properly
4. Check that user profile is displayed
5. Test API calls to backend

### 4.3 iOS App

```bash
cd ios
pod install
open TherapyRex.xcworkspace
```

**Manual Testing:**
1. Build and run on simulator or device
2. Tap "Sign in with Microsoft"
3. Complete authentication flow
4. Verify user session persists
5. Test "Sign in with Google"
6. Test "Sign in with Apple" (requires physical device)

## Step 5: Security Verification

### 5.1 Token Security

```bash
# Verify JWT tokens are properly signed
python -c "
import jwt
import os
from dotenv import load_dotenv
load_dotenv('.env.local')

# This should succeed with correct secret
token = 'YOUR_JWT_TOKEN'
secret = os.getenv('JWT_SECRET_KEY')
try:
    decoded = jwt.decode(token, secret, algorithms=['HS256'])
    print('✓ Token valid and properly signed')
except jwt.InvalidSignatureError:
    print('✗ Invalid token signature')
except jwt.ExpiredSignatureError:
    print('⚠ Token expired (this is normal)')
"
```

### 5.2 HTTPS Enforcement (Production Only)

In production, verify:
```bash
# Should redirect to HTTPS
curl -I http://your-production-domain.com/api/health
# Expected: 301 Moved Permanently or 308 Permanent Redirect
```

### 5.3 CORS Configuration

```bash
# Test CORS from different origin (should be blocked)
curl -X OPTIONS http://localhost:8000/api/user/profile \
  -H "Origin: http://malicious-site.com" \
  -H "Access-Control-Request-Method: GET" \
  -v
# Should NOT return Access-Control-Allow-Origin header

# Test CORS from allowed origin (should work)
curl -X OPTIONS http://localhost:8000/api/user/profile \
  -H "Origin: http://localhost:8501" \
  -H "Access-Control-Request-Method: GET" \
  -v
# Should return Access-Control-Allow-Origin: http://localhost:8501
```

### 5.4 Rate Limiting

```bash
# Rapidly make requests to test rate limiting
for i in {1..100}; do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/health
done
# Should see some 429 (Too Many Requests) responses
```

## Step 6: CI/CD and Deployment

### 6.1 Environment Variables Setup

For deployment platforms (Vercel, Azure, GCP, etc.):

**Vercel:**
```bash
# Set environment variables via Vercel dashboard or CLI
vercel env add AZURE_CLIENT_ID
vercel env add AZURE_CLIENT_SECRET
vercel env add GOOGLE_CLIENT_ID
# ... etc
```

**Azure App Service:**
```bash
az webapp config appsettings set \
  --name your-app-name \
  --resource-group your-resource-group \
  --settings \
    AZURE_CLIENT_ID="..." \
    AZURE_CLIENT_SECRET="..." \
    GOOGLE_CLIENT_ID="..." \
    JWT_SECRET_KEY="..."
```

**Google Cloud Run:**
```bash
gcloud run deploy poker-therapist \
  --set-env-vars AZURE_CLIENT_ID="..." \
  --set-env-vars AZURE_CLIENT_SECRET="..." \
  --set-env-vars GOOGLE_CLIENT_ID="..." \
  --set-env-vars JWT_SECRET_KEY="..."
```

### 6.2 Update Redirect URIs

For each deployment environment, update redirect URIs in provider consoles:

**Microsoft Azure AD:**
1. Go to Azure Portal → App registrations → Your app
2. Navigate to Authentication → Platform configurations → Web
3. Add production redirect URI: `https://your-domain.com/auth/callback`

**Google Cloud Console:**
1. Go to Cloud Console → APIs & Services → Credentials
2. Select your OAuth 2.0 client ID
3. Add production redirect URI: `https://your-domain.com/google/callback`

### 6.3 Test Production Deployment

```bash
# Test production health endpoint
curl https://your-domain.com/health

# Test production authentication
curl https://your-domain.com/auth/microsoft/authorize
```

## Step 7: Monitoring and Logging

### 7.1 Backend Logs

Monitor backend logs for authentication events:

```bash
# Local development
tail -f backend/logs/app.log | grep -E "auth|token"

# Production (varies by platform)
# Azure: az webapp log tail --name your-app-name
# Google Cloud: gcloud run logs read --service poker-therapist
# Vercel: vercel logs
```

### 7.2 Failed Authentication Attempts

Set up alerts for:
- Multiple failed login attempts
- Invalid token usage
- Expired refresh tokens
- API rate limit violations

### 7.3 Performance Monitoring

Monitor:
- Authentication flow latency
- Token validation time
- Google Cloud Storage upload/download speeds

## Troubleshooting Common Issues

### Authentication Failures

**"invalid_client" Error:**
- Verify client ID and secret are correct
- Check that credentials match the environment (dev/staging/prod)
- Ensure client secret hasn't expired

**"redirect_uri_mismatch" Error:**
- Exact match required (including http/https, port, trailing slash)
- Verify redirect URI is added to provider console
- Check for URL encoding issues

**"Token expired":**
- Implement token refresh logic
- Check system clock synchronization
- Verify token expiration settings

### Cloud Storage Issues

**"Bucket not found":**
- Verify bucket name in `.env.local`
- Check that bucket exists in correct GCP project
- Ensure service account has access

**"Permission denied":**
- Service account needs "Storage Object Admin" role
- Verify IAM permissions in GCP Console
- Check that bucket is in the correct project

**"Invalid credentials":**
- Ensure service account JSON file is valid
- Check file path in `GOOGLE_APPLICATION_CREDENTIALS`
- Verify file permissions (must be readable)

## Success Criteria

Your authentication is properly configured when:

- [ ] ✅ Verification script passes all checks
- [ ] ✅ Backend starts without errors
- [ ] ✅ Microsoft authentication flow completes successfully
- [ ] ✅ Google authentication flow completes successfully
- [ ] ✅ Apple Sign-In works (iOS only)
- [ ] ✅ Tokens are properly generated and validated
- [ ] ✅ Authenticated API calls work
- [ ] ✅ Google Cloud Storage upload/download works
- [ ] ✅ All frontend apps can authenticate
- [ ] ✅ Sessions persist correctly
- [ ] ✅ Token refresh works
- [ ] ✅ Security measures are enforced (HTTPS, CORS, rate limiting)
- [ ] ✅ Deployment to test environment successful
- [ ] ✅ All redirect URIs updated for production
- [ ] ✅ Monitoring and logging operational

## Next Steps

After successful end-to-end testing:

1. **Production Deployment**
   - Generate separate production credentials
   - Update all redirect URIs to production domains
   - Set `FORCE_HTTPS=true` in production
   - Configure production monitoring

2. **Security Hardening**
   - Enable MFA for all admin accounts
   - Set up credential rotation schedule
   - Configure security alerts
   - Perform security audit

3. **Documentation**
   - Document production configuration
   - Create runbooks for common issues
   - Train team on authentication flows

4. **Compliance**
   - Verify compliance with institutional policies
   - Document data handling procedures
   - Set up audit logging

## Additional Resources

- [CREDENTIAL_CONFIGURATION_GUIDE.md](./CREDENTIAL_CONFIGURATION_GUIDE.md) - Step-by-step credential setup
- [AUTHENTICATION_SETUP.md](./AUTHENTICATION_SETUP.md) - Complete authentication documentation
- [GOOGLE_CLOUD_SETUP.md](./GOOGLE_CLOUD_SETUP.md) - GCP integration guide
- [DEPLOYMENT_VERIFICATION.md](./DEPLOYMENT_VERIFICATION.md) - Deployment checklist
- [SECURITY.md](./SECURITY.md) - Security best practices

For support, refer to provider documentation:
- [Microsoft MSAL Documentation](https://docs.microsoft.com/azure/active-directory/develop/)
- [Google Sign-In Documentation](https://developers.google.com/identity)
- [Apple Sign-In Documentation](https://developer.apple.com/sign-in-with-apple/)
