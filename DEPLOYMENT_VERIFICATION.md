# Deployment Verification Checklist

Use this checklist to verify that authentication and cloud services are properly configured and working end-to-end.

## Pre-Deployment Checklist

### Environment Configuration

- [ ] `.env.local` file created from `.env.example`
- [ ] All authentication credentials configured:
  - [ ] `JWT_SECRET_KEY` (generate new random secret)
  - [ ] Microsoft Azure AD credentials (client ID, secret, tenant ID)
  - [ ] Google OAuth credentials (client ID, secret, project ID)
  - [ ] Apple Sign-In credentials (team ID, key ID, services ID)
- [ ] Google Cloud Storage configured:
  - [ ] `GOOGLE_CLOUD_PROJECT_ID`
  - [ ] `GOOGLE_STORAGE_BUCKET_NAME`
  - [ ] `GOOGLE_APPLICATION_CREDENTIALS` path set
  - [ ] Service account JSON file in place
- [ ] `.env.local` and credential files added to `.gitignore`
- [ ] Separate credentials for dev/staging/production environments

### Azure AD Configuration

- [ ] App registered in Azure Portal
- [ ] All platform redirect URIs configured:
  - [ ] iOS: `msauth.com.therapyrex.app://auth`
  - [ ] Windows: `http://localhost:3000/auth/callback`
  - [ ] Web: `http://localhost:8501/auth/callback`
  - [ ] Production URLs added
- [ ] Client secret created and saved
- [ ] API permissions configured:
  - [ ] User.Read
  - [ ] email
  - [ ] profile
  - [ ] openid
  - [ ] offline_access
- [ ] Admin consent granted
- [ ] Institutional domain configured (if applicable)

### Google Cloud Platform Configuration

- [ ] GCP project created
- [ ] Billing enabled
- [ ] Required APIs enabled:
  - [ ] Cloud Storage API
  - [ ] Cloud Identity API
  - [ ] IAM API
- [ ] OAuth 2.0 credentials created for each platform:
  - [ ] iOS client ID
  - [ ] Web client ID
- [ ] OAuth consent screen configured
- [ ] Authorized redirect URIs added
- [ ] Cloud Storage bucket created
- [ ] Service account created with Storage Object Admin role
- [ ] Service account key downloaded

### Apple Developer Configuration

- [ ] App IDs registered:
  - [ ] iOS: `com.therapyrex.app`
  - [ ] watchOS: `com.therapyrex.app.watchkitapp`
- [ ] Services ID created: `com.therapyrex.signin`
- [ ] Sign in with Apple enabled for all App IDs
- [ ] Private key (.p8) created and downloaded
- [ ] Return URLs configured for web platform

### iOS Setup

- [ ] Podfile created with authentication SDKs:
  - [ ] MSAL pod
  - [ ] GoogleSignIn pod
- [ ] `pod install` executed successfully
- [ ] Info.plist configured with:
  - [ ] Azure client ID
  - [ ] Google client ID
  - [ ] URL schemes for OAuth callbacks
- [ ] Sign in with Apple capability added in Xcode
- [ ] App builds without errors

### Windows Setup

- [ ] package.json updated with auth libraries:
  - [ ] @azure/msal-browser
  - [ ] google-auth-library
- [ ] `npm install` or `pnpm install` completed
- [ ] Authentication service created
- [ ] API client updated with auth headers
- [ ] App builds without errors

### Backend Setup

- [ ] Python dependencies installed:
  - [ ] `pip install -r backend/requirements.txt`
- [ ] Authentication modules created in `backend/auth/`
- [ ] Google Cloud Storage module created in `backend/cloud/`
- [ ] Service account JSON file in correct location
- [ ] Backend starts without errors

## Deployment Testing

### Backend API Tests

Start the backend server:
```bash
cd backend
uvicorn api.main:app --reload
```

- [ ] Backend starts successfully
- [ ] No authentication errors in logs
- [ ] Health check endpoint responds: `curl http://localhost:8000/health`

### Microsoft Authentication Test

- [ ] Generate Microsoft authorization URL
- [ ] Open URL in browser
- [ ] Sign in with Microsoft account (or institutional account)
- [ ] Verify redirect back to app with authorization code
- [ ] Exchange code for access token successfully
- [ ] Retrieve user profile info
- [ ] JWT token generated successfully
- [ ] Token validates correctly
- [ ] Refresh token works

### Google Authentication Test

- [ ] Generate Google authorization URL
- [ ] Open URL in browser
- [ ] Sign in with Google account
- [ ] Grant necessary permissions
- [ ] Verify redirect with authorization code
- [ ] Exchange code for access token
- [ ] Retrieve user info from Google
- [ ] JWT token generated successfully
- [ ] Token validates correctly

### Apple Sign-In Test (iOS/macOS only)

- [ ] Sign in with Apple button appears
- [ ] Click triggers Apple authentication flow
- [ ] Face ID/Touch ID authentication works
- [ ] Authorization completes successfully
- [ ] ID token received from Apple
- [ ] Backend validates Apple ID token
- [ ] JWT token generated
- [ ] User info extracted correctly

