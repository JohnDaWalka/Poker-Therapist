# Versace Gateway Deployment Guide

This document explains the Vercel deployment configuration for exposing both the Therapy Rex API and Poker-Coach-Grind API (Versace Poker coaches) through a unified gateway.

## Architecture Overview

The repository deploys **two separate FastAPI applications** to Vercel:

1. **Therapy Rex API** (`backend/api/main.py`) - Mental game coaching system
2. **Poker-Coach-Grind API** (`Poker-Coach-Grind/api/main.py`) - Bankroll tracker and hand history reviewer (Versace)

## Routing Configuration

The `vercel.json` file configures routes with proper precedence (more specific first):

```json
{
  "routes": [
    { "src": "/api/coaches/(.*)", "dest": "/api/coaches.py" },  // Specific - Versace
    { "src": "/coaches/(.*)", "dest": "/api/coaches.py" },       // Specific - Versace  
    { "src": "/api/(.*)", "dest": "/api/index.py" },            // General - Therapy Rex
    { "src": "/(.*)", "dest": "/api/index.py" }                 // Fallback - Therapy Rex
  ]
}
```

### API Endpoints

**Versace Poker Coaches API** - Access via `/api/coaches/*` or `/coaches/*`:
- `/api/coaches/` - Root endpoint
- `/api/coaches/health` - Health check
- `/api/coaches/api/bankroll/*` - Bankroll tracking
- `/api/coaches/api/hands/*` - Hand history review
- `/api/coaches/api/crypto/*` - Cryptocurrency integration
- `/api/coaches/api/n8n/*` - n8n workflow integration

**Therapy Rex API** - Access via `/api/*`:
- `/api/auth/*` - Authentication
- `/api/triage/*` - Initial assessment
- `/api/deep-session/*` - Deep coaching sessions
- `/api/analyze/*` - Session analysis
- `/api/tracking/*` - Progress tracking
- `/api/coinpoker/*` - CoinPoker integration
- `/api/n8n/*` - n8n webhooks

## Serverless Function Handlers

### `/api/index.py`
- **Purpose**: Entry point for Therapy Rex API
- **Import**: `from backend.api.main import app`
- **Memory**: 2048 MB
- **Timeout**: 60 seconds

### `/api/coaches.py`
- **Purpose**: Entry point for Poker-Coach-Grind API (Versace)
- **Import**: `from Poker_Coach_Grind.api.main import app`
- **Memory**: 2048 MB
- **Timeout**: 60 seconds

## Python Package Symlink

The `Poker-Coach-Grind` directory name contains hyphens, which are not valid in Python package names. To enable proper imports:

**Symlink**: `Poker_Coach_Grind` → `Poker-Coach-Grind`

This symlink:
- Is tracked in Git and deployed to Vercel
- Enables `from Poker_Coach_Grind.api.main import app` imports
- Allows Python's relative import system to work correctly

### Verifying the Symlink

```bash
# Check symlink exists
ls -la | grep Poker_Coach_Grind

# Expected output:
# lrwxrwxrwx 1 user user 17 Jan 25 06:09 Poker_Coach_Grind -> Poker-Coach-Grind
```

## Dependencies

All dependencies for both APIs are consolidated in the root `requirements.txt`:
- FastAPI, Uvicorn, Pydantic (both APIs)
- SQLAlchemy, aiosqlite (both APIs)
- OpenAI, Anthropic, Google Gemini (Therapy Rex)
- HTTPX (Poker-Coach-Grind crypto APIs)

## Environment Variables

Set these in Vercel dashboard under Project Settings → Environment Variables:

### Therapy Rex API
- `OPENAI_API_KEY` - OpenAI API access
- `ANTHROPIC_API_KEY` - Claude API access
- `GOOGLE_API_KEY` - Gemini API access
- `XAI_API_KEY` - Grok API access
- Other authentication and service credentials

### Poker-Coach-Grind API
- `ENVIRONMENT` - Set to "production"
- `ALLOWED_ORIGINS` - Comma-separated list of allowed origins for CORS
- Database and crypto API credentials as needed

## Deployment Checklist

- [x] Symlink `Poker_Coach_Grind` exists and is committed to Git
- [x] `vercel.json` has routes in correct precedence order
- [x] Both serverless handlers (`api/index.py`, `api/coaches.py`) exist
- [x] All dependencies are in root `requirements.txt`
- [ ] Environment variables configured in Vercel dashboard
- [ ] Test deployment by accessing both API endpoints
- [ ] Verify API documentation at `/docs` and `/api/coaches/docs`

## Testing After Deployment

```bash
# Test Therapy Rex API
curl https://your-domain.vercel.app/api/health

# Test Versace Poker Coaches API
curl https://your-domain.vercel.app/api/coaches/health

# View Therapy Rex API docs
open https://your-domain.vercel.app/docs

# View Versace Poker Coaches API docs
open https://your-domain.vercel.app/api/coaches/docs
```

## Troubleshooting

### Import Errors
- Verify `Poker_Coach_Grind` symlink exists in deployed code
- Check Vercel build logs for symlink warnings
- Ensure symlink is not in `.vercelignore`

### Route Conflicts
- Verify routes in `vercel.json` are in correct order (specific before general)
- Check Vercel function logs to see which handler received the request

### Missing Dependencies
- All dependencies must be in root `requirements.txt`
- Vercel installs from root directory, not subdirectories

## Related Documentation
- [Vercel Deployment](VERCEL_DEPLOYMENT.md)
- [Poker-Coach-Grind Integration](Poker-Coach-Grind/INTEGRATION_GUIDE.md)
- [Backend API](backend/README.md)
