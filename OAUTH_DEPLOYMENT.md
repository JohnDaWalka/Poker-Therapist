# OAuth Production Deployment Checklist

This checklist ensures a smooth and secure deployment of OAuth authentication to production.

## Pre-Deployment

### 1. OAuth Provider Configuration

#### Microsoft Azure AD
- [ ] Production app registered in Azure Portal
- [ ] Production redirect URI configured: `https://your-domain.com/`
- [ ] API permissions granted and admin consent obtained
- [ ] Client secret created and securely stored
- [ ] Tenant ID verified (use specific tenant for institutional SSO)
- [ ] Test with real institutional accounts (e.g., ctstate.edu)

#### Google OAuth
- [ ] Production OAuth client created in Google Cloud Console
- [ ] OAuth consent screen configured with production branding
- [ ] Production redirect URI authorized: `https://your-domain.com/`
- [ ] Scopes reviewed and minimized
- [ ] Test users verified (if internal app)
- [ ] Production credentials secured

#### Apple Sign In (Optional)
- [ ] Services ID configured with production domain
- [ ] Production return URL registered: `https://your-domain.com/`
- [ ] Private key downloaded and securely stored
- [ ] Test with Apple ID accounts
- [ ] Email relay configured (if using private relay)

### 2. Environment Variables

#### Required for All Environments
- [ ] `JWT_SECRET_KEY` - Strong random key (32+ characters)
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] `SESSION_TIMEOUT_MINUTES` - Appropriate timeout (default: 60)
- [ ] `AUTHORIZED_EMAILS` - VIP user list (comma-separated)

#### Microsoft (if enabled)
- [ ] `MICROSOFT_CLIENT_ID`
- [ ] `MICROSOFT_CLIENT_SECRET`
- [ ] `MICROSOFT_TENANT_ID`
- [ ] `MICROSOFT_REDIRECT_URI=https://your-domain.com/`

#### Google (if enabled)
- [ ] `GOOGLE_CLIENT_ID`
- [ ] `GOOGLE_CLIENT_SECRET`
- [ ] `GOOGLE_REDIRECT_URI=https://your-domain.com/`

#### Apple (if enabled)
- [ ] `APPLE_CLIENT_ID`
- [ ] `APPLE_TEAM_ID`
- [ ] `APPLE_KEY_ID`
- [ ] `APPLE_PRIVATE_KEY` (PEM format, properly escaped)
- [ ] `APPLE_REDIRECT_URI=https://your-domain.com/`

### 3. Security Review

- [ ] No secrets committed to git repository
- [ ] `.env.local` in `.gitignore`
- [ ] OAuth secrets stored in secure vault (Azure Key Vault, AWS Secrets Manager, etc.)
- [ ] HTTPS enforced for all redirect URIs
- [ ] CORS origins properly configured
- [ ] Rate limiting configured on authentication endpoints
- [ ] Session timeout appropriate for use case
- [ ] JWT secret is strong and unique per environment

### 4. Code Review

- [ ] All OAuth code reviewed
- [ ] Security best practices followed
- [ ] Error messages don't leak sensitive information
- [ ] Logging configured for security events
- [ ] No hardcoded credentials or test values
- [ ] All TODOs and FIXMEs addressed

## Deployment Steps

### 1. Staging Environment

#### Deploy to Staging
```bash
# Set staging environment variables
export MICROSOFT_CLIENT_ID=staging-client-id
export MICROSOFT_CLIENT_SECRET=staging-secret
export JWT_SECRET_KEY=staging-jwt-secret
# ... other variables

# Deploy application
# (deployment commands depend on your platform)
```

#### Test in Staging
- [ ] Run verification script: `python verify_oauth_setup.py`
- [ ] Test Microsoft authentication end-to-end
- [ ] Test Google authentication end-to-end
- [ ] Test Apple authentication end-to-end (if configured)
- [ ] Verify JWT token creation and validation
- [ ] Test authenticated API endpoints
- [ ] Verify VIP user detection
- [ ] Test session timeout and refresh
- [ ] Check logs for errors or warnings
- [ ] Performance test with concurrent users

### 2. Production Environment

#### Set Production Environment Variables

**Vercel**:
```bash
vercel env add MICROSOFT_CLIENT_ID production
vercel env add MICROSOFT_CLIENT_SECRET production
vercel env add GOOGLE_CLIENT_ID production
vercel env add GOOGLE_CLIENT_SECRET production
vercel env add JWT_SECRET_KEY production
vercel env add SESSION_TIMEOUT_MINUTES production
vercel env add AUTHORIZED_EMAILS production
```

**AWS/Heroku/Other**:
Follow platform-specific documentation for setting environment variables securely.

#### Deploy to Production
```bash
# Verify environment variables are set
# Deploy application
# (platform-specific commands)

# Verify deployment
curl https://your-domain.com/api/auth/health
```

#### Post-Deployment Verification
- [ ] Health check passes: `/api/auth/health`
- [ ] OAuth login buttons appear
- [ ] Microsoft sign-in works
- [ ] Google sign-in works
- [ ] Apple sign-in works (if configured)
- [ ] User profile displays correctly
- [ ] VIP badge shows for authorized users
- [ ] Chat functionality works with OAuth users
- [ ] API authentication works
- [ ] Session persists correctly
- [ ] Logout works properly

### 3. Monitoring Setup

#### Application Monitoring
- [ ] Set up application performance monitoring (APM)
- [ ] Configure error tracking (Sentry, etc.)
- [ ] Monitor authentication success/failure rates
- [ ] Track OAuth provider performance
- [ ] Alert on authentication errors

