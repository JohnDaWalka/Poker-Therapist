# Therapy Rex API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### POST /api/triage
Quick tilt intervention (5-10 minutes)

### POST /api/deep-session
Deep therapy session (45-90 minutes)

### POST /api/analyze/hand
Analyze poker hand with GTO and meta context

### POST /api/analyze/voice
Transcribe and analyze voice recording

### POST /api/analyze/video
Analyze session video for body language

### GET /api/profile/{user_id}
Get user tilt profile

### GET /api/playbook/{user_id}
Get user mental game playbook

See full documentation at `/docs` endpoint when server is running.
