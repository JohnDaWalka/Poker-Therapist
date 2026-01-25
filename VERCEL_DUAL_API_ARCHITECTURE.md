# Vercel Dual API Architecture

## Overview

The Poker Therapist application now exposes **two separate FastAPI applications** through Vercel serverless functions:

1. **Main Therapy Rex API** - Primary poker coaching and mental game features
2. **Poker-Coach-Grind API** - Bankroll tracking, hand history, and cryptocurrency integration

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Vercel Edge Network                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴──────────────┐
        │                            │
        ▼                            ▼
┌──────────────────┐      ┌──────────────────┐
│  api/index.py    │      │  api/grind.py    │
│  (Main API)      │      │  (Grind API)     │
└────────┬─────────┘      └────────┬─────────┘
         │                         │
         ▼                         ▼
┌──────────────────┐      ┌──────────────────┐
│ backend/api/     │      │ Poker-Coach-     │
│ main.py          │      │ Grind/api/       │
│                  │      │ main.py          │
└──────────────────┘      └──────────────────┘
```

## URL Routing

### Main API Routes (`api/index.py`)

**Base URL**: `https://poker-therapist.vercel.app`

- `/` - Root endpoint (API info)
- `/health` - Health check
- `/docs` - Interactive API documentation
- `/api/auth/*` - Authentication endpoints
- `/api/triage` - Triage analysis
- `/api/deep-session` - Deep session coaching
- `/api/analyze/*` - Hand/voice/video analysis
- `/api/tracking/*` - Session tracking and profiles
- `/api/coinpoker/*` - CoinPoker integration
- `/api/n8n` - n8n webhook endpoints

### Grind API Routes (`api/grind.py`)

**Base URL**: `https://poker-therapist.vercel.app/grind`

- `/grind/` - Root endpoint (Grind API info)
- `/grind/health` - Health check
- `/grind/docs` - Interactive API documentation
- `/grind/api/bankroll/*` - Bankroll management
  - `GET /grind/api/bankroll/{user_id}` - Get user bankroll
  - `POST /grind/api/bankroll/transaction` - Create transaction
  - `GET /grind/api/bankroll/history/{user_id}` - Transaction history
  - `GET /grind/api/bankroll/stats/{user_id}` - Bankroll statistics
- `/grind/api/hands/*` - Hand history management
  - `POST /grind/api/hands/import` - Import hand histories
  - `POST /grind/api/hands/query` - Query hands
  - `GET /grind/api/hands/{hand_id}` - Get specific hand
  - `GET /grind/api/hands/session/{session_id}` - Get session hands
  - `GET /grind/api/hands/user/{user_id}/recent` - Get recent hands
- `/grind/api/crypto/*` - Cryptocurrency integration
  - `GET /grind/api/crypto/prices` - Get crypto prices
  - `POST /grind/api/crypto/wallet/add` - Add wallet
  - `GET /grind/api/crypto/portfolio` - Get portfolio
  - `GET /grind/api/crypto/wallet/{user_id}/{blockchain}/{address}` - Get wallet info
  - `GET /grind/api/crypto/supported-tokens` - List supported tokens
- `/grind/api/n8n/*` - n8n webhook endpoints
  - `POST /grind/api/n8n/webhook/bankroll-transaction`
  - `POST /grind/api/n8n/webhook/hand-import`
  - `POST /grind/api/n8n/webhook/crypto-alert`
  - `POST /grind/api/n8n/webhook/therapy-session`

## Configuration

### vercel.json

```json
{
  "version": 2,
  "name": "poker-therapist",
  "routes": [
    {
      "src": "/grind/(.*)",
      "dest": "/api/grind.py"
    },
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ],
  "functions": {
    "api/index.py": {
      "memory": 2048,
      "maxDuration": 60
    },
    "api/grind.py": {
      "memory": 2048,
      "maxDuration": 60
    }
  }
}
```

### Route Priority

Routes are matched in order:
1. `/grind/*` → Poker-Coach-Grind API
2. `/api/*` → Main Therapy Rex API
3. `/*` → Main Therapy Rex API (default)

## Serverless Function Handlers

### api/index.py (Main API)

```python
from backend.api.main import app

handler = app
__all__ = ["app", "handler"]
```

### api/grind.py (Grind API)

```python
import sys
from pathlib import Path
import importlib

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

grind_api = importlib.import_module('Poker-Coach-Grind.api.main')
app = grind_api.app

handler = app
__all__ = ["app", "handler"]
```

## Dependencies

Both APIs share the same `requirements.txt` which includes all necessary dependencies:

- **FastAPI & Server**: `fastapi`, `uvicorn`, `pydantic`
- **Database**: `sqlalchemy`, `aiosqlite`
- **AI Providers**: `openai`, `anthropic`, `google-generativeai`
- **HTTP Client**: `httpx`, `requests`
- **Authentication**: `python-jose`, `passlib`
- **And more...**

## Testing

### Local Testing

```bash
# Test Main API
uvicorn backend.api.main:app --reload --port 8000

# Test Grind API
cd Poker-Coach-Grind
uvicorn api.main:app --reload --port 8001
```

### Production Testing

```bash
# Main API
curl https://poker-therapist.vercel.app/health
curl https://poker-therapist.vercel.app/docs

# Grind API
curl https://poker-therapist.vercel.app/grind/health
curl https://poker-therapist.vercel.app/grind/docs
```

## Benefits

✅ **Separation of Concerns**: Each API has its own domain and responsibilities  
✅ **Independent Scaling**: Vercel can scale each function independently  
✅ **Clear URL Structure**: `/grind/*` vs `/api/*` makes it obvious which API you're using  
✅ **Shared Dependencies**: Single `requirements.txt` for easier maintenance  
✅ **Unified Deployment**: Both APIs deploy together from the same repository

## Future Considerations

- **API Versioning**: Could add `/v1/`, `/v2/` prefixes
- **Rate Limiting**: May need separate limits per API
- **Monitoring**: Track metrics separately for each API
- **CORS**: May need different CORS settings per API
- **Authentication**: Consider if both APIs need the same auth or different auth

---

**Last Updated**: 2026-01-25  
**Vercel Runtime**: Python 3.12  
**Framework**: FastAPI 0.104.0+
