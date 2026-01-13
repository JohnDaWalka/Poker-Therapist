# Authentication & Cloud Services Quick Start

This guide provides quick instructions to get authentication and Google Cloud services working.

## 🚀 Quick Setup (5 minutes)

### 1. Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env.local

# Edit .env.local with your credentials
nano .env.local  # or use your preferred editor
```

Minimum required variables:
```bash
JWT_SECRET_KEY=your-random-secret-key
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_STORAGE_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=./config/google-service-account.json
```

### 2. Google Cloud Platform Setup (Automated)

```bash
# Run the automated setup script
chmod +x scripts/setup-gcp.sh
./scripts/setup-gcp.sh

# Follow the prompts to create:
# - GCP project
# - Cloud Storage bucket
# - Service account with credentials
```

### 3. Install Dependencies

```bash
# Backend
pip install -r backend/requirements.txt

# iOS (optional, if developing iOS app)
cd ios && pod install

# Windows (optional, if developing Windows app)
cd windows && pnpm install
```

### 4. Test the Setup

```bash
# Start the backend
cd backend
uvicorn api.main:app --reload

# Backend should start on http://localhost:8000
```

## 📱 Platform-Specific Setup

### iOS

1. Get credentials from provider consoles (see detailed guides)
2. Update `ios/TherapyRex/Info.plist` with client IDs
3. Install pods: `cd ios && pod install`
4. Open workspace: `open TherapyRex.xcworkspace`
5. Build and run

### Windows

1. Update credentials in `windows/.env`
2. Install dependencies: `cd windows && pnpm install`
3. Run: `pnpm run electron:dev`

## 🔐 Getting Credentials

### Microsoft Azure AD

1. Go to [Azure Portal](https://portal.azure.com)
2. Create app registration
3. Get: Client ID, Client Secret, Tenant ID
4. Configure redirect URIs
5. **See**: [AUTHENTICATION_SETUP.md](./AUTHENTICATION_SETUP.md#microsoft-azure-ad-setup)

### Google Cloud Platform

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create project or use automated script
3. Get: Client ID, Client Secret, Project ID
4. Create service account and download JSON key
5. **See**: [GOOGLE_CLOUD_SETUP.md](./GOOGLE_CLOUD_SETUP.md)

### Apple Developer

1. Go to [Apple Developer Portal](https://developer.apple.com/account)
2. Register App IDs and Services ID
3. Create private key (.p8 file)
4. Get: Team ID, Key ID, Services ID
5. **See**: [AUTHENTICATION_SETUP.md](./AUTHENTICATION_SETUP.md#apple-developer-setup)

## 📚 Complete Documentation

- **[AUTHENTICATION_SETUP.md](./AUTHENTICATION_SETUP.md)** - Complete authentication setup guide
- **[GOOGLE_CLOUD_SETUP.md](./GOOGLE_CLOUD_SETUP.md)** - Google Cloud Platform integration
- **[DEPLOYMENT_VERIFICATION.md](./DEPLOYMENT_VERIFICATION.md)** - Testing checklist
- **[IMPLEMENTATION_SUMMARY_AUTH.md](./IMPLEMENTATION_SUMMARY_AUTH.md)** - Technical overview

## 🔧 Troubleshooting

### Common Issues

**"Permission denied" on GCS**
```bash
# Verify service account has Storage Object Admin role
gcloud projects get-iam-policy YOUR_PROJECT_ID
```

**"Invalid redirect URI"**
```
- Exact match required (including http/https, trailing slashes)
- Add all redirect URIs to provider console
```

**"Token expired"**
```
- Implement token refresh (already done in code)
- Check system clock
```

### Get Help

1. Check [AUTHENTICATION_SETUP.md](./AUTHENTICATION_SETUP.md#troubleshooting)
2. Check provider documentation
3. Review backend logs
4. Open GitHub issue

## ✅ Verify Everything Works

```bash
# Run the deployment verification checklist
# See: DEPLOYMENT_VERIFICATION.md
```

Key tests:
- [ ] Backend starts without errors
- [ ] Microsoft login works
- [ ] Google login works
- [ ] Apple Sign-In works (iOS only)
- [ ] Files upload to Cloud Storage
- [ ] Tokens stored securely
- [ ] API calls authenticated

## 🎯 What's Implemented

### Authentication
✅ Microsoft Azure AD / Windows accounts  
✅ Google OAuth 2.0  
✅ Apple Sign-In (iOS/macOS/watchOS)  
✅ Institutional SSO (e.g., @ctstate.edu)  
✅ JWT token management  

### Platforms
✅ iOS native app  
✅ watchOS (synced from iPhone)  
✅ Windows desktop (Electron)  
✅ Backend API  

### Cloud Services
✅ Google Cloud Storage  
✅ Service account authentication  
✅ File upload/download  
✅ Signed URLs  

## 📦 Project Structure

```
backend/
├── auth/              # Authentication services
│   ├── jwt_handler.py
│   ├── microsoft_auth.py
│   ├── google_auth.py
│   └── apple_auth.py
└── cloud/             # Google Cloud services
    └── google_storage.py

ios/TherapyRex/Services/
├── AuthenticationService.swift
├── KeychainService.swift
├── MicrosoftAuthService.swift
└── GoogleAuthService.swift

windows/src/services/
├── authService.js
└── api.js

scripts/
└── setup-gcp.sh       # Automated GCP setup
```

## 🔒 Security Checklist

Before deploying to production:

- [ ] Change all default secrets
- [ ] Use separate credentials per environment
- [ ] Enable HTTPS (FORCE_HTTPS=true)
- [ ] Configure CORS properly
- [ ] Add rate limiting
- [ ] Never commit .env.local or credential files
- [ ] Rotate keys regularly
- [ ] Set up monitoring

## 🚢 Deploy to Production

1. Set production environment variables
2. Update redirect URIs to production URLs
3. Enable HTTPS
4. Test all authentication flows
5. Monitor logs and metrics
6. Set up cost alerts

See [DEPLOYMENT_VERIFICATION.md](./DEPLOYMENT_VERIFICATION.md) for complete checklist.

## 💰 Estimated Costs

**Google Cloud Platform:**
- Storage: ~$0.020/GB/month
- Operations: ~$0.05/10K operations
- **Expected**: ~$0.50/month for 1000 users

**Azure AD:** Free for basic authentication  
**Apple Developer:** $99/year program membership  

## 🎉 You're Ready!

With everything configured, you now have:
- Secure authentication across all platforms
- Cloud storage for user data
- Production-ready code
- Comprehensive documentation

Happy coding! 🚀
