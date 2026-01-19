# Vercel Deployment Setup for Google Authentication

This guide provides step-by-step instructions to configure Google OAuth 2.0 authentication and deploy the Poker Therapist application to Vercel.

## Overview

The application now includes complete OAuth 2.0 authentication with Google, Microsoft, and Apple providers. For the Vercel deployment with email `maurofanellijr@gmail.com`, we'll focus on Google authentication.

## Prerequisites

1. Google account (maurofanellijr@gmail.com or institutional account)
2. Vercel account connected to the GitHub repository
3. Access to Google Cloud Console

## Part 1: Google Cloud Console Setup

### Step 1: Create or Select a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account (maurofanellijr@gmail.com)
3. Click the project dropdown at the top
4. Click **"New Project"** or select an existing project
5. Enter project details:
   - **Project name**: `poker-therapist` (or your preferred name)
   - **Organization**: Leave as "No organization" or select your institution
6. Click **"Create"**
7. Wait for the project to be created, then select it

### Step 2: Enable Required APIs

1. In your project, go to **"APIs & Services" > "Library"**
2. Search for and enable the following APIs:
   - **Google+ API** (for user profile)
   - **Google OAuth2 API** (for authentication)
   - **Cloud Storage API** (optional, for file storage)
   
3. For each API:
   - Click on the API name
   - Click **"Enable"**
   - Wait for activation

### Step 3: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services" > "Credentials"**
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"OAuth client ID"**

4. If this is your first time:
   - Click **"Configure Consent Screen"**
   - Select **"External"** (for testing with any Google account)
   - OR select **"Internal"** (if using institutional email only)
   - Click **"Create"**

5. Fill in the OAuth consent screen:
   - **App name**: `Poker Therapist`
   - **User support email**: `maurofanellijr@gmail.com`
   - **App logo**: (optional) Upload your app icon
   - **Application home page**: Your Vercel URL (e.g., `https://poker-therapist.vercel.app`)
   - **Authorized domains**: 
     - `vercel.app`
     - `ctstate.edu` (if using institutional SSO)
   - **Developer contact email**: `maurofanellijr@gmail.com`
   - Click **"Save and Continue"**

6. **Scopes** (Step 2):
   - Click **"Add or Remove Scopes"**
   - Add these scopes:
     - `openid`
     - `email`
     - `profile`
     - `.../auth/userinfo.email`
     - `.../auth/userinfo.profile`
   - Click **"Update"** then **"Save and Continue"**

7. **Test users** (Step 3, only for External apps):
   - Click **"+ Add Users"**
   - Add these email addresses:
     - `maurofanellijr@gmail.com`
     - `m.fanelli1@icloud.com`
     - `johndawalka@icloud.com`
     - `mauro.fanelli@ctstate.edu`
     - Any other authorized users
   - Click **"Save and Continue"**

8. Review and click **"Back to Dashboard"**

### Step 4: Create OAuth Client ID

1. Go back to **"Credentials"**
2. Click **"+ CREATE CREDENTIALS" > "OAuth client ID"**
3. Application type: **"Web application"**
4. Name: `Poker Therapist Web Client`

5. **Authorized JavaScript origins**:
   - Add your Vercel deployment URL(s):
     ```
     https://poker-therapist.vercel.app
     https://poker-therapist-git-main-yourusername.vercel.app
     https://poker-therapist-<hash>.vercel.app
     ```
   - For local testing:
     ```
     http://localhost:8501
     http://localhost:3000
     ```

6. **Authorized redirect URIs**:
   - Add OAuth callback URLs:
     ```
     https://poker-therapist.vercel.app/api/auth/callback/google
     https://poker-therapist-git-main-yourusername.vercel.app/api/auth/callback/google
     http://localhost:8501/auth/callback/google
     ```
   - **IMPORTANT**: Replace `poker-therapist` with your actual Vercel project name
   - Add all preview deployment URLs if needed

7. Click **"Create"**

8. **Save your credentials**:
   - A dialog will appear with your credentials
   - **Client ID**: Starts with something like `123456789-abcdef.apps.googleusercontent.com`
   - **Client Secret**: A random string like `GOCSPX-xxxxxxxxxxxxx`
   - **CRITICAL**: Copy both values immediately - you'll need them for Vercel
   - Click **"OK"**

### Step 5: Get Your Project ID

