# PokerTracker 4 Integration for Poker Therapist

This guide explains how to integrate Poker Therapist with PokerTracker 4 on Windows to enable real-time hand history tracking and analysis.

## Requirements

- PokerTracker 4 installed on Windows
- PostgreSQL database (included with PT4)
- Python 3.8+ with Poker Therapist installed
- `psycopg2-binary` Python package

## Installation

### 1. Install PostgreSQL Driver

```bash
pip install psycopg2-binary
```

### 2. Configure PT4 Database Connection

Create or update `.env` file in the backend directory:

```env
# PokerTracker 4 Database Configuration
PT4_DB_HOST=localhost
PT4_DB_PORT=5432
PT4_DB_NAME=PT4 DB
PT4_DB_USER=postgres
PT4_DB_PASSWORD=your_password_here
```

**Note**: The password was set when you installed PokerTracker 4. If you don't remember it, you can find or reset it through PT4's database management settings.

### 3. Find Your PT4 Database Name

1. Open PokerTracker 4
2. Go to `Database` > `Database Management`
3. Note the active database name (usually "PT4 DB" or similar)
4. Update `PT4_DB_NAME` in your `.env` file if different

## Usage

### Testing Connection

Test if Poker Therapist can connect to your PT4 database:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/pt4/test-connection",
    json={}
)

print(response.json())
# Expected: {"connected": true, "message": "Successfully connected...", "sites": [...]}
```

### List Your Player Names

Get all player names in your PT4 database:

```python
response = requests.post(
    "http://localhost:8000/api/pt4/list-players",
    json={}
)

players = response.json()["players"]
print(f"Found {len(players)} players: {players}")
```

### Import Recent Hands

Import your last 100 hands from PT4:

```python
response = requests.post(
    "http://localhost:8000/api/pt4/import-recent",
    json={
        "user_id": "my_user_id",
        "player_name": "YourPokerName",
        "limit": 100,
        "site_filter": "Americas Cardroom"  # Optional
    }
)

result = response.json()
print(f"Session ID: {result['session_id']}")
print(f"Imported: {result['imported_hands']} hands")
```

### Import Complete Session by Time Range

Import all hands from a specific playing session:

```python
from datetime import datetime

response = requests.post(
    "http://localhost:8000/api/pt4/import-session",
    json={
        "user_id": "my_user_id",
        "player_name": "YourPokerName",
        "session_start": "2024-01-10T18:00:00",  # ISO format
        "session_end": "2024-01-10T22:30:00"
    }
)

result = response.json()
print(f"Imported {result['imported_hands']} hands from session")
```

### Get AI Analysis

After importing, request Therapy Rex analysis:

```python
# Using WPN session review endpoint (works with PT4 imported hands too)
response = requests.post(
    "http://localhost:8000/api/wpn/session-review",
    json={
        "user_id": "my_user_id",
        "session_id": "your_session_id_from_import",
        "max_hands": 50
    }
)

analysis = response.json()
print("Strategy Review:", analysis["strategy_review"])
print("Therapy Review:", analysis["therapy_review"])
```

## Windows Client Integration

### Option 1: Python Script

Create `pt4_sync.py` in your Poker Therapist directory:

```python
"""Sync hands from PokerTracker 4 to Poker Therapist."""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

PT4_API_URL = "http://localhost:8000/api/pt4"
USER_ID = os.getenv("POKER_THERAPIST_USER_ID", "default_user")
PLAYER_NAME = os.getenv("PT4_PLAYER_NAME", "")

