# Vercel Deployment Checklist for Poker Therapist

Use this checklist to ensure a successful deployment to Vercel with full authentication support.

## Pre-Deployment Setup

### 1. Provider Account Setup
- [ ] Vercel account created and verified
- [ ] Microsoft Azure account with admin access
- [ ] Google Cloud Platform account with billing enabled
- [ ] Apple Developer account (optional, for iOS features)

### 2. Microsoft Azure AD Configuration
- [ ] Azure AD app registered
- [ ] Client secret created and saved securely
- [ ] API permissions configured (`User.Read`, `email`, `profile`, `openid`, `offline_access`)
- [ ] Admin consent granted for API permissions
- [ ] Redirect URIs configured for Vercel domain
- [ ] Tenant ID documented
- [ ] Client ID documented
- [ ] Client secret documented (stored securely, not in code)

### 3. Google Cloud Platform Configuration
- [ ] GCP project created
- [ ] Project billing enabled
- [ ] Cloud Storage API enabled
- [ ] Cloud Identity API enabled
- [ ] OAuth 2.0 credentials created (Web application type)
- [ ] OAuth consent screen configured
- [ ] Redirect URIs configured for Vercel domain
- [ ] Service account created with Storage Object Admin role
- [ ] Service account JSON key downloaded
- [ ] Service account JSON converted to base64
- [ ] Cloud Storage bucket created
- [ ] Bucket permissions configured for service account
- [ ] Project ID documented
- [ ] Client ID documented
- [ ] Client secret documented
- [ ] Bucket name documented

### 4. Apple Developer Configuration (Optional)
- [ ] Apple Developer account active ($99/year)
- [ ] App ID registered with Sign in with Apple capability
- [ ] Services ID created
- [ ] Private key (.p8) generated and downloaded
- [ ] Private key converted to base64 or uploaded to secure storage
- [ ] Team ID documented
- [ ] Services ID documented
- [ ] Key ID documented

### 5. AI Provider API Keys
- [ ] xAI API key obtained (for Grok)
- [ ] OpenAI API key obtained (for ChatGPT)
- [ ] Anthropic API key obtained (for Claude) - optional
- [ ] Google AI API key obtained (for Gemini) - optional
- [ ] Perplexity API key obtained - optional

### 6. Security Preparation
- [ ] JWT secret key generated (32+ bytes, cryptographically secure)
- [ ] All secrets stored in password manager or secure vault
- [ ] `.env.local` file removed or not committed to repository
- [ ] Service account JSON file not committed to repository
- [ ] Apple private key not committed to repository

## Vercel Deployment

### 7. Repository Connection
- [ ] Repository pushed to GitHub
- [ ] Vercel account connected to GitHub
- [ ] Repository imported in Vercel dashboard
- [ ] Vercel project name configured
- [ ] Production branch set (usually `main` or `master`)

### 8. Environment Variables - Core
Navigate to Project Settings → Environment Variables in Vercel dashboard

**Authentication:**
- [ ] `JWT_SECRET_KEY` added
- [ ] `AUTHORIZED_EMAILS` added (comma-separated)

**AI Providers:**
- [ ] `XAI_API_KEY` added
- [ ] `OPENAI_API_KEY` added
- [ ] `ANTHROPIC_API_KEY` added (if using)
- [ ] `GOOGLE_API_KEY` added (if using)
- [ ] `GOOGLE_AI_API_KEY` added (if using)
- [ ] `PERPLEXITY_API_KEY` added (if using)

### 9. Environment Variables - Microsoft Azure
- [ ] `AZURE_TENANT_ID` added
- [ ] `AZURE_CLIENT_ID` added
- [ ] `AZURE_CLIENT_SECRET` added
- [ ] `AZURE_AUTHORITY` added
- [ ] `INSTITUTIONAL_EMAIL_DOMAIN` added (e.g., `ctstate.edu`)

