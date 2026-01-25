# Vercel API Key Configuration Guide

This guide explains how to configure the new Vercel API key for automated deployments.

## Overview

The Poker Therapist application uses Vercel for serverless deployment. To enable automated deployments via GitHub Actions, you need to configure the Vercel API token as a GitHub secret.

## New Vercel API Key

**Important**: A new Vercel API key has been generated for this project (referenced in PR #114). This key must be configured as a GitHub Secret.

⚠️ **SECURITY NOTICE**: API keys provide access to your Vercel account. Never commit them directly to source control or documentation files. Always store them securely as GitHub Secrets or in environment variables.

## Step-by-Step Configuration

### Step 1: Configure GitHub Secrets

1. **Navigate to Repository Settings**
   - Go to https://github.com/JohnDaWalka/Poker-Therapist
   - Click on **Settings** → **Secrets and variables** → **Actions**

2. **Add VERCEL_TOKEN Secret**
   - Click **New repository secret**
   - Name: `VERCEL_TOKEN`
   - Value: `<your-vercel-api-token>` (use the token from PR #114 or generate a new one from Vercel Dashboard)
   - Click **Add secret**

3. **Add VERCEL_ORG_ID Secret** (if not already configured)
   - Get your Vercel Organization ID:
     ```bash
     vercel whoami
     ```
   - Or find it in Vercel Dashboard → Settings → General
   - Click **New repository secret**
   - Name: `VERCEL_ORG_ID`
   - Value: Your organization ID from Vercel
   - Click **Add secret**

4. **Add VERCEL_PROJECT_ID Secret** (if not already configured)
   - Get your Vercel Project ID:
     ```bash
     vercel project ls
     ```
   - Or find it in Vercel Dashboard → Project Settings → General
   - Click **New repository secret**
   - Name: `VERCEL_PROJECT_ID`
   - Value: Your project ID from Vercel
   - Click **Add secret**

### Step 2: Verify GitHub Actions Workflow

The repository includes a GitHub Actions workflow at `.github/workflows/vercel-deployment.yml` that will:
- Automatically deploy preview deployments for pull requests
- Automatically deploy to production when changes are pushed to main/master branch
- Comment on PRs with the preview deployment URL

### Step 3: Test the Configuration

1. **Trigger a Test Deployment**
   - Go to **Actions** tab in GitHub
   - Select **Vercel Deployment** workflow
   - Click **Run workflow**
   - Select the branch you want to deploy
   - Click **Run workflow**

2. **Verify Deployment Success**
   - Watch the workflow execution
   - Check for any errors in the logs
   - Verify the deployment appears in your Vercel dashboard

### Step 4: Automated Deployments

Once configured, the workflow will automatically:

- **On Pull Requests**:
  - Deploy a preview version to Vercel
  - Comment on the PR with the preview URL
  - Update the preview on each new commit to the PR

- **On Push to Main/Master**:
  - Deploy to production
  - Make the deployment live at your production URL

## Vercel CLI Setup (Optional)

For local deployments and testing, you can also configure the Vercel CLI:

```bash
# Install Vercel CLI
npm install -g vercel@latest

# Login with the API token
vercel login

# Or set the token as an environment variable
export VERCEL_TOKEN=<your-vercel-api-token>

# Deploy from command line
vercel --token=$VERCEL_TOKEN

# Deploy to production
vercel --prod --token=$VERCEL_TOKEN
```

## Environment Variables in Vercel

Don't forget to configure your application environment variables in Vercel:

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add required variables:
   - `OPENAI_API_KEY`
   - `XAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `GOOGLE_AI_API_KEY`
   - `PERPLEXITY_API_KEY`
   - `AUTHORIZED_EMAILS`
   - Any other required environment variables from `.env.example`

## Troubleshooting

### Authentication Errors

If you see authentication errors:
1. Verify the `VERCEL_TOKEN` is correctly set in GitHub Secrets
2. Check that the token hasn't expired
3. Ensure the token has the correct permissions

### Deployment Failures

If deployments fail:
1. Check the GitHub Actions logs for specific error messages
2. Verify `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID` are correct
3. Ensure all required environment variables are set in Vercel
4. Check the Vercel dashboard for deployment logs

### Token Expiration

Vercel API tokens can expire. If you need to regenerate:
1. Go to Vercel Dashboard → Settings → Tokens
2. Create a new token
3. Update the `VERCEL_TOKEN` secret in GitHub

## Security Best Practices

1. **Never commit API keys to source control**
   - Always use GitHub Secrets or environment variables
   - Keep `.env.local` files out of git (already in `.gitignore`)

2. **Use different tokens for different environments**
   - Development token for local testing
   - Production token for automated deployments

3. **Rotate tokens regularly**
   - Generate new tokens periodically
   - Revoke old tokens after replacement

4. **Limit token scope**
   - Create tokens with minimal required permissions
   - Use project-specific tokens when possible

5. **Monitor token usage**
   - Review Vercel audit logs regularly
   - Watch for unauthorized deployment attempts

## Additional Resources

- [Vercel CLI Documentation](https://vercel.com/docs/cli)
- [Vercel API Documentation](https://vercel.com/docs/rest-api)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Vercel GitHub Integration](https://vercel.com/docs/git/vercel-for-github)

## Related Documentation

- [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md) - General Vercel deployment guide
- [VERCEL_SETUP_QUICKSTART.md](./VERCEL_SETUP_QUICKSTART.md) - Quick setup guide
- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - Complete deployment checklist

## Support

For issues with Vercel deployment:
- Check [Vercel Status](https://www.vercel-status.com/)
- Visit [Vercel Community](https://github.com/vercel/vercel/discussions)
- Review workflow logs in GitHub Actions
