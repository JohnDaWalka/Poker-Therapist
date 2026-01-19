# Vercel Deployment Guide for Poker Therapist

This guide explains how to deploy the Poker Therapist application to Vercel.

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. Vercel CLI installed (optional, for command-line deployment)
3. Required AI Provider API keys:
   - xAI API key (for Grok)
   - OpenAI API key (for ChatGPT)
   - Anthropic API key (for Claude) - optional
   - Google AI API key (for Gemini) - optional
   - Perplexity API key (for Perplexity AI) - optional
4. Authentication Provider Credentials (see [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md)):
   - Microsoft Azure AD credentials (for Windows/institutional SSO)
   - Google Cloud Platform credentials (for OAuth 2.0 and GCP services)
   - Apple Developer credentials (for iOS/macOS/watchOS) - optional
5. Google Cloud Storage setup (for data persistence):
   - Service account JSON key file
   - Cloud Storage bucket created

## Deployment Options

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Connect Repository**
   - Go to https://vercel.com/new
   - Import the `JohnDaWalka/Poker-Therapist` repository
   - Vercel will automatically detect the `vercel.json` configuration

2. **Configure Environment Variables**
   Add the following environment variables in the Vercel dashboard (Settings → Environment Variables):
   
   **AI Provider Keys:**
   - `XAI_API_KEY`: Your xAI API key for Grok
   - `OPENAI_API_KEY`: Your OpenAI API key for ChatGPT
   - `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude (optional)
   - `GOOGLE_API_KEY`: Your Google API key (optional)
   - `GOOGLE_AI_API_KEY`: Your Google AI API key for Gemini (optional)
   - `PERPLEXITY_API_KEY`: Your Perplexity API key (optional)
   
   **Authentication & Authorization:**
   - `AUTHORIZED_EMAILS`: Comma-separated list of authorized user emails
   - `JWT_SECRET_KEY`: Secure random secret for JWT tokens (generate with: `openssl rand -base64 32`)
   
   **Microsoft Azure AD (Windows/Institutional SSO):**
   - `AZURE_TENANT_ID`: Your Azure AD tenant/directory ID
   - `AZURE_CLIENT_ID`: Your Azure AD application/client ID
   - `AZURE_CLIENT_SECRET`: Your Azure AD client secret (keep secure!)
   - `AZURE_AUTHORITY`: Authority URL (e.g., `https://login.microsoftonline.com/common`)
   - `INSTITUTIONAL_EMAIL_DOMAIN`: Your institutional domain (e.g., `ctstate.edu`)
   
   **Google Cloud Platform (OAuth 2.0 & Storage):**
   - `GOOGLE_CLOUD_PROJECT_ID`: Your GCP project ID
   - `GOOGLE_CLIENT_ID`: Your OAuth 2.0 client ID
   - `GOOGLE_CLIENT_SECRET`: Your OAuth 2.0 client secret
   - `GOOGLE_STORAGE_BUCKET_NAME`: Your Cloud Storage bucket name
   - `GOOGLE_APPLICATION_CREDENTIALS`: Base64-encoded service account JSON (see below)
   
   **Apple Sign-In (iOS/macOS/watchOS - Optional):**
   - `APPLE_TEAM_ID`: Your Apple Developer Team ID
   - `APPLE_SERVICES_ID`: Your Apple Services ID
   - `APPLE_KEY_ID`: Your Apple Sign-In Key ID
   - `APPLE_PRIVATE_KEY_PATH`: Path to Apple private key or base64-encoded key content
   
   **Note about Service Account JSON:**
   For `GOOGLE_APPLICATION_CREDENTIALS`, encode your service account JSON file:
   ```bash
   base64 -i config/google-service-account.json | tr -d '\n'
   ```
   Then paste the output as the environment variable value in Vercel.

3. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy your application
   - Your app will be available at `https://poker-therapist.vercel.app` (or your custom domain)

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from Project Root**
   ```bash
   cd /path/to/Poker-Therapist
   vercel
   ```

4. **Set Environment Variables**
   ```bash
   # AI Provider Keys
   vercel env add XAI_API_KEY
   vercel env add OPENAI_API_KEY
   vercel env add ANTHROPIC_API_KEY
   vercel env add GOOGLE_API_KEY
   vercel env add GOOGLE_AI_API_KEY
   vercel env add PERPLEXITY_API_KEY
   vercel env add AUTHORIZED_EMAILS
   
   # Authentication
   vercel env add JWT_SECRET_KEY
   
   # Microsoft Azure AD
   vercel env add AZURE_TENANT_ID
   vercel env add AZURE_CLIENT_ID
   vercel env add AZURE_CLIENT_SECRET
   vercel env add AZURE_AUTHORITY
   vercel env add INSTITUTIONAL_EMAIL_DOMAIN
   
   # Google Cloud Platform
   vercel env add GOOGLE_CLOUD_PROJECT_ID
   vercel env add GOOGLE_CLIENT_ID
   vercel env add GOOGLE_CLIENT_SECRET
   vercel env add GOOGLE_STORAGE_BUCKET_NAME
   vercel env add GOOGLE_APPLICATION_CREDENTIALS
   
   # Apple Sign-In (optional)
   vercel env add APPLE_TEAM_ID
   vercel env add APPLE_SERVICES_ID
   vercel env add APPLE_KEY_ID
   vercel env add APPLE_PRIVATE_KEY_PATH
   ```

