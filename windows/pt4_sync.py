"""Sync hands from PokerTracker 4 to Poker Therapist.

This script provides easy commands to import hands from your PT4 database
into Poker Therapist for AI analysis with Therapy Rex.

Usage:
    python pt4_sync.py              # Import recent 50 hands
    python pt4_sync.py recent 100   # Import recent 100 hands
    python pt4_sync.py session      # Import last 4 hours
    python pt4_sync.py test         # Test PT4 connection
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PT4_API_URL = os.getenv("POKER_THERAPIST_API_URL", "http://localhost:8000/api/pt4")
USER_ID = os.getenv("POKER_THERAPIST_USER_ID", "JohnDaWalka")
PLAYER_NAME = os.getenv("PT4_PLAYER_NAME", "")


def test_connection() -> bool:
    """Test connection to PT4 database."""
    print("🔍 Testing PT4 connection...")
    
    try:
        response = requests.post(
            f"{PT4_API_URL}/test-connection",
            json={},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result["connected"]:
                print(f"✅ {result['message']}")
                
                if result.get("sites"):
                    print(f"\n📍 Available sites ({len(result['sites'])}):")
                    for site in result["sites"]:
                        print(f"   - {site['site_name']}")
                
                return True
            else:
                print(f"❌ {result['message']}")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            return False
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Poker Therapist API")
        print("   Make sure the API server is running: python -m backend.api.main")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def list_players() -> list[str]:
    """List all players in PT4 database."""
    print("👥 Fetching player list from PT4...")
    
    try:
        response = requests.post(
            f"{PT4_API_URL}/list-players",
            json={},
            timeout=10
        )
        
        if response.status_code == 200:
            players = response.json()["players"]
            print(f"\n✅ Found {len(players)} players:")
            for player in players:
                indicator = "  👉" if player == PLAYER_NAME else "    "
                print(f"{indicator} {player}")
            return players
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            return []
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def sync_recent_hands(limit: int = 50, site_filter: Optional[str] = None) -> Optional[str]:
    """Sync recent hands from PT4.
    
    Args:
        limit: Number of recent hands to import
        site_filter: Optional site name filter (e.g., 'Americas Cardroom')
    
    Returns:
        Session ID if successful, None otherwise
    """
    if not PLAYER_NAME:
        print("❌ PT4_PLAYER_NAME not set in .env file")
        print("   Please set it to your poker screen name")
        return None
    
    print(f"📥 Importing {limit} recent hands for {PLAYER_NAME}...")
    if site_filter:
        print(f"   Filtering by site: {site_filter}")
    
    try:
        response = requests.post(
            f"{PT4_API_URL}/import-recent",
            json={
                "user_id": USER_ID,
                "player_name": PLAYER_NAME,
                "limit": limit,
                "site_filter": site_filter
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Import complete!")
            print(f"   Imported: {result['imported_hands']} hands")
            print(f"   Skipped: {result['skipped_hands']} hands")
            print(f"   📊 Session ID: {result['session_id']}")
            print(f"\n💡 Analyze with: python -m backend.api.main")
            print(f"   Then use session ID: {result['session_id']}")
            return result['session_id']
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def sync_session(hours: int = 4) -> Optional[str]:
    """Sync hands from last N hours.
    
    Args:
        hours: Number of hours to look back
    
    Returns:
        Session ID if successful, None otherwise
    """
    if not PLAYER_NAME:
        print("❌ PT4_PLAYER_NAME not set in .env file")
        return None
    
    now = datetime.now()
    start = now - timedelta(hours=hours)
    
    print(f"📥 Importing session from last {hours} hours for {PLAYER_NAME}...")
    print(f"   Time range: {start.strftime('%Y-%m-%d %H:%M')} to {now.strftime('%Y-%m-%d %H:%M')}")
    
    try:
        response = requests.post(
            f"{PT4_API_URL}/import-session",
            json={
                "user_id": USER_ID,
                "player_name": PLAYER_NAME,
                "session_start": start.isoformat(),
                "session_end": now.isoformat()
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Session import complete!")
            print(f"   Imported: {result['imported_hands']} hands")
            print(f"   Skipped: {result['skipped_hands']} hands")
            print(f"   📊 Session ID: {result['session_id']}")
            return result['session_id']
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def print_usage():
    """Print usage information."""
    print("""
🧠 Poker Therapist - PT4 Sync Tool

Usage:
    python pt4_sync.py                    # Import recent 50 hands
    python pt4_sync.py recent [N]         # Import recent N hands
    python pt4_sync.py session [hours]    # Import last N hours (default: 4)
    python pt4_sync.py test               # Test PT4 connection
    python pt4_sync.py players            # List players in PT4

Environment Variables (.env):
    PT4_PLAYER_NAME              Your poker screen name
    POKER_THERAPIST_USER_ID      Your user ID (optional)
    PT4_DB_HOST                  PT4 database host (default: localhost)
    PT4_DB_PORT                  PT4 database port (default: 5432)
    PT4_DB_NAME                  PT4 database name (default: PT4 DB)
    PT4_DB_USER                  PT4 database user (default: postgres)
    PT4_DB_PASSWORD              PT4 database password

Examples:
    python pt4_sync.py                    # Quick sync
    python pt4_sync.py recent 200         # Import last 200 hands
    python pt4_sync.py session 6          # Import last 6 hours
    python pt4_sync.py test               # Check connection
    """)


def main():
    """Main entry point."""
    print("=" * 60)
    print("🧠 Poker Therapist - PT4 Integration")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        # Default: sync recent 50 hands
        sync_recent_hands(50)
    else:
        command = sys.argv[1].lower()
        
        if command in ["help", "-h", "--help", "?"]:
            print_usage()
        
        elif command == "test":
            test_connection()
        
        elif command == "players":
            list_players()
        
        elif command == "recent":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            sync_recent_hands(limit)
        
        elif command == "session":
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 4
            sync_session(hours)
        
        else:
            print(f"❌ Unknown command: {command}")
            print_usage()


if __name__ == "__main__":
    main()