1. Go to [Google Cloud Console Dashboard](https://console.cloud.google.com/home/dashboard)
2. Your **Project ID** is shown at the top (different from project name)
3. Copy this Project ID for later use

## Part 2: Vercel Environment Variables Setup

### Step 6: Configure Vercel Environment Variables

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your **Poker Therapist** project
3. Go to **"Settings" > "Environment Variables"**

4. Add the following environment variables one by one:

#### Required Google OAuth Variables

| Variable Name | Value | Example |
|--------------|-------|---------|
| `GOOGLE_CLIENT_ID` | Your OAuth Client ID from Step 4 | `123456789-abc...apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Your OAuth Client Secret from Step 4 | `GOCSPX-xxxxxxxxxxxxxxxx` |
| `GOOGLE_CLOUD_PROJECT_ID` | Your Project ID from Step 5 | `poker-therapist-12345` |

#### Required JWT and Auth Configuration

| Variable Name | Value | Notes |
|--------------|-------|-------|
| `JWT_SECRET_KEY` | Generate a secure random string | Use: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `ENABLE_GOOGLE_AUTH` | `true` | Enable Google authentication |
| `ENABLE_MICROSOFT_AUTH` | `false` | Disable Microsoft (optional) |
| `ENABLE_APPLE_AUTH` | `false` | Disable Apple (optional) |
| `DEFAULT_AUTH_PROVIDER` | `google` | Use Google as default |
| `REQUIRE_AUTHENTICATION` | `false` | Don't force auth (recommended for testing) |

#### Existing Variables (verify these are set)

| Variable Name | Value | Notes |
|--------------|-------|-------|
| `AUTHORIZED_EMAILS` | `maurofanellijr@gmail.com,m.fanelli1@icloud.com,...` | Comma-separated authorized users |
| `XAI_API_KEY` | Your xAI API key | For chatbot functionality |
| `OPENAI_API_KEY` | Your OpenAI API key | For chatbot functionality |
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Optional |
| `GOOGLE_API_KEY` | Your Google AI API key | For Gemini (different from OAuth) |

### Step 7: Generate JWT Secret Key

On your local machine, run:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and use it as your `JWT_SECRET_KEY` in Vercel.

### Step 8: Set Environment Variable Scope

For each variable you add in Vercel:
- **Production**: ✓ (check)
- **Preview**: ✓ (check) 
- **Development**: ✓ (check)

This ensures variables are available in all environments.

## Part 3: Deployment and Testing

### Step 9: Deploy to Vercel

1. After setting all environment variables, trigger a new deployment:
   - Option A: Push a commit to your repository
   - Option B: In Vercel dashboard, go to **"Deployments"** and click **"Redeploy"**

2. Monitor the deployment:
   - Watch the build logs for any errors
   - Common issues to check:
     - Missing environment variables
     - Python dependencies installation
     - Import errors

3. Once deployed, note your deployment URL (e.g., `https://poker-therapist.vercel.app`)

### Step 10: Update Google Cloud Redirect URIs

**IMPORTANT**: After your first Vercel deployment, you may need to update redirect URIs:

1. Go back to [Google Cloud Credentials](https://console.cloud.google.com/apis/credentials)
2. Click on your OAuth 2.0 Client ID
3. Add any new Vercel preview URLs that were created
4. Click **"Save"**

### Step 11: Test Authentication Flow

1. Visit your Vercel deployment URL
2. Navigate to the API docs: `https://your-app.vercel.app/docs`
3. Test the authentication endpoints:
   - **GET** `/api/auth/providers` - Should show Google is enabled
   - **POST** `/api/auth/authorize` - Should return Google OAuth URL

4. Test the full OAuth flow:
   ```bash
   # Get authorization URL
   curl -X POST "https://your-app.vercel.app/api/auth/authorize" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "google",
       "redirect_uri": "https://your-app.vercel.app/api/auth/callback/google",
       "state": "random-state-string"
     }'
   ```

5. Open the returned `authorization_url` in a browser
6. Sign in with your Google account (maurofanellijr@gmail.com)
7. Grant permissions
8. You should be redirected to the callback URL with an access token

## Part 4: Troubleshooting

### Common Issues and Solutions

#### Issue 1: "redirect_uri_mismatch" Error

**Cause**: The redirect URI used doesn't match any in Google Cloud Console

**Solution**:
1. Check the exact redirect URI in the error message
2. Add it to Google Cloud Console OAuth client
3. Make sure there are no trailing slashes or typos

#### Issue 2: "Access blocked: This app's request is invalid"

**Cause**: OAuth consent screen not properly configured

**Solution**:
1. Complete all steps of the OAuth consent screen
2. Ensure app is in "Testing" mode if using External user type
3. Add your email to Test Users list

#### Issue 3: Environment Variables Not Loading

**Cause**: Vercel didn't pick up the new variables

**Solution**:
1. Verify variables are set in Vercel dashboard
2. Redeploy the application
3. Check deployment logs for environment variable values (they should show as `***`)

#### Issue 4: "Authentication service not configured"

**Cause**: Missing required environment variables

**Solution**:
1. Verify all three Google OAuth variables are set:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_CLOUD_PROJECT_ID`
2. Check Vercel deployment logs for specific error messages
3. Ensure variables don't have extra spaces or quotes

#### Issue 5: CORS Errors

**Cause**: Frontend trying to access API from unauthorized origin

**Solution**:
1. Check `backend/api/main.py` CORS configuration
2. Ensure your Vercel URL is in `allow_origins`
3. Verify requests include proper CORS headers

## Part 5: Vercel-Specific Configuration

### Understanding vercel.json

The `vercel.json` file has been updated with Google auth variables:

```json
{
  "env": {
    "GOOGLE_CLIENT_ID": "@google_client_id",
    "GOOGLE_CLIENT_SECRET": "@google_client_secret",
    "GOOGLE_CLOUD_PROJECT_ID": "@google_cloud_project_id",
    "JWT_SECRET_KEY": "@jwt_secret_key",
    "ENABLE_GOOGLE_AUTH": "true",
    ...
  }
}
```

The `@` prefix indicates these are Vercel secret references that must be set in the dashboard.

### Vercel Secrets vs Environment Variables

- **Environment Variables**: Set in Vercel dashboard UI
- **Secrets**: Referenced in `vercel.json` with `@` prefix
- Both work the same way - the `@` syntax just references them securely

## Part 6: Security Best Practices

### DO ✅

1. **Rotate secrets regularly**: Change OAuth client secret every 90 days
2. **Use different credentials per environment**: Separate dev/staging/production
3. **Monitor OAuth consent screen**: Check for suspicious activity
4. **Enable MFA**: On your Google account used for OAuth
5. **Restrict authorized users**: Only add emails that need access
6. **Use HTTPS only**: Never use HTTP in production
7. **Review access logs**: Check Google Cloud audit logs regularly

### DON'T ❌

1. **Never commit secrets**: Don't put credentials in code or `.env` files in Git
2. **Don't share client secrets**: Keep OAuth client secret private
3. **Don't use same credentials everywhere**: Separate dev from production
4. **Don't skip the consent screen**: Always configure it properly
5. **Don't disable CSRF protection**: Keep the `state` parameter
6. **Don't use weak JWT secrets**: Generate strong random keys

## Part 7: Monitoring and Maintenance

### Check Deployment Health

1. Visit the health endpoint: `https://your-app.vercel.app/health`
2. Should return: `{"status": "healthy"}`

### View Logs

1. In Vercel dashboard, go to your project
2. Click on **"Logs"** or a specific deployment
3. Monitor for authentication errors or API failures

### Monitor Google Cloud Usage

1. Go to [Google Cloud Console - APIs & Services - Dashboard](https://console.cloud.google.com/apis/dashboard)
2. Monitor OAuth API calls
3. Check for quota limits or unusual activity

## Completion Checklist

Before considering deployment complete, verify:

- [ ] Google Cloud project created and configured
- [ ] OAuth 2.0 Client ID created
- [ ] OAuth consent screen configured
- [ ] All authorized redirect URIs added
- [ ] Test users added (for External apps)
- [ ] All Vercel environment variables set
- [ ] JWT secret key generated and added
- [ ] Application deployed to Vercel successfully
- [ ] `/health` endpoint returns healthy status
- [ ] `/api/auth/providers` shows Google enabled
- [ ] Can generate authorization URL via API
- [ ] OAuth flow completes successfully
- [ ] Can exchange code for tokens
- [ ] Can validate and refresh tokens
- [ ] Authorized emails can authenticate
- [ ] Unauthorized emails are rejected

## Support and Resources

### Documentation Links

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

### API Endpoints

Once deployed, your API will have these authentication endpoints:

- `GET /api/auth/providers` - List enabled providers
- `POST /api/auth/authorize` - Get OAuth URL
- `GET /api/auth/callback/google` - OAuth callback
- `POST /api/auth/token` - Exchange code for tokens
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout and revoke token

### Contact

For issues specific to this deployment:
- GitHub Issues: [Poker-Therapist Repository](https://github.com/JohnDaWalka/Poker-Therapist)
- Email: maurofanellijr@gmail.com

---

**Last Updated**: January 2026  
**Version**: 1.0  
**Author**: Poker Therapist Development Team
