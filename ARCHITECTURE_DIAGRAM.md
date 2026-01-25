# Vercel Deployment Architecture - Two Projects

┌─────────────────────────────────────────────────────────────────────┐
│                      GitHub Repository                               │
│                  JohnDaWalka/Poker-Therapist                        │
│                                                                      │
│  ┌────────────────────┐         ┌─────────────────────────────┐   │
│  │  Root Directory    │         │  Poker-Coach-Grind/         │   │
│  │  ├── api/          │         │  ├── api/                   │   │
│  │  │   └── index.py  │         │  │   ├── index.py ← NEW    │   │
│  │  │   └── grind.py  │         │  │   ├── main.py           │   │
│  │  ├── backend/      │         │  │   ├── bankroll.py       │   │
│  │  ├── vercel.json   │         │  │   └── ...               │   │
│  │  └── ...           │         │  ├── vercel.json ← NEW     │   │
│  │                    │         │  ├── .vercelignore ← NEW   │   │
│  │                    │         │  ├── requirements.txt       │   │
│  └────────────────────┘         │  └── ...                    │   │
│                                  └─────────────────────────────┘   │
└──────────────┬──────────────────────────────┬──────────────────────┘
               │                              │
               │ Webhook                      │ Webhook
               ↓                              ↓
┌──────────────────────────────┐   ┌──────────────────────────────┐
│    Vercel Project 1          │   │    Vercel Project 2          │
│    poker-therapist           │   │    poker-coaches             │
│                              │   │                              │
│ Root Dir: /                  │   │ Root Dir: Poker-Coach-Grind  │
│ Entry: api/index.py          │   │ Entry: api/index.py          │
│                              │   │                              │
│ Routes:                      │   │ Routes:                      │
│ • /api/*  → api/index.py    │   │ • /api/*  → api/index.py    │
│ • /grind/* → api/grind.py   │   │ • /*      → api/index.py    │
│ • /*      → api/index.py    │   │                              │
└──────────────┬───────────────┘   └──────────────┬───────────────┘
               │                                   │
               ↓                                   ↓
┌──────────────────────────────┐   ┌──────────────────────────────┐
│  poker-therapist.vercel.app  │   │  poker-coaches.vercel.app    │
│                              │   │                              │
│ • /api/triage               │   │ • /api/bankroll              │
│ • /api/deep-session         │   │ • /api/hands                 │
│ • /api/analyze              │   │ • /api/crypto                │
│ • /api/tracking             │   │ • /api/n8n                   │
│ • /grind/* (proxies to →)   │   │ • /health                    │
│                              │   │ • /docs                      │
└──────────────────────────────┘   └──────────────────────────────┘

Key Points:
═══════════
1. TWO SEPARATE VERCEL PROJECTS from the SAME REPOSITORY
2. Different Root Directories → Independent deployments
3. Each has its own vercel.json configuration
4. Both deploy on git push (separate webhooks)
5. No conflicts - completely isolated

Configuration Required:
══════════════════════
poker-coaches project in Vercel Dashboard:
  ✓ Root Directory: Poker-Coach-Grind  ← CRITICAL!
  ✓ Auto-deploy: Enabled
  ✓ Branch: main (or your default)

Files This PR Added:
═══════════════════
• Poker-Coach-Grind/vercel.json        ← Configuration
• Poker-Coach-Grind/api/index.py       ← Entry point
• Poker-Coach-Grind/.vercelignore      ← Exclusions
• Poker-Coach-Grind/VERCEL_DEPLOYMENT.md ← Full guide
• POKER_COACHES_FIX_SUMMARY.md         ← Summary
• NEXT_STEPS.md                        ← Action items

Deployment Flow:
═══════════════
1. Developer pushes to GitHub
2. Vercel webhook triggers both projects
3. Each builds independently with its own root directory
4. Both deploy to separate URLs
5. Both accessible and independent

Result:
══════
✓ poker-therapist API: Main therapy/coaching API
✓ poker-coaches API: Bankroll/hands/crypto API
✓ No interference between projects
✓ Independent scaling and monitoring
✓ Both maintained from single repository
