# Windows PT4 Integration Tools for JohnDaWalka

This directory contains Windows-specific tools for integrating Poker Therapist with PokerTracker 4.

## User: JohnDaWalka

These tools are preconfigured for user `JohnDaWalka` with player name `jdwalka`.

## Quick Setup

1. **Run Setup Script**
   ```cmd
   windows\setup_pt4.bat
   ```
   This will:
   - Check Python installation
   - Install required packages
   - Create `.env` configuration file
   - Open the config file for you to set your PT4 password

2. **Configure Your Settings**
   
   Edit `backend\.env` and set:
   ```env
   PT4_DB_PASSWORD=your_pt4_password_here
   PT4_PLAYER_NAME=jdwalka
   POKER_THERAPIST_USER_ID=JohnDaWalka
   ```

3. **Test Connection**
   ```cmd
   python windows\pt4_sync.py test
   ```

## Available Tools

### `quick_start.py` - One-Click Sync & Analysis

The fastest way to sync and analyze your poker hands.

**Commands:**
```cmd
# Quick sync recent 100 hands + get AI analysis
python windows\quick_start.py

# Import all hands from today
python windows\quick_start.py today

# List all your sessions
python windows\quick_start.py sessions
```

**What it does:**
1. Connects to your PT4 database
2. Imports recent hands from Americas Cardroom
3. Automatically requests Therapy Rex analysis
4. Shows strategy and mental game insights

### `pt4_sync.py` - Manual Hand Import

More control over what hands to import.

**Commands:**
```cmd
# Test PT4 connection
python windows\pt4_sync.py test

# List all players in PT4
python windows\pt4_sync.py players

# Import recent 50 hands (default)
python windows\pt4_sync.py

# Import specific number of recent hands
python windows\pt4_sync.py recent 200

# Import last 4 hours (default session)
python windows\pt4_sync.py session

# Import last N hours
python windows\pt4_sync.py session 6
```

### `setup_pt4.bat` - Initial Setup

One-time setup script that:
- Checks Python installation
- Installs required packages (`psycopg2-binary`, `python-dotenv`, `requests`)
- Creates configuration files
- Opens config for editing

## Typical Workflow

### After Playing a Session

1. **Quick Analysis** (easiest):
   ```cmd
   python windows\quick_start.py
   ```
   This imports your recent hands and shows AI analysis immediately.

2. **Or Manual Process**:
   ```cmd
   # Step 1: Import hands
   python windows\pt4_sync.py session

   # Step 2: Note the session ID from output
   # Step 3: Get analysis via API or Streamlit
   ```

### Daily Routine

```cmd
# Morning: Review yesterday's sessions
python windows\quick_start.py sessions

# After playing: Quick sync and analysis
python windows\quick_start.py

# End of day: Import full day
python windows\quick_start.py today
```

## Configuration

All configuration is in `backend\.env`:

```env
# Your PT4 Database (usually defaults work)
PT4_DB_HOST=localhost
PT4_DB_PORT=5432
PT4_DB_NAME=PT4 DB
PT4_DB_USER=postgres
PT4_DB_PASSWORD=your_password_here

# Your Identity
POKER_THERAPIST_USER_ID=JohnDaWalka
PT4_PLAYER_NAME=jdwalka

# API Keys (for AI analysis)
XAI_API_KEY=your_grok_api_key
OPENAI_API_KEY=your_openai_key
PERPLEXITY_API_KEY=your_perplexity_key
```

## Troubleshooting

### "Cannot connect to PT4 database"

1. Make sure PokerTracker 4 is running
2. Check Windows Services - PostgreSQL should be running
3. Verify password in `backend\.env`
4. Test with: `python windows\pt4_sync.py test`

### "API server not running"

Start the API server in a separate terminal:
```cmd
python -m backend.api.main
```

Or visit http://localhost:8000/docs to check if it's running.

### "Player not found"

1. Run: `python windows\pt4_sync.py players`
2. Find your exact player name (case-sensitive)
3. Update `PT4_PLAYER_NAME` in `backend\.env`

### "psycopg2 not found"

```cmd
pip install psycopg2-binary
```

## Advanced Usage

### Filter by Specific Site

Edit `quick_start.py` and change:
```python
"site_filter": "Americas Cardroom"  # Your primary site
```

To:
```python
"site_filter": "BetACR"  # or "Black Chip Poker", etc.
```

Or remove the filter entirely to import from all sites.

### Automated Syncing

Set up Windows Task Scheduler to run `quick_start.py` automatically:

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: After you typically finish playing
4. Action: `python C:\path\to\Poker-Therapist\windows\quick_start.py`

## Support

- **PT4 Integration Guide**: `docs\PT4_INTEGRATION.md`
- **WPN Hand History**: `docs\WPN_HAND_HISTORY.md`
- **API Documentation**: http://localhost:8000/docs (when server is running)

## Scripts Summary

| Script | Purpose | Best For |
|--------|---------|----------|
| `setup_pt4.bat` | Initial setup | First time use |
| `quick_start.py` | One-click sync + analysis | Daily use |
| `pt4_sync.py` | Manual hand import | Power users |

---

**User**: JohnDaWalka  
**Player**: jdwalka  
**Primary Site**: Americas Cardroom (ACR)

---

## Electron App (Separate)

See the original `README.md` content above for the Electron/Vue.js desktop application.
