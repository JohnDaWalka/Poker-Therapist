# Vercel Poker-Coaches Connection Fix - Summary

## Problem Statement

The Vercel deployment for the "poker-coaches" project was failing with errors. The poker-coaches project is a separate Vercel deployment that exposes the Poker-Coach-Grind API.

## Root Cause

The Poker-Coach-Grind directory lacked the necessary Vercel configuration files to be deployed as a standalone Vercel project. While the main repository had a vercel.json for the poker-therapist API, the poker-coaches project (which uses Poker-Coach-Grind as its root directory) needed its own configuration.

## Solution

Added complete Vercel deployment configuration to the Poker-Coach-Grind directory, enabling it to be deployed as a separate Vercel project called "poker-coaches".

### Files Created

1. **Poker-Coach-Grind/vercel.json**
   - Configures routing for the poker-coaches project
   - Sets function memory to 2048MB and timeout to 60s
   - Routes all traffic through api/index.py

2. **Poker-Coach-Grind/api/index.py**
   - Entry point for Vercel's Python runtime
   - Imports and exports the FastAPI app from main.py
   - Provides compatibility with Vercel's serverless function expectations

3. **Poker-Coach-Grind/.vercelignore**
   - Excludes unnecessary files from deployment (CLI, UI, tests, docs)
   - Reduces deployment size and improves build speed
   - Keeps only essential API components

4. **Poker-Coach-Grind/VERCEL_DEPLOYMENT.md**
   - Comprehensive deployment guide
   - Step-by-step setup instructions
   - Environment variable configuration
   - Troubleshooting tips

## Vercel Configuration Required

To deploy the poker-coaches project in Vercel:

1. **Create New Project** (or reconfigure existing)
   - Project Name: `poker-coaches`
   - Repository: `JohnDaWalka/Poker-Therapist`
   - **Root Directory: `Poker-Coach-Grind`** ← This is crucial!

2. **Environment Variables** (in Vercel dashboard)
   - `ENVIRONMENT=production`
   - `ALLOWED_ORIGINS` (optional): Comma-separated list of allowed CORS origins
   - `COINGECKO_API_KEY` (optional): For crypto price tracking
   - `N8N_WEBHOOK_URL` (optional): For n8n integration

3. **Deploy**
   - Vercel will automatically detect the configuration
   - Build from requirements.txt in Poker-Coach-Grind/
   - Deploy the FastAPI app

## Architecture

### Two Separate Vercel Projects

**poker-therapist** (Main API)
- Root Directory: `/` (repository root)
- Entry Point: `api/index.py`
- Routes: Main therapy and coaching API
- URL: `https://poker-therapist.vercel.app`

**poker-coaches** (Grind API)
- Root Directory: `Poker-Coach-Grind`
- Entry Point: `api/index.py` (in Poker-Coach-Grind/)
- Routes: Bankroll, hand history, crypto, n8n integration
- URL: `https://poker-coaches.vercel.app`

### Benefits of Separate Projects

1. **Independent Scaling**: Each API scales based on its own traffic
2. **Isolated Deployments**: Changes to one don't affect the other
3. **Separate Monitoring**: Each has its own logs and metrics
4. **Resource Allocation**: Different memory/timeout settings
5. **Environment Isolation**: Different environment variables

## API Endpoints

After deployment, the poker-coaches API will expose:

```
https://poker-coaches.vercel.app/
├── /                          # API info
├── /health                    # Health check
├── /docs                      # Interactive API documentation
├── /api/bankroll/*            # Bankroll tracking endpoints
├── /api/hands/*               # Hand history endpoints
├── /api/crypto/*              # Cryptocurrency integration
└── /api/n8n/*                 # n8n workflow integration
```

## Deployment Verification

To verify the deployment works:

```bash
# Health check
curl https://poker-coaches.vercel.app/health
# Expected: {"status": "healthy"}

# API info
curl https://poker-coaches.vercel.app/
# Expected: JSON with API name, version, and endpoints

# Interactive docs
# Visit: https://poker-coaches.vercel.app/docs
```

## Integration with Main API

The poker-coaches API can work alongside the poker-therapist API:

1. **CORS Configuration**: Set `ALLOWED_ORIGINS` to include poker-therapist domain
2. **Cross-API Calls**: Frontend can call both APIs independently
3. **Shared Resources**: Can share database via environment variables if needed

## Troubleshooting

### If Build Still Fails

1. **Verify Root Directory**: Must be set to `Poker-Coach-Grind` in Vercel project settings
2. **Check Dependencies**: Ensure `Poker-Coach-Grind/requirements.txt` has all needed packages
3. **Review Logs**: Check Vercel build logs for specific errors
4. **Import Errors**: Verify all `__init__.py` files are present in subdirectories

### Common Issues

**Issue**: "Module not found" errors
**Solution**: 
- Check that root directory is `Poker-Coach-Grind`
- Verify Python path resolution in api/index.py

**Issue**: Routes not working
**Solution**:
- Verify vercel.json routes configuration
- Check that all routes point to /api/index.py

**Issue**: Function timeout
**Solution**:
- Increase maxDuration in vercel.json (Pro plan supports up to 60s)
- Optimize slow API endpoints

## Security Notes

✅ **CodeQL Scan**: 0 alerts found
✅ **No Secrets**: All sensitive data uses environment variables
✅ **CORS Protection**: Properly configured allowed origins
✅ **Dependencies**: Using well-maintained open-source packages

## Next Steps

After merging this PR:

1. **Configure Vercel Project**:
   - Go to Vercel dashboard
   - Create or reconfigure poker-coaches project
   - Set root directory to `Poker-Coach-Grind`
   - Add environment variables

2. **Trigger Deployment**:
   - Push to the configured branch
   - Vercel will auto-deploy

3. **Verify Deployment**:
   - Check health endpoint
   - View interactive docs
   - Test API endpoints

4. **Monitor**:
   - Watch Vercel logs for any issues
   - Monitor function invocations
   - Track error rates

## References

- Vercel Documentation: https://vercel.com/docs
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/
- Poker-Coach-Grind Deployment Guide: `Poker-Coach-Grind/VERCEL_DEPLOYMENT.md`
- Main API Deployment: `VERCEL_DEPLOYMENT.md`

## Support

For issues with this fix:
- Review `Poker-Coach-Grind/VERCEL_DEPLOYMENT.md`
- Check Vercel build logs
- Verify root directory setting
- Open GitHub issue with deployment logs
