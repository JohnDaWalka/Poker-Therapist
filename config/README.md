# Config Directory

This directory is for storing authentication credentials and configuration files.

## ⚠️ SECURITY NOTICE

**CRITICAL**: All files in this directory contain sensitive credentials and **MUST NEVER** be committed to git.

## Files Stored Here

### Google Cloud Platform
- `google-service-account.json` - Service account credentials for GCP APIs
  - Download from: Google Cloud Console → IAM & Admin → Service Accounts
  - Required for: Cloud Storage, Speech-to-Text, Text-to-Speech APIs

### Apple Developer
- `apple-auth-key.p8` - Private key for Sign in with Apple
  - Download from: Apple Developer Portal → Keys
  - Required for: Server-side Apple Sign-In validation

## Security Best Practices

1. **Never Commit Credentials**
   - All credential files are excluded in `.gitignore`
   - Double-check with `git status` before committing

2. **File Permissions**
   - Keep credential files read-only: `chmod 400 config/*.json config/*.p8`
   - Restrict directory access: `chmod 700 config/`

3. **Separate Environments**
   - Use different credentials for dev, staging, and production
   - Never share production credentials

4. **Rotate Regularly**
   - Rotate service account keys every 90 days
   - Rotate Apple private keys every 6 months
   - Update keys in all environments after rotation

5. **Secure Storage**
   - For production, use secure secret management:
     - Azure Key Vault
     - Google Secret Manager
     - AWS Secrets Manager
     - HashiCorp Vault

## Verification

After adding credential files, verify they are excluded from git:

```bash
# Check that no credential files appear
git status

# Verify .gitignore is working
git check-ignore config/*.json config/*.p8
# Should output: config/*.json and config/*.p8
```

## Getting Credentials

See the following guides for detailed instructions:

- **Google Cloud**: [GOOGLE_CLOUD_SETUP.md](../GOOGLE_CLOUD_SETUP.md)
- **Apple Developer**: [CREDENTIAL_CONFIGURATION_GUIDE.md](../CREDENTIAL_CONFIGURATION_GUIDE.md)
- **Microsoft Azure**: [CREDENTIAL_CONFIGURATION_GUIDE.md](../CREDENTIAL_CONFIGURATION_GUIDE.md)

## Troubleshooting

**"Service account credentials not found"**
- Ensure file path in `.env.local` matches actual file location
- Check file permissions (must be readable)
- Verify JSON file is valid (not corrupted)

**"Permission denied"**
- Service account needs appropriate IAM roles
- For Cloud Storage: "Storage Object Admin" role
- Verify in GCP Console → IAM & Admin → IAM

**"Invalid private key"**
- Ensure .p8 file is valid PEM format
- Check file wasn't corrupted during download
- Verify file encoding is UTF-8
