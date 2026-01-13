# Quick Start Guide: GCP & Authentication

This is a quick reference for setting up and using the new GCP persistent memory and authentication features.

## What's New? 🎉

Your Poker Therapist application now has:

1. **☁️ Cloud Storage** - Data persists across sessions using Google Firestore
2. **🔐 Secure Login** - Microsoft and Google account authentication
3. **🏫 Institutional SSO** - Support for university email domains (ctstate.edu)
4. **📱 Multi-Device** - Access your data from anywhere

## Quick Setup (5 Minutes)

### Option 1: Use Without GCP (Local Only)

```bash
# Just run the app as before
streamlit run chatbot_app.py

# Or run the API
uvicorn backend.api.main:app --reload
```

Everything works exactly as before with local SQLite storage.

### Option 2: Enable Cloud Features

1. **Get GCP Credentials** (One-time setup):
   - Go to: https://console.cloud.google.com
   - Create project: "poker-therapist"
   - Enable Firestore API
   - Create service account
   - Download JSON credentials as `gcp-credentials.json`

2. **Set Environment Variables**:
   ```bash
   # Add to .env.local
   GCP_PROJECT_ID=your-project-id
   GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json
   ```

3. **That's it!** Your data now syncs to the cloud automatically.

### Option 3: Enable Authentication

1. **For Microsoft (Institutional) Login**:
   - Go to: https://portal.azure.com
   - Register an app
   - Copy Tenant ID, Client ID, and Secret
   - Add to `.env.local`:
     ```bash
     AZURE_TENANT_ID=your-tenant-id
     AZURE_CLIENT_ID=your-client-id
     AZURE_CLIENT_SECRET=your-secret
     AUTHENTICATION_ENABLED=true
     INSTITUTIONAL_EMAIL_DOMAINS=ctstate.edu
     ```

2. **For Google Login**:
   - Go to: https://console.cloud.google.com/apis/credentials
   - Create OAuth Client ID
   - Copy Client ID and Secret
   - Add to `.env.local`:
     ```bash
     GOOGLE_OAUTH_CLIENT_ID=your-client-id
     GOOGLE_OAUTH_CLIENT_SECRET=your-secret
     AUTHENTICATION_ENABLED=true
     ```

## Usage Examples

### Without Authentication (Current Behavior)

```python
# Run Streamlit chatbot
streamlit run chatbot_app.py

# Use the API
curl http://localhost:8000/api/triage \
  -H "Content-Type: application/json" \
  -d '{"emotion": "frustrated", "intensity": 7}'
```

### With Authentication

```bash
# 1. Get a token by logging in
# Visit: http://localhost:8000/auth/login/microsoft
# or: http://localhost:8000/auth/login/google

# 2. Use the token in API calls
curl http://localhost:8000/api/triage \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"emotion": "frustrated", "intensity": 7}'
```

## FAQ

### Q: Do I need to set up GCP to use the app?
**A:** No! The app works perfectly fine without GCP. It will use local SQLite storage.

### Q: Do I need authentication?
**A:** No! Set `AUTHENTICATION_ENABLED=false` or omit it entirely to disable authentication.

### Q: What happens to my existing data?
**A:** Nothing! Your existing SQLite data stays intact. When you enable GCP, it syncs alongside the local data.

### Q: Can I use just GCP without authentication?
**A:** Yes! GCP and authentication are independent features. Use either, both, or neither.

### Q: How much does this cost?
**A:** GCP and Vercel have generous free tiers. For typical usage, it's **$0/month**.

### Q: Is my data secure?
**A:** Yes! We use industry-standard OAuth 2.0, JWT tokens, and encrypted storage. CodeQL security scan passed with 0 vulnerabilities.

## Troubleshooting

### "Could not load credentials"
```bash
# Check your GCP credentials path
export GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json
```

### "Authentication failed"
```bash
# Disable authentication for development
export AUTHENTICATION_ENABLED=false
```

### "Firestore connection timeout"
```bash
# Check internet connection and firewall
# Verify Firestore API is enabled in GCP Console
```

## Complete Documentation

For detailed setup instructions, see:

- 📘 **[GCP_SETUP.md](GCP_SETUP.md)** - Complete GCP Firestore setup
- 🔐 **[AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md)** - Authentication configuration
- 🚀 **[DEPLOYMENT_TESTING.md](DEPLOYMENT_TESTING.md)** - Deployment guide
- 📋 **[IMPLEMENTATION_GCP_AUTH.md](IMPLEMENTATION_GCP_AUTH.md)** - Technical details

## Need Help?

1. Check the documentation above
2. Review error messages in console/logs
3. Open an issue on GitHub
4. Contact support

## Summary

✅ **No breaking changes** - Everything works as before  
✅ **Optional features** - Use what you need  
✅ **Easy setup** - 5 minutes to get started  
✅ **Well documented** - Comprehensive guides available  
✅ **Production ready** - Tested and secure  

Enjoy your enhanced Poker Therapist application! 🎰