### 10. Environment Variables - Google Cloud
- [ ] `GOOGLE_CLOUD_PROJECT_ID` added
- [ ] `GOOGLE_CLIENT_ID` added
- [ ] `GOOGLE_CLIENT_SECRET` added
- [ ] `GOOGLE_STORAGE_BUCKET_NAME` added
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` added (base64-encoded JSON)

### 11. Environment Variables - Apple (Optional)
- [ ] `APPLE_TEAM_ID` added
- [ ] `APPLE_SERVICES_ID` added
- [ ] `APPLE_KEY_ID` added
- [ ] `APPLE_PRIVATE_KEY_PATH` added (base64-encoded .p8 content)

### 12. Deployment Configuration
- [ ] `vercel.json` reviewed and correct
- [ ] `.vercelignore` configured to exclude unnecessary files
- [ ] `api/index.py` handler verified
- [ ] Python version specified (3.12+)
- [ ] Requirements.txt up to date

### 13. Deploy
- [ ] Clicked "Deploy" in Vercel dashboard
- [ ] Build completed successfully
- [ ] No build errors in logs
- [ ] Deployment URL generated

## Post-Deployment Verification

### 14. Basic Health Checks
- [ ] Root endpoint accessible: `https://your-app.vercel.app/`
- [ ] Health endpoint returns success: `https://your-app.vercel.app/health`
- [ ] API docs accessible: `https://your-app.vercel.app/docs`
- [ ] No 500 errors in initial requests

### 15. Authentication Flow Testing

**Microsoft Azure AD:**
- [ ] Authorization URL endpoint works
- [ ] Can initiate login with institutional email
- [ ] Redirect back to application works
- [ ] JWT token is generated correctly
- [ ] Token validation works
- [ ] User profile data retrieved successfully
- [ ] Refresh token flow works

**Google OAuth:**
- [ ] Authorization URL endpoint works
- [ ] Can initiate Google sign-in
- [ ] OAuth consent screen displays correctly
- [ ] Redirect back to application works
- [ ] Access token received
- [ ] Can access Google Cloud Storage
- [ ] File upload/download works

**Apple Sign-In (if configured):**
- [ ] Authorization flow works from iOS app
- [ ] Token validation on backend works
- [ ] User data retrieved correctly

### 16. API Functionality
- [ ] All API routes accessible
- [ ] Authentication middleware works
- [ ] Protected endpoints require valid token
- [ ] Unauthorized requests are rejected (401)
- [ ] CORS configured correctly
- [ ] Request/response times acceptable

### 17. Error Handling
- [ ] 404 errors for invalid routes
- [ ] 401 errors for unauthorized requests
- [ ] 403 errors for forbidden resources
- [ ] 500 errors logged correctly
- [ ] Error messages don't expose sensitive info

### 18. Security Audit
- [ ] HTTPS enabled (automatic on Vercel)
- [ ] Environment variables not exposed in client
- [ ] CORS origins restricted (not `*`)
- [ ] JWT tokens use secure algorithm (HS256 or RS256)
- [ ] Token expiration configured (24 hours or less)
- [ ] Sensitive data not logged
- [ ] Rate limiting enabled
- [ ] SQL injection protection enabled (if using SQL)
- [ ] XSS protection headers set

### 19. Monitoring Setup
- [ ] Vercel Analytics enabled
- [ ] Error tracking configured
- [ ] Log retention period set
- [ ] Billing alerts configured
- [ ] Usage quotas monitored
- [ ] Uptime monitoring set up (optional)

### 20. Documentation
- [ ] Deployment URL documented
- [ ] Environment variables documented in team wiki/docs
- [ ] Credential rotation schedule documented
- [ ] Emergency contact information documented
- [ ] Runbook created for common issues

## Production Readiness

### 21. Domain Configuration (Optional)
- [ ] Custom domain purchased
- [ ] DNS configured
- [ ] Domain added in Vercel
- [ ] SSL certificate issued
- [ ] Redirect URIs updated in all providers
- [ ] Environment variables updated with production domain

### 22. Backup and Recovery
- [ ] Database backup strategy defined
- [ ] Cloud Storage backup configured
- [ ] Disaster recovery plan documented
- [ ] Rollback procedure tested

