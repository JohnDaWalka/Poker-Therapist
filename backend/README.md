# Therapy Rex Backend API

FastAPI backend for Therapy Rex poker mental game coaching system.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and configure your API keys **and PostgreSQL settings** (PokerTracker uses PostgreSQL on port `5432`):
```bash
cp .env.example .env
# Edit .env with your actual API keys
# For database, defaults:
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=postgres
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DB=pokertracker
# Or set DATABASE_URL directly (postgresql+asyncpg://user:pass@host:5432/db)
```

3. Start the server:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /api/triage` - Quick tilt intervention (5-10 min)
- `POST /api/deep-session` - Deep therapy session (45-90 min)
- `POST /api/analyze/hand` - Hand history analysis
- `POST /api/analyze/voice` - Voice rant analysis
- `POST /api/analyze/video` - Session video analysis
- `GET /api/profile/{user_id}` - Get user tilt profile
- `GET /api/playbook/{user_id}` - Get personalized playbook

## AI Model Routing

- **Grok**: Quick triage and containment
- **Perplexity**: Research and hand history analysis
- **Claude**: Deep therapy and cognitive reframing
- **OpenAI**: GTO analysis and strategy
- **Gemini**: Multimodal (voice/video/image) processing

## Testing

```bash
# Test the API
curl http://localhost:8000/docs
```

## Architecture

```
backend/
├── api/           # FastAPI routes and middleware
├── agent/         # Therapy Rex agent logic
├── models/        # AI API clients
└── requirements.txt
```
