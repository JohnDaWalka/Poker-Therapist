# Vercel Deployment Fix – Poker Coach Grind

## Background

The `Poker-Coach-Grind` directory was originally committed with title-case naming.
The user renamed it to all-lowercase (`poker-coach-grind`) to fix a Vercel
deployment failure caused by case-sensitivity on Linux-based build runners.

A previous documentation-only commit (`dd16d4c`) described the intended fix but
never actually added the required Vercel configuration files.  This PR adds the
missing files.

---

## Files added

| File | Purpose |
|---|---|
| `poker-coach-grind/vercel.json` | Routes all requests to the serverless function |
| `poker-coach-grind/api/index.py` | Vercel ASGI entrypoint – imports `app` from `api/main.py` |
| `poker-coach-grind/.vercelignore` | Excludes unneeded files (UI, CLI, docs) from the deploy bundle |
| `poker-coach-grind/requirements.txt` | Python dependencies installed by Vercel at build time |

---

## Vercel project settings (poker-coach-grind)

| Setting | Value |
|---|---|
| **Framework Preset** | Other |
| **Root Directory** | `poker-coach-grind` |
| **Build Command** | *(leave empty)* |
| **Output Directory** | *(leave empty)* |
| **Install Command** | `pip install -r requirements.txt` |

> **Important**: set Root Directory to `poker-coach-grind` (all-lowercase).
> The previous value `Poker-Coach-Grind` will fail on Vercel's case-sensitive
> Linux build runners.

---

## Environment variables

Configure the following in **Vercel → Project → Settings → Environment Variables**:

| Variable | Description | Example |
|---|---|---|
| `GRIND_DATABASE_URL` | SQLite async URL (defaults to `/tmp/`) | `sqlite+aiosqlite:////tmp/poker_grind.db` |
| `ETHEREUM_RPC_URL` | Ethereum JSON-RPC endpoint | `https://eth.llamarpc.com` |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins | `https://your-frontend.vercel.app` |
| `ENVIRONMENT` | Set to `production` for strict CORS | `production` |

> **Note**: Do not commit `.env` files.  Set secrets in the Vercel dashboard.

---

## How the import fix works

`api/main.py` uses Python **relative imports** (`from ..database.session import …`).
Vercel executes `api/index.py` directly as a serverless function, so there is no
parent package in the normal sense.

`api/index.py` works around this by registering synthetic package modules in
`sys.modules` before importing `api.main`.  This lets the relative imports
resolve correctly without modifying the existing source files.

---

## Endpoints

| Path | Description |
|---|---|
| `GET /` | Root – returns API name and available endpoints |
| `GET /health` | Health check – returns `{"status": "healthy"}` |
| `GET /docs` | Interactive Swagger UI |
| `GET /openapi.json` | OpenAPI schema |
| `GET/POST /api/bankroll/*` | Bankroll tracking |
| `GET/POST /api/hands/*` | Hand history review |
| `GET/POST /api/crypto/*` | Cryptocurrency portfolio |
| `GET/POST /api/n8n/*` | n8n workflow integration |

---

## Root project (poker-therapist)

The root Vercel project (`poker-therapist`) is **not affected** by these changes.
Its Root Directory remains `/` and its configuration lives in the repo root
`vercel.json` and `api/index.py`.
