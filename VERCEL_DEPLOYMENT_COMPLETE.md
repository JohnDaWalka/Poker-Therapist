# Vercel Deployment - Complete Setup Guide

This document provides a comprehensive overview of deploying the Poker Therapist application to Vercel with full authentication support.

## 📋 What This Guide Covers

This deployment setup enables:
- ✅ Serverless FastAPI backend on Vercel
- ✅ Microsoft Azure AD authentication (Windows accounts, institutional SSO like @ctstate.edu)
- ✅ Google OAuth 2.0 authentication and Cloud Platform integration
- ✅ Apple Sign-In authentication (optional, for iOS/macOS/watchOS)
- ✅ JWT-based authorization
- ✅ Google Cloud Storage for data persistence
- ✅ Multi-provider AI integration (OpenAI, Anthropic, Google, xAI, Perplexity)
- ✅ Automatic HTTPS and SSL
- ✅ Auto-scaling serverless functions

## 🚀 Quick Start (15 minutes)

### Prerequisites
- [ ] Vercel account (free tier works)
- [ ] GitHub repository access
- [ ] At least one AI provider API key (OpenAI or xAI)
- [ ] Microsoft Azure AD account (for institutional SSO)
- [ ] Google Cloud Platform account (for OAuth and storage)

### Step 1: Deploy to Vercel (5 minutes)
1. Go to https://vercel.com/new
2. Import repository: `JohnDaWalka/Poker-Therapist`
3. Vercel auto-detects configuration
4. Click "Deploy" (initial deploy to create project)

### Step 2: Configure Minimum Required Variables (5 minutes)
In Vercel Dashboard → Settings → Environment Variables, add:

```bash
# Minimum required for basic functionality
XAI_API_KEY=xai-your-key-here
OPENAI_API_KEY=sk-your-key-here
JWT_SECRET_KEY=<generate with: openssl rand -base64 32>
AUTHORIZED_EMAILS=your-email@example.com,another@example.com
```

Redeploy after adding variables.

