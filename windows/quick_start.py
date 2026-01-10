"""Quick start script for JohnDaWalka's Poker Therapist setup.

This script helps you quickly sync your poker hands from PT4 and get analysis.
"""

import os
import sys
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

# JohnDaWalka's Configuration
USER_ID = "JohnDaWalka"
PLAYER_NAME = os.getenv("PT4_PLAYER_NAME", "jdwalka")
API_URL = "http://localhost:8000/api"


def quick_sync():
    """Quick sync of recent hands."""
    print("🎰 JohnDaWalka's Poker Therapist - Quick Sync")
    print("=" * 60)
    
    # Test connection
    print("\n1️⃣ Testing PT4 connection...")
    try:
        response = requests.post(
            f"{API_URL}/pt4/test-connection",
            json={},
            timeout=10
        )
        
        if response.status_code == 200 and response.json()["connected"]:
            print("   ✅ Connected to PT4!")
        else:
            print("   ❌ Cannot connect to PT4")
            print("   💡 Make sure PokerTracker 4 is running")
            return
    except:
        print("   ❌ API server not running")
        print("   💡 Start with: python -m backend.api.main")
        return
    
    # Import recent hands
    print(f"\n2️⃣ Importing recent hands for {PLAYER_NAME}...")
    try:
        response = requests.post(
            f"{API_URL}/pt4/import-recent",
            json={
                "user_id": USER_ID,
                "player_name": PLAYER_NAME,
                "limit": 100,
                "site_filter": "Americas Cardroom"  # Your primary site
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            session_id = result['session_id']
            print(f"   ✅ Imported {result['imported_hands']} hands")
            print(f"   📊 Session ID: {session_id}")
        else:
            print(f"   ❌ Import failed: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Get session review
    print("\n3️⃣ Getting Therapy Rex analysis...")
    try:
        response = requests.post(
            f"{API_URL}/wpn/session-review",
            json={
                "user_id": USER_ID,
                "session_id": session_id,
                "max_hands": 50
            },
            timeout=120
        )
        
        if response.status_code == 200:
            analysis = response.json()
            print("\n" + "=" * 60)
            print("📊 STRATEGY REVIEW")
            print("=" * 60)
            print(analysis.get("strategy_review", "No strategy review available"))
            
            print("\n" + "=" * 60)
            print("🧠 THERAPY REVIEW")
            print("=" * 60)
            print(analysis.get("therapy_review", "No therapy review available"))
            
            print("\n✅ Analysis complete!")
        else:
            print(f"   ⚠️  Analysis not available yet")
            print(f"   💡 Session ID saved: {session_id}")
    except Exception as e:
        print(f"   ⚠️  Analysis error: {e}")
        print(f"   💡 Session ID saved: {session_id}")
    
    print("\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("   - Review your strategy insights above")
    print("   - Visit http://localhost:8000/docs for full API")
    print(f"   - Your session ID: {session_id}")
    print("=" * 60)


def import_todays_session():
    """Import all hands from today."""
    print("🎰 JohnDaWalka's Poker Therapist - Today's Session")
    print("=" * 60)
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    now = datetime.now()
    
    print(f"\n📥 Importing all hands from today...")
    print(f"   Time range: {today.strftime('%Y-%m-%d %H:%M')} to now")
    
    try:
        response = requests.post(
            f"{API_URL}/pt4/import-session",
            json={
                "user_id": USER_ID,
                "player_name": PLAYER_NAME,
                "session_start": today.isoformat(),
                "session_end": now.isoformat()
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Imported {result['imported_hands']} hands from today")
            print(f"📊 Session ID: {result['session_id']}")
            
            # Get quick stats
            print("\n💡 Use this session ID for detailed analysis:")
            print(f"   python -c 'import requests; print(requests.post(\"http://localhost:8000/api/wpn/session-review\", json={{\"user_id\": \"{USER_ID}\", \"session_id\": \"{result['session_id']}\"}}).json())'")
        else:
            print(f"❌ Import failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")


def list_sessions():
    """List all your sessions."""
    print("🎰 JohnDaWalka's Poker Therapist - Session History")
    print("=" * 60)
    
    try:
        response = requests.get(
            f"{API_URL}/wpn/sessions/{USER_ID}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            sessions = data.get("sessions", [])
            
            if not sessions:
                print("\n📭 No sessions found yet")
                print("   💡 Import hands first with: python windows/pt4_sync.py")
            else:
                print(f"\n📊 Found {len(sessions)} sessions:\n")
                for i, session in enumerate(sessions[:10], 1):
                    print(f"{i}. Session ID: {session['session_id']}")
                    print(f"   Hands: {session['hands']}")
                    if session.get('last_played'):
                        print(f"   Last played: {session['last_played']}")
                    print()
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "today":
            import_todays_session()
        elif command == "sessions":
            list_sessions()
        else:
            print(f"Unknown command: {command}")
            print("Usage:")
            print("  python windows/quick_start.py          # Quick sync recent hands")
            print("  python windows/quick_start.py today    # Import all hands from today")
            print("  python windows/quick_start.py sessions # List all sessions")
    else:
        quick_sync()


if __name__ == "__main__":
    main()