### Google Cloud Storage Test

Run test script:
```bash
python scripts/test-gcp-connection.py
```

- [ ] Connection to GCS succeeds
- [ ] Bucket is accessible
- [ ] File upload works
- [ ] File download works
- [ ] Signed URL generation works
- [ ] File listing works
- [ ] File deletion works
- [ ] Lifecycle policies are active

### iOS App Tests

Build and run iOS app:
```bash
cd ios
open TherapyRex.xcworkspace
# Build and run in Xcode
```

- [ ] App builds successfully
- [ ] Authentication UI appears
- [ ] Microsoft sign-in works
  - [ ] Opens MSAL authentication view
  - [ ] Authenticates successfully
  - [ ] Returns to app with token
- [ ] Google sign-in works
  - [ ] Opens Google sign-in view
  - [ ] Authenticates successfully
  - [ ] Returns with token
- [ ] Apple Sign-In works
  - [ ] Shows Apple authentication prompt
  - [ ] Face ID/Touch ID works
  - [ ] Returns with credentials
- [ ] Token stored securely in Keychain
- [ ] API calls include authentication header
- [ ] Protected endpoints accessible
- [ ] Sign out works correctly

### watchOS App Tests

- [ ] watchOS app builds
- [ ] Authentication synced from iPhone
- [ ] Token accessible on watch
- [ ] API calls authenticated
- [ ] Watch can access user data

### Windows App Tests

Run Windows app:
```bash
cd windows
pnpm run electron:dev
```

- [ ] App starts successfully
- [ ] Authentication UI displays
- [ ] Microsoft sign-in works
  - [ ] Opens browser for authentication
  - [ ] Redirects back to app
  - [ ] Token stored securely
- [ ] Google sign-in works
  - [ ] Opens browser
  - [ ] Completes OAuth flow
  - [ ] Stores token
- [ ] Tokens persist after app restart
- [ ] API calls authenticated
- [ ] Sign out clears tokens

### Token Management Tests

- [ ] Access token expiration works
- [ ] Token refresh triggers before expiration
- [ ] Refresh token works
- [ ] Expired tokens handled gracefully (re-authentication)
- [ ] Sign out revokes tokens
- [ ] Multiple sessions handled correctly

### Security Tests

- [ ] Tokens not visible in logs
- [ ] Tokens not stored in localStorage (web)
- [ ] Tokens encrypted at rest (mobile)
- [ ] HTTPS enforced in production
- [ ] CORS configured correctly
- [ ] Rate limiting works
- [ ] No secrets in source code
- [ ] No secrets in environment visible to clients

### Integration Tests

- [ ] User can sign in on iOS
- [ ] Same user can sign in on Windows
- [ ] Sessions work across platforms
- [ ] User data syncs via cloud storage
- [ ] Voice recordings upload successfully
- [ ] Recordings accessible across devices
- [ ] Transcripts save correctly
- [ ] Profile data persists

## Production Deployment

### Pre-Production

- [ ] Production environment variables set
- [ ] Production redirect URIs added to all providers
- [ ] Production domain configured
- [ ] SSL certificates installed
- [ ] Database migrations completed
- [ ] Backup procedures in place

### Production Deployment

- [ ] Deploy backend to production server
- [ ] Deploy web app to hosting platform
- [ ] Submit iOS app to App Store
- [ ] Package Windows app for distribution
- [ ] Verify all redirect URIs point to production URLs
- [ ] Test authentication in production environment

### Post-Deployment

- [ ] Production sign-in tested for all providers
- [ ] Monitor logs for errors
- [ ] Check cloud storage costs
- [ ] Set up cost alerts
- [ ] Configure monitoring/alerting
- [ ] Document any issues
- [ ] Create support documentation

## Monitoring

### Ongoing Checks

- [ ] Monitor authentication success rates
- [ ] Track token refresh failures
- [ ] Monitor API error rates
- [ ] Check cloud storage usage
- [ ] Review security logs
- [ ] Track costs (GCP, Azure)

### Monthly Tasks

- [ ] Review failed authentication attempts
- [ ] Check for expired credentials
- [ ] Rotate service account keys (if needed)
- [ ] Review and optimize cloud storage costs
- [ ] Update dependencies
- [ ] Review security advisories

## Troubleshooting

If any checks fail, refer to:
- [AUTHENTICATION_SETUP.md](./AUTHENTICATION_SETUP.md) - Complete authentication guide
- [GOOGLE_CLOUD_SETUP.md](./GOOGLE_CLOUD_SETUP.md) - GCP configuration guide
- Backend logs: `backend/logs/`
- iOS logs: Xcode console
- Windows logs: Electron console

## Sign-Off

Date: _______________

Tested by: _______________

Approved by: _______________

Notes:
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________

## Summary

- [ ] All authentication providers working
- [ ] All platforms tested (iOS, Windows, Web)
- [ ] Cloud storage operational
- [ ] Security measures in place
- [ ] Documentation complete
- [ ] Production deployment successful
- [ ] Monitoring configured

**Status**: ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed
