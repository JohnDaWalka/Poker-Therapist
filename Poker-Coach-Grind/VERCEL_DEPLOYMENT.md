# Vercel Deployment Guide for Poker-Coach-Grind (poker-coaches)

This guide explains how to deploy the Poker-Coach-Grind API as a separate Vercel project.

## Overview

The Poker-Coach-Grind API is deployed as a separate Vercel project called **poker-coaches** with its root directory set to the `Poker-Coach-Grind` folder. This allows it to have its own independent deployment, scaling, and configuration.

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. The repository connected to Vercel: `JohnDaWalka/Poker-Therapist`

## Deployment Setup

### Step 1: Create New Vercel Project

1. Go to https://vercel.com/new
2. Import the `JohnDaWalka/Poker-Therapist` repository (if not already imported)
3. Click "Add Another Project" or create a new project

### Step 2: Configure Project Settings

**Project Name**: `poker-coaches`

**Root Directory**: `Poker-Coach-Grind`
- Click "Edit" next to Root Directory
- Select or type `Poker-Coach-Grind`
- This tells Vercel to use the Poker-Coach-Grind directory as the project root

**Framework Preset**: Other (or leave as detected)

**Build Command**: Leave empty (Vercel auto-detects Python)

**Output Directory**: Leave empty

### Step 3: Configure Environment Variables

Add the following environment variables in the Vercel dashboard under Settings → Environment Variables:

#### Required Variables
- `DATABASE_URL` (optional): Database connection string if using external database
- `ENVIRONMENT`: Set to `production`

#### Optional Variables
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins
  - Example: `https://poker-therapist.vercel.app,https://your-frontend.vercel.app`
- `COINGECKO_API_KEY`: For cryptocurrency price tracking (optional)
- `N8N_WEBHOOK_URL`: For n8n integration (optional)

### Step 4: Deploy

1. Click "Deploy"
2. Vercel will:
   - Read `Poker-Coach-Grind/vercel.json`
   - Install dependencies from `Poker-Coach-Grind/requirements.txt`
   - Deploy the FastAPI app via `Poker-Coach-Grind/api/index.py`

Your API will be available at: `https://poker-coaches.vercel.app`

## API Endpoints

After deployment, your API endpoints will be:

- **Root**: `https://poker-coaches.vercel.app/`
- **Health Check**: `https://poker-coaches.vercel.app/health`
- **API Docs**: `https://poker-coaches.vercel.app/docs`
- **Bankroll**: `https://poker-coaches.vercel.app/api/bankroll/*`
- **Hands**: `https://poker-coaches.vercel.app/api/hands/*`
- **Crypto**: `https://poker-coaches.vercel.app/api/crypto/*`
- **n8n Integration**: `https://poker-coaches.vercel.app/api/n8n/*`

## Configuration Files

### vercel.json
Located at `Poker-Coach-Grind/vercel.json`, this file configures:
- Project name: `poker-coaches`
- Routes: All routes go to `api/index.py`
- Function settings: 2048MB memory, 60s timeout

### api/index.py
Entry point for Vercel's Python runtime. Imports and exports the FastAPI app from `main.py`.

### .vercelignore
Excludes unnecessary files from deployment:
- CLI tools
- UI components
- Documentation
- Test files
- n8n workflows

## Vercel Dashboard Configuration

### Deployment Settings
- **Branch**: Connect to your preferred branch (e.g., `main` or `master`)
- **Production Branch**: Set the branch that triggers production deployments
- **Deploy Hooks**: Optional webhooks for manual deployments

### Function Settings
The API runs as a serverless function with:
- **Memory**: 2048 MB (configured in vercel.json)
- **Max Duration**: 60 seconds (Pro plan) or 10 seconds (Hobby plan)
- **Region**: Auto-selected based on traffic

## Integration with Main API

The poker-coaches API (Poker-Coach-Grind) can work alongside the main poker-therapist API:

1. **Separate Deployments**: Each API has its own URL and deployment
2. **Independent Scaling**: Each scales based on its own traffic
3. **Cross-Origin Requests**: Configure CORS to allow requests between APIs
4. **Shared Database**: Can share database if needed via environment variables

### CORS Configuration

To allow the main poker-therapist frontend to access poker-coaches API:

1. Set `ALLOWED_ORIGINS` environment variable in poker-coaches project
2. Include poker-therapist domains:
   ```
   https://poker-therapist.vercel.app,https://your-domain.com
   ```

## Monitoring and Logs

### View Logs
1. Go to Vercel dashboard
2. Select `poker-coaches` project
3. Navigate to "Logs" tab
4. View real-time function logs

### Monitor Performance
- **Invocations**: Number of API calls
- **Response Time**: Average response time
- **Error Rate**: Percentage of failed requests
- **Bandwidth**: Data transferred

## Troubleshooting

### Build Fails
**Problem**: Deployment fails during build
**Solution**:
1. Check that `Poker-Coach-Grind/requirements.txt` has all dependencies
2. Verify Python version compatibility (3.12+)
3. Check build logs in Vercel dashboard

### Import Errors
**Problem**: Module import fails
**Solution**:
1. Verify root directory is set to `Poker-Coach-Grind`
2. Check that `api/index.py` correctly imports from `.main`
3. Ensure all `__init__.py` files are present

### Database Connection Errors
**Problem**: Cannot connect to database
**Solution**:
1. Verify `DATABASE_URL` environment variable
2. Check database allows connections from Vercel IPs
3. Use aiosqlite for local SQLite if no external database

### CORS Errors
**Problem**: Frontend cannot access API
**Solution**:
1. Add frontend URL to `ALLOWED_ORIGINS` environment variable
2. Verify CORS middleware in `Poker-Coach-Grind/api/main.py`
3. Check that requests include proper headers

## Updates and Redeployment

Vercel automatically redeploys when you push to the connected branch:

1. Make changes to files in `Poker-Coach-Grind/`
2. Commit and push to GitHub
3. Vercel detects changes and triggers deployment
4. New version goes live automatically

## Testing Deployment

After deployment, test the API:

```bash
# Health check
curl https://poker-coaches.vercel.app/health

# API info
curl https://poker-coaches.vercel.app/

# View interactive docs
open https://poker-coaches.vercel.app/docs
```

## Related Documentation

- Main API Deployment: See `VERCEL_DEPLOYMENT.md` in repository root
- Integration Guide: See `Poker-Coach-Grind/INTEGRATION_GUIDE.md`
- API Documentation: See `Poker-Coach-Grind/README.md`

## Support

For deployment issues:
- Check [Vercel Status](https://www.vercel-status.com/)
- Visit [Vercel Documentation](https://vercel.com/docs)
- Review [Vercel Community](https://github.com/vercel/vercel/discussions)

For application issues:
- Check the main repository README
- Review Poker-Coach-Grind documentation
- Open an issue on GitHub