5. **Deploy to Production**
   ```bash
   vercel --prod
   ```

## Configuration Files

### vercel.json
The main configuration file that defines:
- Build settings
- Routes and redirects
- Environment variable references (using Vercel secrets)
- Serverless function configuration

### .vercelignore
Specifies files and directories to exclude from deployment:
- Test files
- Documentation
- Development dependencies
- Database files
- IDE configuration

### api/index.py
The serverless function entrypoint that wraps the FastAPI application for Vercel.

## Authentication Setup for Vercel Deployment

### Overview
The Poker Therapist application supports multiple authentication providers:
1. **Microsoft Azure AD** - For Windows accounts and institutional SSO (e.g., @ctstate.edu)
2. **Google OAuth 2.0** - For Google accounts and GCP API access
3. **Apple Sign-In** - For iOS, macOS, and watchOS apps

For detailed setup instructions for each provider, see [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md).

### Quick Authentication Setup

#### 1. Microsoft Azure AD (Required for Institutional SSO)

**Step 1: Register Application in Azure Portal**
1. Go to [Azure Portal](https://portal.azure.com) → Azure Active Directory → App registrations
2. Click "New registration"
3. Name: "Poker Therapist"
4. Supported account types: 
   - For institutional SSO only: "Accounts in this organizational directory only"
   - For multi-tenant: "Accounts in any organizational directory"
5. Redirect URI: Add `https://your-vercel-domain.vercel.app/auth/callback`
6. Click "Register"

**Step 2: Create Client Secret**
1. Go to "Certificates & secrets" → "New client secret"
2. Description: "Vercel Production"
3. Expires: 24 months
4. Copy the secret value immediately (shown only once)

**Step 3: Configure API Permissions**
1. Go to "API permissions" → "Add a permission" → "Microsoft Graph"
2. Add delegated permissions: `User.Read`, `email`, `profile`, `openid`, `offline_access`
3. Click "Grant admin consent" (requires admin)

**Step 4: Add to Vercel**
- `AZURE_TENANT_ID`: From Overview page (Directory/tenant ID)
- `AZURE_CLIENT_ID`: From Overview page (Application/client ID)
- `AZURE_CLIENT_SECRET`: From step 2
- `AZURE_AUTHORITY`: `https://login.microsoftonline.com/{tenant-id}` or `https://login.microsoftonline.com/common`
- `INSTITUTIONAL_EMAIL_DOMAIN`: Your domain (e.g., `ctstate.edu`)

#### 2. Google Cloud Platform (Required for OAuth & Cloud Storage)

**Step 1: Create GCP Project**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project: "Poker Therapist Production"
3. Note the Project ID

**Step 2: Enable APIs**
1. Navigate to "APIs & Services" → "Library"
2. Enable: Cloud Storage API, Cloud Identity API

**Step 3: Create OAuth 2.0 Credentials**
1. Go to "APIs & Services" → "Credentials" → "Create Credentials" → "OAuth client ID"
2. Application type: Web application
3. Name: "Poker Therapist Vercel"
4. Authorized redirect URIs: `https://your-vercel-domain.vercel.app/google/callback`
5. Copy Client ID and Client Secret

**Step 4: Create Service Account for Cloud Storage**
1. Go to "IAM & Admin" → "Service Accounts" → "Create Service Account"
2. Name: "poker-therapist-vercel"
3. Grant role: "Storage Object Admin"
4. Click "Done"
5. Click on service account → "Keys" → "Add Key" → "Create new key" → JSON
6. Download the JSON file
7. Convert to base64 for Vercel:
   ```bash
   base64 -i service-account.json | tr -d '\n'
   ```

**Step 5: Create Cloud Storage Bucket**
1. Go to "Cloud Storage" → "Create Bucket"
2. Name: `poker-therapist-prod` (must be globally unique)
3. Location: Choose region closest to your users
4. Access control: Uniform
5. Add service account with "Storage Object Admin" permission

**Step 6: Add to Vercel**
- `GOOGLE_CLOUD_PROJECT_ID`: From step 1
- `GOOGLE_CLIENT_ID`: From step 3
- `GOOGLE_CLIENT_SECRET`: From step 3
- `GOOGLE_STORAGE_BUCKET_NAME`: From step 5
- `GOOGLE_APPLICATION_CREDENTIALS`: Base64 string from step 4

#### 3. Apple Sign-In (Optional - For iOS/macOS/watchOS)

**Step 1: Register App ID**
1. Go to [Apple Developer Portal](https://developer.apple.com/account)
2. Certificates, Identifiers & Profiles → Identifiers → App IDs
3. Create new: Bundle ID `com.therapyrex.app`
4. Enable "Sign in with Apple" capability

**Step 2: Create Services ID**
1. Create Services ID: `com.therapyrex.signin`
2. Enable "Sign in with Apple"
3. Configure: Add domain and return URL for your Vercel deployment

**Step 3: Create Private Key**
1. Keys → Create new key
2. Enable "Sign in with Apple"
3. Download .p8 file (cannot re-download)
4. Note the Key ID
5. Convert to base64 or upload to secure location

**Step 4: Add to Vercel**
- `APPLE_TEAM_ID`: From Membership page
- `APPLE_SERVICES_ID`: From step 2
- `APPLE_KEY_ID`: From step 3
- `APPLE_PRIVATE_KEY_PATH`: Base64-encoded .p8 content or secure URL

### Security Notes for Vercel Deployment

1. **Never commit secrets to repository** - Use Vercel's environment variables
2. **Use Vercel secrets** - For sensitive values, use `vercel secrets` (prefixed with `@`)
3. **Separate environments** - Use different credentials for Preview and Production
4. **Rotate credentials regularly** - Set reminders to rotate secrets every 6-12 months
5. **Monitor usage** - Check Vercel logs and provider audit logs regularly
6. **Enable 2FA** - Enable two-factor authentication on all provider accounts

## API Endpoints

After deployment, your API will be available at:
- Health check: `https://your-app.vercel.app/health`
- API docs: `https://your-app.vercel.app/docs`
- Root: `https://your-app.vercel.app/`

### Available Routes
- `/api/triage` - Triage endpoints
- `/api/deep-session` - Deep session endpoints
- `/api/analyze` - Analysis endpoints
- `/api/tracking` - Tracking endpoints

## CORS Configuration

The FastAPI application is pre-configured to allow requests from:
- `http://localhost:3000` (local development)
- `http://localhost:8080` (local development)
- `http://localhost:5173` (local development)
- `https://*.vercel.app` (Vercel preview deployments)
- `https://poker-therapist.vercel.app` (production)

## Limitations

### Vercel Serverless Functions
- Maximum execution time: 10 seconds (Hobby), 60 seconds (Pro)
- Maximum payload size: 4.5 MB
- Maximum Lambda size: 50 MB (configured in vercel.json)

### Not Supported on Vercel
- Long-running processes
- WebSocket connections (for real-time voice streaming)
- File system persistence (use external storage)

### Workarounds
For features that require long-running processes or WebSockets:
1. Use Vercel for the API backend
2. Deploy Streamlit app separately (e.g., Streamlit Cloud, Railway, Render)
3. Use external services for real-time features

## Monitoring and Logs

1. **View Logs**
   - Go to your Vercel dashboard
   - Select your project
   - Navigate to the "Logs" tab

2. **Monitor Performance**
   - View function invocations
   - Check response times
   - Monitor error rates

## Custom Domain

To use a custom domain:
1. Go to your project settings in Vercel
2. Navigate to "Domains"
3. Add your custom domain
4. Update DNS records as instructed

## Troubleshooting

### Build Fails
- Check that all dependencies are listed in `requirements.txt`
- Verify that Python version is compatible (3.12+)
- Check build logs in Vercel dashboard

### Import Errors
- Ensure all modules are properly imported in `api/index.py`
- Verify that the project structure is correct
- Check that all required files are not in `.vercelignore`

### Environment Variables Not Working
- Verify variables are set in Vercel dashboard
- Check variable names match those in the code
- Redeploy after adding/updating variables

### CORS Issues
- Verify allowed origins in `backend/api/main.py`
- Check that requests include proper headers
- Test with different origins

## Updates and Redeployment

Vercel automatically redeploys when you push to your connected Git repository:
1. Push changes to your repository
2. Vercel detects the change
3. Automatic build and deployment starts
4. New version goes live

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/runtimes#official-runtimes/python)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

## Support

For issues specific to Vercel deployment:
- Check Vercel [Status Page](https://www.vercel-status.com/)
- Visit [Vercel Community](https://github.com/vercel/vercel/discussions)
- Review [Vercel Examples](https://github.com/vercel/examples)

For application-specific issues:
- Check the main README.md
- Review DEPLOYMENT_CHECKLIST.md
- Open an issue on GitHub

For authentication setup:
- See [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) for detailed provider setup
- See [AUTH_QUICKSTART.md](AUTH_QUICKSTART.md) for quick start guide
- See [DEPLOYMENT_VERIFICATION.md](DEPLOYMENT_VERIFICATION.md) for testing procedures

## Post-Deployment Verification

After deploying to Vercel, verify that everything works correctly:

### 1. Basic API Health Check
```bash
curl https://your-app.vercel.app/health
# Expected: {"status": "healthy"}

curl https://your-app.vercel.app/
# Expected: {"message": "Therapy Rex API", "version": "1.0.0", "docs": "/docs"}
```

### 2. Test API Documentation
Visit `https://your-app.vercel.app/docs` in your browser to see the interactive API documentation.

### 3. Test Authentication Endpoints

**Microsoft Authentication:**
```bash
curl https://your-app.vercel.app/auth/microsoft/authorize
# Should return authorization URL
```

**Google Authentication:**
```bash
curl https://your-app.vercel.app/auth/google/authorize
# Should return authorization URL
```

### 4. Test Complete Authentication Flow

1. **Test Microsoft SSO:**
   - Navigate to the authorization URL
   - Sign in with your institutional email (e.g., @ctstate.edu)
   - Verify redirect back to application
   - Check that JWT token is generated

2. **Test Google OAuth:**
   - Navigate to Google authorization URL
   - Sign in with Google account
   - Verify OAuth flow completes
   - Test Google Cloud Storage access

3. **Test Apple Sign-In (if configured):**
   - Use iOS/macOS app to test Apple Sign-In
   - Verify authentication completes
   - Check token validation

### 5. Monitor Vercel Logs
1. Go to Vercel dashboard
2. Select your project
3. Click "Logs" tab
4. Watch for errors during authentication attempts

### 6. Test Environment Variables
```bash
# Test that environment variables are loaded
curl https://your-app.vercel.app/api/health
# Check logs for any missing environment variable errors
```

### 7. Security Checklist
- [ ] All secrets are stored as Vercel environment variables (not in code)
- [ ] HTTPS is enabled (automatic on Vercel)
- [ ] CORS origins are properly configured
- [ ] JWT secret is cryptographically secure (at least 32 bytes)
- [ ] Authentication providers are using production credentials
- [ ] Redirect URIs match exactly (including protocol and trailing slashes)
- [ ] Service account has minimum required permissions
- [ ] Rate limiting is configured
- [ ] Audit logging is enabled

### 8. Performance Testing
- Test API response times from different regions
- Check serverless function cold start times
- Monitor function execution duration in Vercel dashboard
- Verify function doesn't exceed 10-second timeout (Hobby) or 60 seconds (Pro)

### 9. Common Issues and Solutions

**Issue: "Module not found" errors**
- Solution: Ensure all dependencies are in `requirements.txt`
- Check that imports use correct paths
- Verify Python version compatibility

**Issue: Authentication redirects fail**
- Solution: Verify redirect URIs exactly match in provider consoles
- Check that domain is correctly configured
- Ensure environment variables are set correctly

**Issue: Service account authentication fails**
- Solution: Verify base64 encoding of service account JSON
- Check that service account has required permissions
- Ensure Cloud Storage bucket exists and is accessible

**Issue: Function timeout**
- Solution: Optimize long-running operations
- Consider using async operations
- Upgrade to Vercel Pro for 60-second timeout

**Issue: Environment variables not loaded**
- Solution: Redeploy after adding/updating variables
- Check variable names match exactly (case-sensitive)
- Verify secrets are correctly referenced with @ prefix in vercel.json

### 10. Monitoring and Maintenance

**Set up monitoring:**
1. Enable Vercel Analytics
2. Configure Google Cloud Monitoring for GCS
3. Set up Azure AD audit logs
4. Monitor API usage and costs

**Regular maintenance:**
1. Review Vercel logs weekly
2. Rotate credentials every 6-12 months
3. Update dependencies regularly
4. Monitor API usage quotas
5. Review and update CORS origins
6. Test authentication flows monthly

**Cost monitoring:**
1. Check Vercel usage dashboard
2. Monitor GCP costs
3. Review Azure AD usage
4. Set up billing alerts

### Need Help?

If you encounter issues during deployment:
1. Check this guide's troubleshooting section
2. Review [DEPLOYMENT_VERIFICATION.md](DEPLOYMENT_VERIFICATION.md)
3. Check [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md#troubleshooting)
4. Open an issue on GitHub with:
   - Error messages from Vercel logs
   - Steps to reproduce
   - Environment (Vercel region, Python version, etc.)
   - Authentication provider being used
