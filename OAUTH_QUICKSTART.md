# Quick Start: OAuth Authentication

This is a condensed guide to get OAuth authentication up and running quickly for Poker Therapist.

## Prerequisites

```bash
pip install -r requirements.txt
```

## Option 1: Microsoft Azure AD (Institutional SSO)

**Use this for ctstate.edu or other organizational accounts**

### 1. Azure Portal Setup (5 minutes)

1. Go to https://portal.azure.com
2. Navigate to **Azure Active Directory** → **App registrations** → **New registration**
3. Settings:
   - Name: `Poker Therapist`
   - Account types: `Accounts in any organizational directory`
   - Redirect URI: `http://localhost:8501/`
4. After creation:
   - Go to **API permissions** → Add: `User.Read`, `openid`, `email`, `profile`
   - Go to **Certificates & secrets** → Create new client secret → **Copy the value**

### 2. Environment Configuration

Create `.env.local`:

```bash
MICROSOFT_CLIENT_ID=your-application-id-from-overview
MICROSOFT_CLIENT_SECRET=your-client-secret-value
MICROSOFT_TENANT_ID=common
MICROSOFT_REDIRECT_URI=http://localhost:8501/

JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

For ctstate.edu only access, use your tenant ID instead of `common`.

### 3. Test

```bash
streamlit run chatbot_app.py
```

Click "Sign in with Microsoft" in the sidebar.

---

## Option 2: Google OAuth

**Use this for Google accounts and GCP API access**

### 1. Google Cloud Console Setup (5 minutes)

1. Go to https://console.cloud.google.com
2. Create a project or select existing
3. **APIs & Services** → **Credentials** → **Create OAuth client ID**
4. Configure OAuth consent screen if prompted:
   - User type: `External` or `Internal`
   - App name: `Poker Therapist`
   - Add scopes: `userinfo.email`, `userinfo.profile`, `openid`
5. Create OAuth client:
   - Application type: `Web application`
   - Authorized redirect URIs: `http://localhost:8501/`
6. **Copy Client ID and Client Secret**

### 2. Environment Configuration

Create `.env.local`:

```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8501/

JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

### 3. Test

```bash
streamlit run chatbot_app.py
```

Click "Sign in with Google" in the sidebar.

---

## Option 3: Both Providers

You can configure both Microsoft and Google at the same time:

```bash
# Microsoft
MICROSOFT_CLIENT_ID=...
MICROSOFT_CLIENT_SECRET=...
MICROSOFT_TENANT_ID=common
MICROSOFT_REDIRECT_URI=http://localhost:8501/

# Google
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8501/

# JWT
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

Both buttons will appear in the sidebar.

---

## Production Deployment

### Update Redirect URIs

For production (e.g., Vercel):

1. **Microsoft**: Azure Portal → App Registration → Authentication → Add `https://your-domain.vercel.app/`
2. **Google**: Cloud Console → Credentials → OAuth client → Add `https://your-domain.vercel.app/`

### Set Environment Variables

In your deployment platform (Vercel, Heroku, etc.):

- Add all OAuth environment variables
- Update redirect URIs to production URLs
- **Never** commit secrets to git

### Vercel Example

```bash
vercel env add MICROSOFT_CLIENT_ID
vercel env add MICROSOFT_CLIENT_SECRET
vercel env add GOOGLE_CLIENT_ID
vercel env add GOOGLE_CLIENT_SECRET
vercel env add JWT_SECRET_KEY
```

---

## Troubleshooting

### "OAuth provider not configured"

**Fix**: Check your `.env.local` file exists and has the correct variable names.

### "Invalid redirect URI"

**Fix**: Make sure redirect URI in code matches exactly what's in Azure/Google portal (including trailing `/`).

### "AADSTS50011" (Microsoft)

**Fix**: Add the exact redirect URI from error message to Azure portal.

### "redirect_uri_mismatch" (Google)

**Fix**: Add the exact redirect URI to authorized list in Google Cloud Console.

---

## Testing Tips

1. **Start with one provider** (Microsoft or Google, not both at first)
2. **Use localhost** for initial testing (`http://localhost:8501/`)
3. **Check browser console** for JavaScript errors
4. **Clear browser cache** if having issues
5. **Test with personal account first** before institutional accounts

---

## Next Steps

- ✅ Basic OAuth working? → See [OAUTH_SETUP.md](OAUTH_SETUP.md) for advanced configuration
- 🔒 Security concerns? → See [SECURITY.md](SECURITY.md) for security best practices
- 🐛 Issues? → Check the detailed troubleshooting in [OAUTH_SETUP.md](OAUTH_SETUP.md)

---

## Common Scenarios

### Scenario 1: University/College (e.g., ctstate.edu)

Use **Microsoft Azure AD** with your institution's tenant ID:

```bash
MICROSOFT_TENANT_ID=your-institution-tenant-id  # Get from IT department
```

### Scenario 2: Personal Use + GCP Integration

Use **Google OAuth** to authenticate and access Google Cloud APIs:

```bash
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

### Scenario 3: Enterprise Deployment

Use **both** Microsoft (for employees) and Google (for external users):

```bash
# Configure both in .env.local
```

Users can choose which provider to use at login.

---

## Support

- 📖 **Full Documentation**: [OAUTH_SETUP.md](OAUTH_SETUP.md)
- 🔒 **Security Guide**: [SECURITY.md](SECURITY.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/JohnDaWalka/Poker-Therapist/issues)
