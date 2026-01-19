# Quick Setup: Vercel Environment Variables for Google Auth

## Required Environment Variables

Copy and paste these into Vercel Dashboard > Settings > Environment Variables

### 1. Google OAuth Credentials
```
Name: GOOGLE_CLIENT_ID
Value: [Your OAuth Client ID from Google Cloud Console]
Example: 123456789-abcdefghijklmnop.apps.googleusercontent.com

Name: GOOGLE_CLIENT_SECRET  
Value: [Your OAuth Client Secret from Google Cloud Console]
Example: GOCSPX-xxxxxxxxxxxxxxxxxxxxxxxx

Name: GOOGLE_CLOUD_PROJECT_ID
Value: [Your Google Cloud Project ID]
Example: poker-therapist-12345
```

### 2. JWT Configuration
```
Name: JWT_SECRET_KEY
Value: [Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"]
Example: Rp7KPXj8Y9mQ2wN5vB3xF6tL1cD4hS8eW0zU7iO9aG
```

### 3. Authentication Provider Settings
```
Name: ENABLE_GOOGLE_AUTH
Value: true

Name: ENABLE_MICROSOFT_AUTH
Value: false

Name: ENABLE_APPLE_AUTH
Value: false

Name: DEFAULT_AUTH_PROVIDER
Value: google

Name: REQUIRE_AUTHENTICATION
Value: false
```

### 4. Authorized Users (Already Set)
```
Name: AUTHORIZED_EMAILS
Value: maurofanellijr@gmail.com,m.fanelli1@icloud.com,johndawalka@icloud.com,mauro.fanelli@ctstate.edu,cooljack87@icloud.com,jdwalka@pm.me
```

## Google Cloud Console Setup

### Quick Steps:

1. **Create OAuth Credentials**:
   - Go to: https://console.cloud.google.com/apis/credentials
   - Create OAuth 2.0 Client ID
   - Type: Web application

2. **Authorized Redirect URIs** (add all):
   ```
   https://poker-therapist.vercel.app/api/auth/callback/google
   https://[your-vercel-url].vercel.app/api/auth/callback/google
   http://localhost:8501/auth/callback/google
   ```

3. **OAuth Consent Screen**:
   - User type: External
   - Add test users:
     - maurofanellijr@gmail.com
     - mauro.fanelli@ctstate.edu
     - (other authorized emails)

4. **Required Scopes**:
   - openid
   - email  
   - profile

## Generate JWT Secret

Run this command locally:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and use as `JWT_SECRET_KEY`

## Verify Setup

After deployment, test these endpoints:

1. Health check:
   ```
   GET https://your-app.vercel.app/health
   ```

2. Auth providers:
   ```
   GET https://your-app.vercel.app/api/auth/providers
   ```

3. API documentation:
   ```
   https://your-app.vercel.app/docs
   ```

## Common Errors

### "redirect_uri_mismatch"
→ Add your exact Vercel URL to Google Cloud Console authorized redirect URIs

### "Authentication service not configured"  
→ Verify GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_CLOUD_PROJECT_ID are set in Vercel

### "Invalid client"
→ Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are correct and don't have extra spaces

## Next Steps

1. Set all environment variables in Vercel
2. Configure Google Cloud Console OAuth client
3. Redeploy from Vercel dashboard
4. Test authentication endpoints
5. Verify authorized emails can authenticate

---

For detailed setup instructions, see: [VERCEL_GOOGLE_AUTH_SETUP.md](./VERCEL_GOOGLE_AUTH_SETUP.md)
