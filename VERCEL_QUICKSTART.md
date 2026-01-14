# 🚀 Quick Deploy to Vercel - 3 Step Guide

Deploy Poker Therapist to Vercel in **15 minutes** with full authentication support.

## ⚡ TL;DR - Super Quick Start

```bash
# 1. Deploy to Vercel
# Visit: https://vercel.com/new
# Import: JohnDaWalka/Poker-Therapist

# 2. Add minimum environment variables in Vercel dashboard:
XAI_API_KEY=xai-your-key
OPENAI_API_KEY=sk-your-key
JWT_SECRET_KEY=$(openssl rand -base64 32)
AUTHORIZED_EMAILS=you@example.com

# 3. Deploy and test
curl https://your-app.vercel.app/health
```

**Done!** 🎉 Your API is live.

For authentication setup, continue below ⬇️

---

## 📖 Complete Setup (15 minutes)

### Step 1: Deploy to Vercel (2 minutes)

1. **Go to:** https://vercel.com/new
2. **Import:** `JohnDaWalka/Poker-Therapist`
3. **Click:** "Deploy" (don't configure anything yet)
4. **Wait:** For initial deployment to complete
5. **Note:** Your deployment URL (e.g., `poker-therapist-abc123.vercel.app`)

### Step 2: Configure Environment Variables (10 minutes)

**In Vercel Dashboard:** Settings → Environment Variables

#### Required for Basic Functionality

```bash
# AI Provider (choose at least one)
XAI_API_KEY=xai-your-key-here                    # Get from: https://x.ai/api
OPENAI_API_KEY=sk-your-key-here                   # Get from: https://platform.openai.com/api-keys

# Security
JWT_SECRET_KEY=<run: openssl rand -base64 32>    # Generate a secure random key
AUTHORIZED_EMAILS=email1@example.com,email2@example.com  # Comma-separated, no spaces
```

#### Optional: Additional AI Providers

```bash
ANTHROPIC_API_KEY=sk-ant-your-key                # Get from: https://console.anthropic.com/
GOOGLE_AI_API_KEY=your-google-key                # Get from: https://makersuite.google.com/app/apikey
PERPLEXITY_API_KEY=your-perplexity-key          # Get from: https://www.perplexity.ai/settings/api
```

#### For Microsoft Authentication (Institutional SSO)

**Setup Azure AD first:** See [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md#microsoft-azure-ad-setup)

```bash
AZURE_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_SECRET=your-client-secret
AZURE_AUTHORITY=https://login.microsoftonline.com/common
INSTITUTIONAL_EMAIL_DOMAIN=ctstate.edu
```

#### For Google OAuth & Cloud Storage

**Setup GCP first:** See [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md#google-cloud-platform-setup)

```bash
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_STORAGE_BUCKET_NAME=poker-therapist-prod
GOOGLE_APPLICATION_CREDENTIALS=<base64-encoded-service-account-json>
```

**How to get base64 service account:**
```bash
base64 -i service-account.json | tr -d '\n'
```

#### For Apple Sign-In (iOS/macOS - Optional)

**Setup Apple Developer first:** See [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md#apple-developer-setup)

```bash
APPLE_TEAM_ID=YOUR_TEAM_ID
APPLE_SERVICES_ID=com.therapyrex.signin
APPLE_KEY_ID=YOUR_KEY_ID
APPLE_PRIVATE_KEY_PATH=<base64-encoded-p8-file>
```

### Step 3: Redeploy & Test (3 minutes)

1. **Redeploy:** Go to Deployments tab → Click "Redeploy"
2. **Wait:** For deployment to complete
3. **Test:**

```bash
# Health check
curl https://your-app.vercel.app/health
# Expected: {"status": "healthy"}

# API info
curl https://your-app.vercel.app/
# Expected: {"message": "Therapy Rex API", ...}

# Interactive docs
open https://your-app.vercel.app/docs
```

4. **Test Authentication** (if configured):

```bash
# Microsoft OAuth
curl https://your-app.vercel.app/auth/microsoft/authorize
# Returns authorization URL - test in browser

# Google OAuth
curl https://your-app.vercel.app/auth/google/authorize
# Returns authorization URL - test in browser
```

---

## 🎯 What's Next?

### Just Want Basic API?
You're done! Your API is live with AI capabilities.

### Need Authentication?
1. Follow provider setup guides in [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md)
2. Add environment variables from Step 2 above
3. Redeploy
4. Test authentication flows

### Want Complete Setup?
Use the comprehensive guides:
- **[VERCEL_DEPLOYMENT_COMPLETE.md](VERCEL_DEPLOYMENT_COMPLETE.md)** - Master guide with all details
- **[VERCEL_DEPLOYMENT_CHECKLIST.md](VERCEL_DEPLOYMENT_CHECKLIST.md)** - Step-by-step checklist
- **[VERCEL_ENV_SETUP.md](VERCEL_ENV_SETUP.md)** - Environment variables reference

---

## 📚 Documentation Index

Choose your path:

### 🏃‍♂️ I Want to Deploy Fast
→ You're reading it! (VERCEL_QUICKSTART.md)

### 📖 I Want Complete Instructions  
→ [VERCEL_DEPLOYMENT_COMPLETE.md](VERCEL_DEPLOYMENT_COMPLETE.md)

### ✅ I Want a Checklist
→ [VERCEL_DEPLOYMENT_CHECKLIST.md](VERCEL_DEPLOYMENT_CHECKLIST.md)

### 🔧 I Need Environment Variable Reference
→ [VERCEL_ENV_SETUP.md](VERCEL_ENV_SETUP.md)

### 🔐 I Need Authentication Setup
→ [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md)

### ⚡ I Need Quick Auth Setup
→ [AUTH_QUICKSTART.md](AUTH_QUICKSTART.md)

### 📝 I Want Detailed Deployment Guide
→ [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)

---

## 🆘 Troubleshooting

### Deployment fails with "Module not found"
**Solution:** All dependencies should be in `requirements.txt` - check logs for missing module

### Environment variables not working
**Solution:** 
1. Verify variable names match exactly (case-sensitive)
2. Redeploy after adding variables
3. Check Vercel logs for errors

### Authentication fails
**Solution:**
1. Verify redirect URIs match exactly in provider console
2. Check environment variables are set correctly
3. See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) troubleshooting section

### Function timeout
**Solution:**
- Vercel free tier: 10-second limit
- Vercel Pro: 60-second limit
- Optimize long-running operations

---

## 💡 Pro Tips

1. **Use Vercel CLI for faster iteration:**
   ```bash
   npm install -g vercel
   vercel login
   vercel
   ```

2. **Test locally before deploying:**
   ```bash
   pip install -r requirements.txt
   uvicorn backend.api.main:app --reload
   ```

3. **Use different credentials per environment:**
   - Development: Test credentials
   - Preview: Staging credentials
   - Production: Production credentials

4. **Monitor your deployment:**
   - Enable Vercel Analytics
   - Check logs regularly
   - Set up billing alerts

5. **Keep credentials secure:**
   - Never commit `.env` files
   - Use Vercel secrets for sensitive data
   - Rotate credentials regularly

---

## 🎉 Success!

If you can access these URLs, you're done:
- ✅ https://your-app.vercel.app/health
- ✅ https://your-app.vercel.app/docs
- ✅ https://your-app.vercel.app/

**Need help?** Open an issue on GitHub with:
- Error message
- Vercel deployment logs
- Steps you followed

**Questions about authentication?** See the comprehensive guides linked above.

---

**Quick Links:**
- 🌐 Vercel Dashboard: https://vercel.com/dashboard
- 📖 Full Docs: [VERCEL_DEPLOYMENT_COMPLETE.md](VERCEL_DEPLOYMENT_COMPLETE.md)
- 🔐 Auth Setup: [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md)
- ✅ Checklist: [VERCEL_DEPLOYMENT_CHECKLIST.md](VERCEL_DEPLOYMENT_CHECKLIST.md)