def sync_recent_hands(limit=50):
    """Sync recent hands from PT4."""
    response = requests.post(
        f"{PT4_API_URL}/import-recent",
        json={
            "user_id": USER_ID,
            "player_name": PLAYER_NAME,
            "limit": limit
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Imported {result['imported_hands']} hands")
        print(f"📊 Session ID: {result['session_id']}")
        return result['session_id']
    else:
        print(f"❌ Error: {response.text}")
        return None

def sync_last_session():
    """Sync hands from last 4 hours."""
    now = datetime.now()
    start = now - timedelta(hours=4)
    
    response = requests.post(
        f"{PT4_API_URL}/import-session",
        json={
            "user_id": USER_ID,
            "player_name": PLAYER_NAME,
            "session_start": start.isoformat(),
            "session_end": now.isoformat()
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Imported session: {result['imported_hands']} hands")
        return result['session_id']
    else:
        print(f"❌ Error: {response.text}")
        return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "session":
        sync_last_session()
    else:
        sync_recent_hands()
```

Run it:
```bash
# Sync recent hands
python pt4_sync.py

# Sync last session
python pt4_sync.py session
```

### Option 2: Scheduled Task

Set up Windows Task Scheduler to auto-sync after playing:

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, repeat every 1 hour
4. Action: Start a program
   - Program: `python`
   - Arguments: `C:\path\to\pt4_sync.py`
5. Save

## HUD Integration

### Custom PT4 HUD Popup

To add a "Therapy Rex" button to your PT4 HUD:

1. **Create Custom Popup** in PT4:
   - Go to `HUD` > `Edit HUD Profiles`
   - Click `Options` > `Popup Manager`
   - Create new popup group named "Therapy Rex"

2. **Add Instructions**:
   - Add text stat showing:
     ```
     🧠 Therapy Rex Integration
     
     To analyze this session:
     1. Note your session start time
     2. Run: python pt4_sync.py session
     3. Visit: http://localhost:8000/docs
     4. Use session review API
     ```

3. **Assign to HUD**:
   - In HUD Editor, click any stat
   - Assign "Therapy Rex" popup to click action
   - Position near your HUD

### Alternative: Browser Shortcut

Create a browser bookmark:
```
http://localhost:8000/docs#/PokerTracker4
```

Click it during or after sessions to access PT4 integration endpoints.

## Troubleshooting

### Connection Failed

**Error**: "Failed to connect to PT4 database"

**Solutions**:
1. Verify PT4 is running
2. Check PostgreSQL service is running:
   - Windows Services > "postgresql-x64-9.x" should be Running
3. Verify password in `.env` file
4. Try connecting with pgAdmin to test credentials

### Player Not Found

**Error**: "No hands found for player"

**Solutions**:
1. Verify player name is exact match (case-sensitive)
2. Check player exists in PT4 database
3. Ensure you've played hands that PT4 has imported

### Import Permission Denied

**Error**: "Permission denied for relation"

**Solutions**:
1. Ensure PT4 user has read access to database
2. Try using the `postgres` superuser
3. Check PT4 database settings allow external connections

### psycopg2 Not Found

**Error**: "psycopg2 is required for PT4 integration"

**Solution**:
```bash
pip install psycopg2-binary
```

## API Reference

### POST `/api/pt4/test-connection`

Test connection to PT4 database.

**Request**:
```json
{
  "pt4_config": {
    "host": "localhost",
    "port": 5432,
    "database": "PT4 DB",
    "user": "postgres",
    "password": "your_password"
  }
}
```

**Response**:
```json
{
  "connected": true,
  "message": "Successfully connected to PokerTracker 4 database!",
  "sites": [
    {"id_site": 1, "site_name": "Americas Cardroom"},
    {"id_site": 2, "site_name": "PokerStars"}
  ]
}
```

### POST `/api/pt4/list-players`

Get all player names in database.

**Response**:
```json
{
  "players": ["YourName", "Villain1", "Villain2"]
}
```

### POST `/api/pt4/import-recent`

Import recent hands.

**Request**:
```json
{
  "user_id": "string",
  "player_name": "string",
  "limit": 100,
  "site_filter": "Americas Cardroom"
}
```

### POST `/api/pt4/import-session`

Import session by time range.

**Request**:
```json
{
  "user_id": "string",
  "player_name": "string",
  "session_start": "2024-01-10T18:00:00",
  "session_end": "2024-01-10T22:00:00"
}
```

## Security Notes

- PT4 database runs locally on your PC
- No hand history data leaves your machine unless you use cloud API features
- Store passwords securely in `.env` file
- Don't commit `.env` to git repositories

## Next Steps

1. ✅ Set up PT4 database connection
2. ✅ Test connection
3. ✅ Import recent hands
4. ✅ Request AI analysis
5. 📊 Review Therapy Rex insights
6. 🎯 Improve your game!

## Support

For issues with PT4 integration:
1. Check [PT4 Documentation](https://www.pokertracker.com/guides)
2. Verify PostgreSQL is running
3. Test with pgAdmin or psql client first
4. Create issue on GitHub with error logs