### 23. Performance Optimization
- [ ] Cold start times acceptable (<3 seconds)
- [ ] Average response times acceptable (<500ms)
- [ ] Function memory usage optimized
- [ ] Unnecessary dependencies removed
- [ ] Function size under limits

### 24. Compliance and Privacy
- [ ] Privacy policy created and linked
- [ ] Terms of service created
- [ ] Cookie consent implemented (if applicable)
- [ ] GDPR compliance reviewed (if applicable)
- [ ] Data retention policies defined
- [ ] User data deletion process implemented

### 25. Team Access
- [ ] Vercel team members invited
- [ ] Appropriate access levels assigned
- [ ] 2FA enabled for all team members
- [ ] Service account access reviewed
- [ ] Emergency access procedures documented

## Ongoing Maintenance

### 26. Regular Tasks (Weekly)
- [ ] Review Vercel logs for errors
- [ ] Check authentication success rates
- [ ] Monitor API usage and costs
- [ ] Review security alerts

### 27. Regular Tasks (Monthly)
- [ ] Test all authentication flows
- [ ] Review and update dependencies
- [ ] Check for security advisories
- [ ] Review and optimize costs
- [ ] Test disaster recovery procedures

### 28. Regular Tasks (Quarterly)
- [ ] Rotate JWT secret key
- [ ] Review and update API permissions
- [ ] Audit user access and permissions
- [ ] Review and update documentation
- [ ] Conduct security assessment

### 29. Regular Tasks (Annually)
- [ ] Rotate all service credentials
- [ ] Review and renew SSL certificates (if using custom)
- [ ] Review and optimize architecture
- [ ] Update privacy policy and terms
- [ ] Conduct comprehensive security audit
- [ ] Renew Apple Developer account (if using)

## Emergency Procedures

### 30. If Credentials are Compromised
- [ ] Immediately rotate affected credentials
- [ ] Revoke compromised tokens
- [ ] Review access logs for suspicious activity
- [ ] Update environment variables in Vercel
- [ ] Redeploy application
- [ ] Notify affected users if necessary
- [ ] Document incident and response

### 31. If Deployment Fails
- [ ] Check Vercel build logs
- [ ] Verify environment variables are set
- [ ] Test locally with production-like environment
- [ ] Rollback to previous deployment if needed
- [ ] Fix issues and redeploy
- [ ] Document root cause

### 32. If Authentication Breaks
- [ ] Check provider status pages
- [ ] Verify redirect URIs are correct
- [ ] Check environment variables
- [ ] Review recent changes
- [ ] Test with different accounts
- [ ] Check Vercel logs for errors
- [ ] Contact provider support if needed

## Completion

- [ ] All checklist items completed
- [ ] Application deployed successfully
- [ ] All authentication flows tested
- [ ] Team trained on maintenance procedures
- [ ] Documentation updated
- [ ] Stakeholders notified

**Deployed By:** _________________  
**Date:** _________________  
**Deployment URL:** _________________  
**Notes:** _________________

---

## Quick Reference

### Essential URLs
- **Vercel Dashboard:** https://vercel.com/dashboard
- **Azure Portal:** https://portal.azure.com
- **Google Cloud Console:** https://console.cloud.google.com
- **Apple Developer Portal:** https://developer.apple.com/account

### Support Resources
- **Vercel Docs:** https://vercel.com/docs
- **Azure AD Docs:** https://docs.microsoft.com/azure/active-directory/
- **Google OAuth Docs:** https://developers.google.com/identity/protocols/oauth2
- **Apple Sign-In Docs:** https://developer.apple.com/sign-in-with-apple/

### Project Documentation
- [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) - Detailed deployment guide
- [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) - Complete authentication setup
- [AUTH_QUICKSTART.md](AUTH_QUICKSTART.md) - Quick authentication setup
- [DEPLOYMENT_VERIFICATION.md](DEPLOYMENT_VERIFICATION.md) - Testing procedures
- [README.md](README.md) - Project overview
