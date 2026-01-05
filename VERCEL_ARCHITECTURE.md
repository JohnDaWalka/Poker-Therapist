# Vercel Deployment Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│              JohnDaWalka/Poker-Therapist                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Git Push
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    Vercel Platform                          │
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │           Build Process                            │    │
│  │                                                    │    │
│  │  1. Read vercel.json configuration                │    │
│  │  2. Install dependencies from requirements.txt    │    │
│  │  3. Build Python serverless function              │    │
│  │  4. Deploy to edge network                        │    │
│  └───────────────────────────────────────────────────┘    │
│                         │                                   │
│                         ↓                                   │
│  ┌───────────────────────────────────────────────────┐    │
│  │        Serverless Functions (Edge Network)        │    │
│  │                                                    │    │
│  │  Entry Point: api/index.py                        │    │
│  │  Handler: FastAPI app (backend/api/main.py)       │    │
│  │                                                    │    │
│  │  Environment Variables:                           │    │
│  │  • XAI_API_KEY                                    │    │
│  │  • OPENAI_API_KEY                                 │    │
│  │  • ANTHROPIC_API_KEY                              │    │
│  │  • GOOGLE_API_KEY                                 │    │
│  │  • AUTHORIZED_EMAILS                              │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTPS Requests
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                     API Endpoints                           │
│                                                             │
│  • GET  /              → Root (API info)                   │
│  • GET  /health        → Health check                      │
│  • GET  /docs          → Interactive API docs              │
│  • POST /api/triage    → Triage analysis                   │
│  • POST /api/deep-session → Deep session coaching          │
│  • POST /api/analyze   → Hand analysis                     │
│  • GET  /api/tracking  → Session tracking                  │
│                                                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ CORS Enabled
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   Client Applications                       │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Vue.js    │  │  Streamlit   │  │    Mobile    │     │
│  │  Frontend   │  │   Chatbot    │  │     Apps     │     │
│  └─────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Request Flow

```
User Request
    ↓
Vercel Edge Network (Auto-selected region)
    ↓
Serverless Function (api/index.py)
    ↓
FastAPI Application (backend/api/main.py)
    ↓
Route Handler (backend/api/routes/*)
    ↓
AI Service Integration (xAI, OpenAI, etc.)
    ↓
Response (JSON)
    ↓
Client Application
```

## File Structure

```
Poker-Therapist/
├── api/
│   └── index.py                    # Vercel serverless function entry
├── backend/
│   └── api/
│       ├── main.py                 # FastAPI app (updated CORS)
│       ├── models.py
│       └── routes/
│           ├── analyze.py
│           ├── deep_session.py
│           ├── tracking.py
│           └── triage.py
├── vercel.json                     # Vercel configuration
├── .vercelignore                   # Deployment exclusions
├── requirements.txt                # Python dependencies (merged)
├── VERCEL_DEPLOYMENT.md            # Deployment guide
├── VERCEL_INTEGRATION_CHECKLIST.md # Verification checklist
└── VERCEL_INTEGRATION_SUMMARY.md   # Implementation summary
```

## Configuration Flow

```
vercel.json
    ├── builds → Defines Python serverless function
    │   └── src: api/index.py
    │   └── use: @vercel/python
    │
    ├── routes → URL routing configuration
    │   └── /api/* → api/index.py
    │   └── /*     → api/index.py
    │
    └── env → Environment variable references
        ├── XAI_API_KEY
        ├── OPENAI_API_KEY
        ├── ANTHROPIC_API_KEY
        ├── GOOGLE_API_KEY
        └── AUTHORIZED_EMAILS
```

## Environment Variables Configuration

```
Vercel Dashboard → Settings → Environment Variables
    ↓
Add variables with @ prefix references in vercel.json
    ↓
Variables injected at runtime into serverless functions
    ↓
Accessed via os.environ in Python code
```

## CORS Configuration

```
backend/api/main.py → CORSMiddleware

Allowed Origins:
    • http://localhost:3000        (Local dev)
    • http://localhost:8080        (Local dev)
    • http://localhost:5173        (Local dev)
    • https://*.vercel.app         (Preview deployments)
    • https://poker-therapist.vercel.app (Production)

Methods: ALL
Headers: ALL
Credentials: Enabled
```

## Deployment Process

```
Developer
    ↓ git push
GitHub Repository
    ↓ webhook
Vercel Platform
    ↓
1. Clone repository
    ↓
2. Read vercel.json
    ↓
3. Install requirements.txt
    ↓
4. Build serverless function
    ↓
5. Deploy to edge network
    ↓
6. Health check
    ↓
7. Go live!
    ↓
Production URL: https://poker-therapist.vercel.app
```

## Monitoring Flow

```
Production Deployment
    ↓
Vercel Dashboard → Logs
    ├── Real-time function logs
    ├── Error tracking
    ├── Performance metrics
    └── Invocation counts
    ↓
Alerts & Notifications (optional)
```

## Scalability

```
User Request
    ↓
Vercel Edge Network (Automatic)
    ├── Cold Start: ~1-2s (first request)
    ├── Warm Function: ~50-200ms
    └── Auto-scaling: Based on traffic
    ↓
Multiple Instances (Automatic)
    ├── High Traffic: More instances
    └── Low Traffic: Fewer instances
```

## Data Flow for AI Coaching

```
Client (User)
    ↓ HTTPS POST /api/triage
Vercel Serverless Function
    ↓
FastAPI App → Triage Route
    ↓
AI Service (xAI, OpenAI, etc.)
    ↓ API Request
External AI API
    ↓ AI Response
FastAPI App
    ↓ JSON Response
Client (User)
```

## Security Layers

```
1. GitHub → Vercel Integration (OAuth)
2. Environment Variables (Encrypted at rest)
3. HTTPS Only (TLS 1.3)
4. CORS Protection (Allowed origins)
5. API Key Authentication (Environment variables)
6. No secrets in code (Verified by CodeQL)
```

## Best Practices Implemented

✅ **Serverless Architecture**: Automatic scaling, pay-per-use
✅ **Edge Network**: Global distribution for low latency
✅ **Environment Variables**: Secure secret management
✅ **CORS Configuration**: Secure cross-origin requests
✅ **Health Checks**: Monitoring and alerting
✅ **Documentation**: Comprehensive deployment guides
✅ **Version Control**: Git-based deployments
✅ **Zero Downtime**: Atomic deployments

---

**Architecture Type**: Serverless  
**Platform**: Vercel  
**Runtime**: Python  
**Framework**: FastAPI  
**Deployment**: Git-based (automatic)  
**Scaling**: Automatic  
**Region**: Auto-selected (global)
