"""
Example: Using the new storage services (GCS and Pattern Storage)

This example demonstrates how to use the persistent memory storage features:
1. Google Cloud Storage for audio files and voice profiles
2. SQLite Pattern Storage for user patterns and insights

Run this example with:
    python examples/storage_example.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Example 1: Pattern Storage - User Behavioral Patterns
print("=" * 60)
print("Example 1: Pattern Storage - User Behavioral Patterns")
print("=" * 60)

from python_src.services.pattern_storage import get_pattern_storage

# Initialize pattern storage
pattern_storage = get_pattern_storage("example_storage.db")

# Simulate user ID (in real app, this comes from database)
user_id = 1

# Save betting patterns
print("\n1. Saving betting patterns...")
pattern_storage.save_pattern(
    user_id=user_id,
    pattern_type="betting",
    pattern_key="aggression_level",
    pattern_value=7.5,
    confidence=0.9,
)

pattern_storage.save_pattern(
    user_id=user_id,
    pattern_type="betting",
    pattern_key="3bet_range",
    pattern_value={
        "hands": ["AA", "KK", "QQ", "AKs"],
        "positions": ["BTN", "CO"],
        "frequency": 0.12,
    },
    confidence=0.85,
)

print("   ✓ Saved aggression level and 3-bet range")

# Retrieve patterns
print("\n2. Retrieving patterns...")
aggression = pattern_storage.get_pattern(user_id, "betting", "aggression_level")
print(f"   Aggression level: {aggression}")

all_betting_patterns = pattern_storage.get_patterns_by_type(user_id, "betting")
print(f"   Found {len(all_betting_patterns)} betting patterns:")
for key, data in all_betting_patterns.items():
    print(f"     - {key}: {data['value']} (confidence: {data['confidence']})")

# Save conversation context
print("\n3. Saving conversation context...")
pattern_storage.save_context(
    user_id=user_id,
    context_key="last_topic",
    context_value="preflop strategy",
    session_id="session_123",
    expires_minutes=60,  # Context expires in 1 hour
)

pattern_storage.save_context(
    user_id=user_id,
    context_key="recent_hands",
    context_value=[
        {"hand": "AKs", "position": "BTN", "result": "won"},
        {"hand": "QQ", "position": "CO", "result": "lost"},
    ],
)

print("   ✓ Saved conversation context")

# Retrieve context
context = pattern_storage.get_context(user_id, "last_topic")
print(f"   Last topic: {context[0] if context else 'None'}")

# Save insights
print("\n4. Saving AI-generated insights...")
pattern_storage.save_insight(
    user_id=user_id,
    insight_type="tilt_pattern",
    insight_data={
        "trigger": "consecutive losses",
        "behavior": "increased aggression",
        "correlation": 0.87,
        "recommendation": "Take break after 3 losses in a row",
    },
    importance=0.95,
)

print("   ✓ Saved tilt pattern insight")

# Retrieve insights
insights = pattern_storage.get_insights(user_id, min_importance=0.8)
print(f"\n5. Retrieved {len(insights)} high-importance insights:")
for insight in insights:
    print(f"   - {insight['type']}: importance={insight['importance']}")
    print(f"     {insight['data']}")

# Example 2: Google Cloud Storage (GCS) - If configured
print("\n" + "=" * 60)
print("Example 2: Google Cloud Storage - Audio & Voice Profiles")
print("=" * 60)

try:
    from python_src.services.gcs_storage_service import get_gcs_service
    
    # Try to initialize GCS (with fallback to local storage)
    gcs_service = get_gcs_service(fallback_to_local=True)
    
    if gcs_service:
        print("\n✓ Google Cloud Storage is configured and available")
        print("  Bucket:", os.getenv("GCS_BUCKET_NAME", "not configured"))
        
        # Example: Upload audio file
        print("\n1. Uploading audio file...")
        fake_audio_data = b"fake audio data for demonstration"
        
        try:
            blob_name = gcs_service.upload_audio(
                audio_data=fake_audio_data,
                user_id=f"user_{user_id}",
                filename="example_recording.mp3",
            )
            print(f"   ✓ Uploaded to: {blob_name}")
            
            # Download it back
            downloaded = gcs_service.download_audio(blob_name)
            print(f"   ✓ Downloaded {len(downloaded)} bytes")
            
            # Clean up
            gcs_service.delete_audio(blob_name)
            print("   ✓ Cleaned up test file")
        except Exception as e:
            print(f"   ⚠ Could not test upload (this is OK): {e}")
        
        # Example: Voice profile
        print("\n2. Voice profile storage...")
        fake_voice_samples = [
            b"sample 1 audio data",
            b"sample 2 audio data",
            b"sample 3 audio data",
        ]
        
        try:
            blob_names = gcs_service.upload_voice_profile(
                profile_id="example_profile",
                user_id=f"user_{user_id}",
                voice_samples=fake_voice_samples,
            )
            print(f"   ✓ Uploaded voice profile: {len(blob_names)} samples")
            
            # Download it back
            samples = gcs_service.download_voice_profile(blob_names)
            print(f"   ✓ Downloaded {len(samples)} samples")
            
            # Clean up
            deleted = gcs_service.delete_voice_profile(blob_names)
            print(f"   ✓ Cleaned up {deleted} files")
        except Exception as e:
            print(f"   ⚠ Could not test voice profile (this is OK): {e}")
    else:
        print("\n⚠ Google Cloud Storage not configured - using local storage fallback")
        print("  To enable GCS, set these environment variables:")
        print("    GCS_BUCKET_NAME=your-bucket-name")
        print("    GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json")
        print("    ENABLE_GCS_STORAGE=true")
        
except ImportError:
    print("\n⚠ Google Cloud Storage library not installed")
    print("  Install with: pip install google-cloud-storage")

# Example 3: Integration with Dossier
print("\n" + "=" * 60)
print("Example 3: Dossier Integration - Voice Profile Storage")
print("=" * 60)

from backend.agent.memory.dossier import Dossier

# Initialize dossier (with optional GCS)
try:
    gcs_service = get_gcs_service(fallback_to_local=True) if 'get_gcs_service' in dir() else None
except Exception:
    gcs_service = None

dossier = Dossier(user_id=f"user_{user_id}", gcs_service=gcs_service)

print("\n1. Storing voice profile via Dossier...")
fake_samples = [b"sample 1", b"sample 2", b"sample 3"]

dossier.store_voice_profile(
    profile_id="rex_custom",
    voice_samples=fake_samples,
    metadata={
        "name": "Custom Rex Voice",
        "description": "Professional poker coach tone",
        "language": "en",
    },
)
print("   ✓ Stored voice profile with metadata")

# List profiles
print("\n2. Listing voice profiles...")
profiles = dossier.list_voice_profiles()
print(f"   Found {len(profiles)} profile(s):")
for profile in profiles:
    print(f"     - {profile['profile_id']}: {profile['sample_count']} samples ({profile['storage']})")
    print(f"       Metadata: {profile['metadata']}")

# Retrieve profile
print("\n3. Retrieving voice profile...")
profile_data = dossier.retrieve_voice_profile("rex_custom")
if profile_data:
    print(f"   ✓ Retrieved {len(profile_data['voice_samples'])} samples")
    print(f"   Metadata: {profile_data['metadata']}")

# Clean up
print("\n4. Cleaning up...")
dossier.delete_voice_profile("rex_custom")
print("   ✓ Deleted voice profile")

# Summary
print("\n" + "=" * 60)
print("Summary: Storage Architecture")
print("=" * 60)
print("""
The Poker Therapist now has a hybrid storage architecture:

1. Pattern Storage (SQLite):
   - User behavioral patterns (betting, emotions, preferences)
   - Conversation context and history
   - AI-generated insights and analytics
   - Fast queries with indexes
   
2. Google Cloud Storage (GCS):
   - Audio files (recordings, TTS output)
   - Voice profiles for voice cloning
   - Large binary data
   - Automatic fallback to local storage
   
3. Dossier Integration:
   - Seamlessly uses GCS when available
   - Falls back to local storage automatically
   - Metadata stored in JSON, binaries in GCS

Benefits:
✓ Persistent memory across sessions
✓ Scalable storage for audio data
✓ Fast pattern recognition and insights
✓ Automatic fallback to local storage
✓ Thread-safe and multi-process safe

See docs/STORAGE_ARCHITECTURE.md for detailed documentation.
""")

print("\n✓ Example completed successfully!")
print(f"\nNote: Test database created at: {Path('example_storage.db').absolute()}")
print("You can delete it after reviewing this example.\n")
