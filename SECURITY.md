# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are
currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 5.1.x   | :white_check_mark: |
| 5.0.x   | :x:                |
| 4.0.x   | :white_check_mark: |
| < 4.0   | :x:                |

## Authentication & Authorization

Poker Therapist now supports OAuth 2.0 and OpenID Connect authentication through multiple identity providers:

- **Microsoft Azure AD / Windows Accounts** - For institutional SSO (e.g., ctstate.edu)
- **Google OAuth 2.0** - For Google account authentication and GCP API access
- **Apple Sign In** - For Apple ID authentication (optional)

### Security Best Practices

1. **OAuth Configuration**
   - Never commit OAuth client secrets to version control
   - Use environment variables or secure secret management systems
   - Rotate client secrets regularly (at least every 90 days)
   - Use HTTPS for all redirect URIs in production
   
2. **JWT Session Tokens**
   - Generate a cryptographically secure JWT secret key
   - Set appropriate session timeout (default: 60 minutes)
   - Tokens are signed and verified on each request
   
3. **State Parameter**
   - CSRF protection is enforced via state parameter validation
   - State tokens are generated securely using `secrets.token_urlsafe()`
   
4. **Redirect URIs**
   - Only use registered redirect URIs
   - Validate redirect URIs on the server side
   - Use exact matching for redirect URIs
   
5. **Scope Management**
   - Request only necessary OAuth scopes
   - Review and audit requested permissions regularly
   
6. **Production Deployment**
   - Always use HTTPS in production
   - Implement rate limiting on OAuth endpoints
   - Monitor for suspicious authentication attempts
   - Enable logging and audit trails

### Environment Variables

The following environment variables must be kept secure:

- `MICROSOFT_CLIENT_SECRET` - Microsoft OAuth client secret
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `APPLE_PRIVATE_KEY` - Apple Sign In private key
- `JWT_SECRET_KEY` - JWT session token signing key

**Never** commit these values to source control. Use:
- `.env.local` (gitignored)
- Environment variable management systems (Azure Key Vault, AWS Secrets Manager, etc.)
- Vercel/deployment platform secret storage

## Reporting a Vulnerability

If you discover a security vulnerability in Poker Therapist, please report it responsibly:

1. **Do NOT** open a public GitHub issue
2. **Email** the security details to: [your-security-email@example.com]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **Initial Response**: Within 48 hours of report
- **Status Update**: Within 7 days of report
- **Fix Timeline**: Varies based on severity
  - Critical: 24-48 hours
  - High: 7 days
  - Medium: 30 days
  - Low: 90 days

### Disclosure Policy

We follow coordinated vulnerability disclosure:

1. Vulnerability is reported privately
2. We confirm and investigate the report
3. A fix is developed and tested
4. The fix is deployed to production
5. Public disclosure occurs after fix is deployed (minimum 30 days after initial report)

## Security Features

### OAuth/SSO Authentication

- Industry-standard OAuth 2.0 and OpenID Connect protocols
- Support for enterprise identity providers (Microsoft Azure AD)
- JWT-based session management
- CSRF protection via state parameter validation
- Automatic token refresh and expiration handling

### Data Protection

- Conversation history stored in SQLite database
- User data associated with verified email addresses
- No storage of OAuth access tokens in database
- Session tokens expire after configured timeout

### API Security

- API keys stored in environment variables only
- No API keys in client-side code
- Rate limiting on API endpoints (when deployed)
- CORS configuration for allowed origins

## Compliance

### GDPR Compliance

Users can:
- Request deletion of their conversation history via the UI
- Export their data (contact administrators)
- Revoke OAuth permissions via their identity provider

### Institutional Compliance

For institutional deployments (e.g., ctstate.edu):
- Use organization-specific tenant IDs for Azure AD
- Configure appropriate data retention policies
- Enable audit logging for compliance requirements
- Follow institution's security and privacy policies

## Security Updates

Security updates are applied as follows:

1. Dependencies are regularly updated via Dependabot
2. Security patches are prioritized and applied quickly
3. Users are notified of critical security updates
4. Changelog includes security-related changes

## Contact

For security concerns or questions:
- Email: [your-security-email@example.com]
- GitHub Issues: For non-security bugs only
- Documentation: See OAUTH_SETUP.md for OAuth security guidelines