### Step 3: Add Authentication (5 minutes)
Follow provider-specific setup:
- **Microsoft Azure AD:** [See Quick Setup](#microsoft-azure-ad-quick-setup)
- **Google Cloud:** [See Quick Setup](#google-cloud-platform-quick-setup)
- **Apple Sign-In:** [See Quick Setup](#apple-sign-in-quick-setup)

### Step 4: Test Deployment
```bash
# Test health endpoint
curl https://your-app.vercel.app/health

# Test API docs
open https://your-app.vercel.app/docs
```

## 📚 Documentation Structure

We've created multiple guides for different needs:

### 1. **Quick Reference Guides**
- **[VERCEL_ENV_SETUP.md](VERCEL_ENV_SETUP.md)** ⭐ START HERE
  - How to set up all environment variables
  - Copy-paste commands for each variable
  - Base64 encoding instructions for service accounts
  - Troubleshooting common issues

### 2. **Comprehensive Deployment Guide**
- **[VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)** 📖 DETAILED GUIDE
  - Complete deployment walkthrough
  - Authentication provider setup instructions
  - Post-deployment verification
  - Monitoring and maintenance
  - Troubleshooting guide

### 3. **Step-by-Step Checklist**
- **[VERCEL_DEPLOYMENT_CHECKLIST.md](VERCEL_DEPLOYMENT_CHECKLIST.md)** ✅ USE FOR DEPLOYMENT
  - Pre-deployment checklist
  - Deployment steps
  - Post-deployment verification
  - Security audit checklist
  - Ongoing maintenance schedule

### 4. **Authentication Setup**
- **[AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md)** 🔐 DEEP DIVE
  - Complete Microsoft Azure AD setup
  - Google Cloud Platform setup
  - Apple Developer setup
  - Security best practices
  - Platform-specific configuration

- **[AUTH_QUICKSTART.md](AUTH_QUICKSTART.md)** ⚡ QUICK START
  - 5-minute authentication setup
  - Essential credentials only
  - Testing procedures

## 🔧 Detailed Setup Instructions

### Microsoft Azure AD Quick Setup

**For institutional SSO (e.g., @ctstate.edu accounts):**

1. **Register App in Azure Portal**
   - Go to https://portal.azure.com
   - Navigate to: Azure Active Directory → App registrations → New registration
   - Name: "Poker Therapist Production"
   - Redirect URI: `https://your-app.vercel.app/auth/callback`
   - Click "Register"

2. **Create Client Secret**
   - Go to: Certificates & secrets → New client secret
   - Description: "Vercel Production"
   - Expiration: 24 months
   - **Copy the value immediately** (shown only once!)

3. **Configure Permissions**
   - Go to: API permissions → Add a permission → Microsoft Graph
   - Add: `User.Read`, `email`, `profile`, `openid`, `offline_access`
   - Click "Grant admin consent"

4. **Add to Vercel**
   ```bash
   vercel env add AZURE_TENANT_ID        # From Overview page
   vercel env add AZURE_CLIENT_ID        # From Overview page
   vercel env add AZURE_CLIENT_SECRET    # From step 2
   vercel env add AZURE_AUTHORITY        # https://login.microsoftonline.com/{tenant-id}
   vercel env add INSTITUTIONAL_EMAIL_DOMAIN  # e.g., ctstate.edu
   ```

**Full details:** [AUTHENTICATION_SETUP.md - Microsoft Azure AD](AUTHENTICATION_SETUP.md#microsoft-azure-ad-setup)

### Google Cloud Platform Quick Setup

**For OAuth 2.0 authentication and Cloud Storage:**

1. **Create GCP Project**
   - Go to https://console.cloud.google.com
   - Create project: "Poker Therapist Production"
   - Enable billing (required for Cloud Storage)

2. **Enable Required APIs**
   - APIs & Services → Library
   - Enable: Cloud Storage API, Cloud Identity API

3. **Create OAuth Credentials**
   - APIs & Services → Credentials → Create Credentials → OAuth client ID
   - Type: Web application
   - Redirect URI: `https://your-app.vercel.app/google/callback`
   - Copy Client ID and Client Secret

4. **Create Service Account**
   - IAM & Admin → Service Accounts → Create Service Account
   - Name: "poker-therapist-vercel"
   - Role: "Storage Object Admin"
   - Create key → JSON → Download
   - **Convert to base64:**
     ```bash
     base64 -i service-account.json | tr -d '\n'
     ```

5. **Create Storage Bucket**
   - Cloud Storage → Create Bucket
   - Name: `poker-therapist-prod-{unique-suffix}`
   - Region: closest to your users
   - Access: Uniform

6. **Add to Vercel**
   ```bash
   vercel env add GOOGLE_CLOUD_PROJECT_ID        # From project dashboard
   vercel env add GOOGLE_CLIENT_ID               # From step 3
   vercel env add GOOGLE_CLIENT_SECRET           # From step 3
   vercel env add GOOGLE_STORAGE_BUCKET_NAME     # From step 5
   vercel env add GOOGLE_APPLICATION_CREDENTIALS # Base64 string from step 4
   ```

**Full details:** [AUTHENTICATION_SETUP.md - Google Cloud Platform](AUTHENTICATION_SETUP.md#google-cloud-platform-setup)

### Apple Sign-In Quick Setup

**Optional - for iOS/macOS/watchOS apps:**

1. **Register App ID**
   - Go to https://developer.apple.com/account
   - Identifiers → App IDs → Create new
   - Bundle ID: `com.therapyrex.app`
   - Enable "Sign in with Apple"

2. **Create Services ID**
   - Identifiers → Services IDs → Create new
   - ID: `com.therapyrex.signin`
   - Configure: Add domain and return URL

3. **Create Private Key**
   - Keys → Create new key
   - Enable "Sign in with Apple"
   - Download .p8 file (cannot re-download!)
   - **Convert to base64:**
     ```bash
     base64 -i AuthKey_XXXXXXXXXX.p8 | tr -d '\n'
     ```

4. **Add to Vercel**
   ```bash
   vercel env add APPLE_TEAM_ID           # From Membership page
   vercel env add APPLE_SERVICES_ID       # From step 2
   vercel env add APPLE_KEY_ID            # From step 3
   vercel env add APPLE_PRIVATE_KEY_PATH  # Base64 from step 3
   ```

**Full details:** [AUTHENTICATION_SETUP.md - Apple Developer](AUTHENTICATION_SETUP.md#apple-developer-setup)

## 🧪 Testing Your Deployment

### 1. Basic Health Check
```bash
# Should return: {"status": "healthy"}
curl https://your-app.vercel.app/health

# Should return API info
curl https://your-app.vercel.app/
```

### 2. Test API Documentation
Visit: `https://your-app.vercel.app/docs`

You should see:
- Interactive Swagger UI
- All API endpoints listed
- Authentication requirements shown

### 3. Test Authentication Flows

**Microsoft Authentication:**
```bash
# Get authorization URL
curl https://your-app.vercel.app/auth/microsoft/authorize

# Test the returned URL in browser
# Should redirect to Microsoft login
# After login, should redirect back with token
```

**Google Authentication:**
```bash
# Get authorization URL
curl https://your-app.vercel.app/auth/google/authorize

# Test in browser - should show Google consent screen
```

### 4. Check Vercel Logs
1. Go to Vercel Dashboard
2. Select your project
3. Click "Logs" tab
4. Look for any errors or warnings

## 🔒 Security Checklist

Before going to production:

- [ ] All secrets stored as Vercel environment variables (not in code)
- [ ] JWT secret is cryptographically secure (32+ bytes)
- [ ] Different credentials for development/staging/production
- [ ] CORS origins restricted (not using `*`)
- [ ] Redirect URIs exactly match in provider consoles
- [ ] Service accounts have minimum required permissions
- [ ] 2FA enabled on Vercel account
- [ ] 2FA enabled on all provider accounts
- [ ] Credentials rotation schedule documented
- [ ] Team access properly configured
- [ ] Monitoring and alerting set up

## 📊 What Gets Deployed

### Files Included in Deployment
- ✅ `api/index.py` - Serverless function handler
- ✅ `backend/` - FastAPI application code
- ✅ `requirements.txt` - Python dependencies
- ✅ `vercel.json` - Vercel configuration
- ✅ All necessary Python modules

### Files Excluded from Deployment
(via `.vercelignore`)
- ❌ Tests (`tests/`, `test_*.py`)
- ❌ Documentation (`.md` files except README)
- ❌ Database files (`*.db`)
- ❌ Development files (`.vscode/`, `.idea/`)
- ❌ Environment files (`.env`, `.env.local`)
- ❌ Platform-specific code (`ios/`, `windows/`, `flutter/`)

## 💰 Cost Estimate

### Vercel
- **Hobby (Free):** 100 GB bandwidth, 100 GB-hours compute/month
- **Pro ($20/month):** Unlimited bandwidth, 1,000 GB-hours compute
- **Typical usage:** Should fit in free tier for development/testing

### Google Cloud Platform
- **Storage:** ~$0.020/GB/month
- **API calls:** ~$0.05/10,000 operations
- **Estimated:** $0.50-$5/month depending on usage
- **Free tier:** $300 credit for new accounts

### Azure AD
- **Basic authentication:** Free
- **Premium features:** $6/user/month (not required)

### Apple Developer
- **Developer Program:** $99/year (only if using Apple Sign-In)

### AI Provider APIs
- **OpenAI:** Pay-as-you-go (varies by model)
- **Anthropic:** Pay-as-you-go
- **xAI:** Check current pricing
- **Estimate:** $10-$100/month depending on usage

## 🎯 Recommended Workflow

### For First-Time Setup:
1. Read this document (VERCEL_DEPLOYMENT_COMPLETE.md)
2. Use **[VERCEL_ENV_SETUP.md](VERCEL_ENV_SETUP.md)** to set up environment variables
3. Follow **[VERCEL_DEPLOYMENT_CHECKLIST.md](VERCEL_DEPLOYMENT_CHECKLIST.md)** step-by-step
4. Refer to **[AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md)** for detailed provider setup

### For Quick Reference:
- Environment variable names: **[VERCEL_ENV_SETUP.md](VERCEL_ENV_SETUP.md)**
- Troubleshooting: **[VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)** (bottom sections)
- Testing procedures: **[DEPLOYMENT_VERIFICATION.md](DEPLOYMENT_VERIFICATION.md)**

### For Maintenance:
- Use **[VERCEL_DEPLOYMENT_CHECKLIST.md](VERCEL_DEPLOYMENT_CHECKLIST.md)** maintenance sections
- Check Vercel logs regularly
- Rotate credentials per schedule

## 🆘 Getting Help

### If Deployment Fails:
1. Check Vercel build logs
2. Verify all environment variables are set
3. See troubleshooting in **[VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)**

### If Authentication Fails:
1. Verify redirect URIs match exactly
2. Check environment variables are correct
3. See **[AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md)** troubleshooting

### If You Need Support:
- GitHub Issues: https://github.com/JohnDaWalka/Poker-Therapist/issues
- Vercel Support: https://vercel.com/support
- Provider Support: Links in respective documentation

## 📝 Next Steps After Deployment

1. **Test Everything**
   - Run through [DEPLOYMENT_VERIFICATION.md](DEPLOYMENT_VERIFICATION.md)
   - Test all authentication flows
   - Verify API endpoints work

2. **Set Up Monitoring**
   - Enable Vercel Analytics
   - Configure error tracking
   - Set up billing alerts

3. **Configure Custom Domain** (Optional)
   - Purchase domain
   - Add to Vercel
   - Update redirect URIs in all providers

4. **Document Your Deployment**
   - Record deployment URL
   - Document credential locations
   - Share access with team

5. **Schedule Maintenance**
   - Set reminder for credential rotation
   - Plan for dependency updates
   - Schedule regular security audits

## ✅ Success Criteria

Your deployment is successful when:
- [ ] Application is accessible at Vercel URL
- [ ] `/health` endpoint returns healthy status
- [ ] `/docs` shows interactive API documentation
- [ ] Can authenticate with Microsoft account
- [ ] Can authenticate with Google account
- [ ] Protected endpoints require valid token
- [ ] Google Cloud Storage works for file operations
- [ ] No errors in Vercel logs
- [ ] All team members can access
- [ ] Monitoring is set up

## 🎉 Congratulations!

If you've followed this guide and completed all steps, you now have:
- ✅ Poker Therapist FastAPI backend deployed to Vercel
- ✅ Multiple authentication providers configured
- ✅ Secure credential management
- ✅ Cloud storage integration
- ✅ Production-ready serverless infrastructure
- ✅ Comprehensive documentation for your team

Your application is now ready for users! 🚀

---

**Maintainers:** Keep this document updated as deployment procedures change.  
**Last Updated:** January 2026  
**Version:** 1.0.0