#### Security Monitoring
- [ ] Monitor for failed authentication attempts
- [ ] Alert on suspicious activity patterns
- [ ] Track token validation failures
- [ ] Monitor for CSRF attempts (invalid state)
- [ ] Log all authentication events

#### Metrics to Track
- [ ] Authentication success rate by provider
- [ ] Average authentication time
- [ ] Token refresh rate
- [ ] Session timeout rate
- [ ] VIP user login frequency
- [ ] Failed authentication attempts

## Post-Deployment

### 1. User Communication

#### Notify Users
- [ ] Announce new OAuth/SSO authentication
- [ ] Provide instructions for signing in
- [ ] Explain benefits (security, convenience)
- [ ] Document any changes to workflow
- [ ] Provide support contact information

#### Documentation
- [ ] Update user documentation
- [ ] Create FAQ for OAuth sign-in
- [ ] Document troubleshooting steps
- [ ] Provide video tutorial (optional)
- [ ] Update support knowledge base

### 2. Support Preparation

#### Support Team Training
- [ ] Train support team on OAuth flow
- [ ] Provide troubleshooting guide
- [ ] Document common issues and solutions
- [ ] Set up support ticket categories
- [ ] Create escalation procedures

#### Common Issues Reference
- [ ] "Invalid redirect URI" - Check provider configuration
- [ ] "State mismatch" - Clear browser cache, retry
- [ ] "Token expired" - Normal, ask user to re-authenticate
- [ ] "VIP access denied" - Verify email in AUTHORIZED_EMAILS
- [ ] "Provider not configured" - Check environment variables

### 3. Maintenance Schedule

#### Regular Tasks
- [ ] Rotate OAuth secrets every 90 days
- [ ] Review and update authorized email list
- [ ] Monitor for security vulnerabilities
- [ ] Update dependencies regularly
- [ ] Review authentication logs weekly
- [ ] Check for provider API changes

#### Quarterly Review
- [ ] Audit VIP user list
- [ ] Review session timeout settings
- [ ] Analyze authentication metrics
- [ ] Update documentation
- [ ] Test disaster recovery procedures
- [ ] Review and renew SSL certificates

## Rollback Plan

### If Issues Occur

#### Immediate Actions
1. Check deployment logs for errors
2. Verify environment variables are set correctly
3. Test authentication flow manually
4. Check provider status pages

#### Rollback Procedure
```bash
# Rollback to previous version
# (platform-specific commands)

# Verify rollback successful
curl https://your-domain.com/health

# Notify users of temporary service restoration
```

#### Legacy Fallback
- [ ] Email-based login still works as fallback
- [ ] Users can continue using application
- [ ] Document issues and resolution plan
- [ ] Schedule fix deployment

## Compliance

### GDPR Compliance
- [ ] Privacy policy updated with OAuth information
- [ ] User consent flow documented
- [ ] Data processing agreements with OAuth providers
- [ ] User data deletion procedures
- [ ] Right to access OAuth data

### Institutional Compliance
- [ ] IT department approval obtained
- [ ] Security review completed
- [ ] Compliance with institutional policies
- [ ] Data retention policies followed
- [ ] Audit logging enabled

### SOC 2 / ISO Compliance (if applicable)
- [ ] Security controls documented
- [ ] Access controls verified
- [ ] Audit trail complete
- [ ] Incident response plan
- [ ] Regular security assessments

## Success Criteria

### Technical
- [x] All OAuth providers working
- [x] Authentication success rate > 99%
- [x] Average authentication time < 3 seconds
- [x] No security vulnerabilities
- [x] Monitoring and alerting active

### Business
- [x] User adoption rate > 80%
- [x] Support tickets < 5% of user base
- [x] User satisfaction score > 4/5
- [x] Reduced authentication-related issues
- [x] Improved security posture

## Emergency Contacts

### Technical Support
- **Primary**: [Your DevOps Team Email/Phone]
- **Secondary**: [Your Development Team Email/Phone]
- **On-Call**: [On-Call Engineer Phone]

### OAuth Providers
- **Microsoft Support**: https://support.microsoft.com/
- **Google Support**: https://support.google.com/
- **Apple Support**: https://developer.apple.com/contact/

### Security Team
- **Security Incident**: [Security Team Email/Phone]
- **Data Breach**: [Breach Response Team]
- **Compliance**: [Compliance Officer Email/Phone]

## Documentation Links

- Setup Guide: [OAUTH_SETUP.md](OAUTH_SETUP.md)
- Quick Start: [OAUTH_QUICKSTART.md](OAUTH_QUICKSTART.md)
- Testing Guide: [OAUTH_TESTING.md](OAUTH_TESTING.md)
- Security Policy: [SECURITY.md](SECURITY.md)
- Implementation Summary: [OAUTH_IMPLEMENTATION_SUMMARY.md](OAUTH_IMPLEMENTATION_SUMMARY.md)

## Sign-Off

### Pre-Deployment Approval
- [ ] Development Lead: _________________ Date: _______
- [ ] Security Team: _________________ Date: _______
- [ ] IT Manager: _________________ Date: _______
- [ ] Product Owner: _________________ Date: _______

### Post-Deployment Verification
- [ ] Production Verified: _________________ Date: _______
- [ ] Monitoring Confirmed: _________________ Date: _______
- [ ] Documentation Updated: _________________ Date: _______
- [ ] Team Notified: _________________ Date: _______

---

**Last Updated**: 2026-01-13
**Version**: 1.0.0
**Maintained By**: Development Team
