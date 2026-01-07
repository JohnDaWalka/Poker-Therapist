# Storage Architecture

This document describes the persistent memory architecture for Poker Therapist, which uses a hybrid storage approach combining Google Cloud Storage (GCS) and SQLite.

## Overview

The application uses two complementary storage systems:

1. **Google Cloud Storage (GCS)**: For large binary data (audio files, voice profiles)
2. **SQLite**: For structured data (user patterns, conversation context, insights)

## Components

### 1. Google Cloud Storage Service (`gcs_storage_service.py`)

Handles storage and retrieval of binary data in Google Cloud Storage.

#### Features
- Audio file storage (voice recordings, TTS output)
- Voice profile storage (voice cloning samples)
- Signed URL generation for temporary access
- Automatic fallback to local storage when GCS is unavailable

#### Configuration

Set the following environment variables:

```bash
# Required: GCS bucket name
GCS_BUCKET_NAME=poker-therapist-storage

# Required: Path to service account credentials
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Optional: Enable/disable GCS (defaults to false)
ENABLE_GCS_STORAGE=true
```

#### Usage Example

```python
from python_src.services.gcs_storage_service import get_gcs_service

# Initialize service (with fallback to local storage)
gcs_service = get_gcs_service(fallback_to_local=True)

if gcs_service:
    # Upload audio
    blob_name = gcs_service.upload_audio(
        audio_data=b"audio bytes",
        user_id="user123",
        filename="recording.mp3",
    )
    
    # Download audio
    audio_data = gcs_service.download_audio(blob_name)
    
    # Upload voice profile
    blob_names = gcs_service.upload_voice_profile(
        profile_id="profile123",
        user_id="user123",
        voice_samples=[b"sample1", b"sample2", b"sample3"],
    )
    
    # Get signed URL for temporary access
    url = gcs_service.get_signed_url(blob_name, expiration_minutes=60)
```

#### Storage Structure

```
bucket-name/
├── audio/
│   └── {user_id}/
│       ├── recording1.mp3
│       ├── recording2.mp3
│       └── ...
└── voice_profiles/
    └── {user_id}/
        └── {profile_id}/
            ├── sample_0.wav
            ├── sample_1.wav
            └── sample_2.wav
```

### 2. Pattern Storage (`pattern_storage.py`)

Manages structured user data in SQLite database.

#### Features
- User behavioral patterns (betting patterns, emotional triggers)
- Conversation context and history
- User insights and analytics
- Session-based context management
- Automatic expiration of temporary context

#### Database Schema

**user_patterns** - User behavioral patterns
```sql
CREATE TABLE user_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pattern_type TEXT NOT NULL,      -- e.g., "betting", "emotion", "preference"
    pattern_key TEXT NOT NULL,       -- e.g., "aggression_level", "tilt_trigger"
    pattern_value TEXT NOT NULL,     -- JSON-serialized value
    confidence REAL DEFAULT 1.0,     -- 0.0 to 1.0
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(user_id, pattern_type, pattern_key)
);
```

**conversation_context** - Conversation context
```sql
CREATE TABLE conversation_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    context_key TEXT NOT NULL,       -- e.g., "last_topic", "current_hand"
    context_value TEXT NOT NULL,     -- JSON-serialized value
    session_id TEXT,                 -- Optional session identifier
    created_at TIMESTAMP,
    expires_at TIMESTAMP             -- Optional expiration
);
```

**user_insights** - AI-generated insights
```sql
CREATE TABLE user_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    insight_type TEXT NOT NULL,      -- e.g., "tilt_pattern", "win_correlation"
    insight_data TEXT NOT NULL,      -- JSON-serialized insight data
    importance REAL DEFAULT 0.5,     -- 0.0 to 1.0
    created_at TIMESTAMP
);
```

#### Usage Example

```python
from python_src.services.pattern_storage import get_pattern_storage

# Initialize storage
pattern_storage = get_pattern_storage("RexVoice.db")

# Save user patterns
pattern_storage.save_pattern(
    user_id=1,
    pattern_type="betting",
    pattern_key="aggression_level",
    pattern_value=7.5,
    confidence=0.9,
)

# Get pattern
aggression = pattern_storage.get_pattern(
    user_id=1,
    pattern_type="betting",
    pattern_key="aggression_level",
)

# Get all patterns of a type
betting_patterns = pattern_storage.get_patterns_by_type(
    user_id=1,
    pattern_type="betting",
)

# Save conversation context
pattern_storage.save_context(
    user_id=1,
    context_key="last_topic",
    context_value="bad beat discussion",
    session_id="session123",
    expires_minutes=60,  # Optional expiration
)

# Get context
topics = pattern_storage.get_context(
    user_id=1,
    context_key="last_topic",
    session_id="session123",
)

# Save insights
pattern_storage.save_insight(
    user_id=1,
    insight_type="tilt_pattern",
    insight_data={
        "trigger": "consecutive losses",
        "pattern": "increased aggression",
        "correlation": 0.85,
    },
    importance=0.9,
)

# Get insights
insights = pattern_storage.get_insights(
    user_id=1,
    insight_type="tilt_pattern",
    min_importance=0.7,
    limit=10,
)
```

### 3. Enhanced Dossier Class

The existing `Dossier` class has been extended to support GCS for voice profile storage.

#### Features
- Automatic GCS integration when available
- Seamless fallback to local storage
- Voice profile management with metadata
- Cross-platform file locking for safety

#### Usage Example

```python
from backend.agent.memory.dossier import Dossier
from python_src.services.gcs_storage_service import get_gcs_service

# Initialize with optional GCS service
gcs_service = get_gcs_service(fallback_to_local=True)
dossier = Dossier(user_id="user123", gcs_service=gcs_service)

# Store voice profile
dossier.store_voice_profile(
    profile_id="profile123",
    voice_samples=[b"sample1", b"sample2"],
    metadata={
        "name": "Custom Rex Voice",
        "description": "Professional poker coach tone",
    },
)

# Retrieve voice profile
profile_data = dossier.retrieve_voice_profile("profile123")
if profile_data:
    voice_samples = profile_data["voice_samples"]
    metadata = profile_data["metadata"]

# List profiles
profiles = dossier.list_voice_profiles()

# Delete profile
dossier.delete_voice_profile("profile123")
```

## Integration with Chatbot App

The storage services are automatically initialized in `chatbot_app.py`:

```python
# Services are initialized on app start
gcs_service = st.session_state.gcs_service
pattern_storage = st.session_state.pattern_storage

# Use in voice features
if gcs_service:
    # Store voice recordings in GCS
    blob_name = gcs_service.upload_audio(...)
    
# Use pattern storage for user insights
if pattern_storage:
    # Track user patterns
    pattern_storage.save_pattern(...)
    
    # Store conversation context
    pattern_storage.save_context(...)
```

## Storage Strategy

### When to use GCS vs SQLite

**Use GCS for:**
- Audio files (voice recordings, TTS output)
- Voice profile samples
- Any binary data > 1MB
- Files that need signed URLs for sharing

**Use SQLite for:**
- User patterns and preferences
- Conversation context
- Message history
- AI-generated insights
- Metadata and references

### Fallback Behavior

The system is designed to gracefully handle GCS unavailability:

1. If GCS is not configured, automatically uses local storage
2. If GCS upload fails, falls back to local storage
3. Local storage uses the same structure as GCS paths
4. Migration from local to GCS can be done later

## Performance Considerations

### SQLite Optimizations
- Indexes on frequently queried columns (user_id, pattern_type, etc.)
- Automatic cleanup of expired context
- JSON serialization for complex values
- Connection pooling via context managers

### GCS Optimizations
- Batch uploads for voice profiles
- Signed URLs to avoid repeated downloads
- Parallel uploads when possible
- Efficient blob naming for listing operations

## Security

### GCS Security
- Service account credentials stored securely
- Bucket-level IAM permissions
- Signed URLs with expiration
- No public access to blobs

### SQLite Security
- File-level permissions
- No sensitive data in database (audio stored externally)
- User isolation through user_id foreign keys

## Monitoring and Maintenance

### Health Checks
```python
# Check if GCS is available
if gcs_service and gcs_service.is_available():
    print("GCS is operational")

# Check database
pattern_storage = get_pattern_storage()
# Will raise exception if database is corrupted
```

### Cleanup Operations
```python
# Clear expired context (automatic on query)
pattern_storage.get_context(user_id, "any_key")

# Manual cleanup
pattern_storage.clear_user_context(user_id)
pattern_storage.clear_user_patterns(user_id)

# Delete old voice profiles
for profile in dossier.list_voice_profiles():
    if should_delete(profile):
        dossier.delete_voice_profile(profile["profile_id"])
```

## Migration Guide

### Setting up GCS

1. Create a GCS bucket:
```bash
gsutil mb gs://poker-therapist-storage
```

2. Create a service account with Storage Admin role

3. Download credentials JSON

4. Configure environment:
```bash
export GCS_BUCKET_NAME=poker-therapist-storage
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
export ENABLE_GCS_STORAGE=true
```

### Migrating from Local to GCS

```python
from pathlib import Path
from python_src.services.gcs_storage_service import get_gcs_service

gcs_service = get_gcs_service()

# Migrate voice profiles
for user_dir in Path("voice_profiles").iterdir():
    user_id = user_dir.name
    for profile_dir in user_dir.iterdir():
        profile_id = profile_dir.name
        
        # Read local samples
        samples = []
        for sample_file in sorted(profile_dir.glob("sample_*.wav")):
            samples.append(sample_file.read_bytes())
        
        # Upload to GCS
        blob_names = gcs_service.upload_voice_profile(
            profile_id=profile_id,
            user_id=user_id,
            voice_samples=samples,
        )
        
        print(f"Migrated {profile_id} for user {user_id}")
```

## Testing

Tests are provided for both storage services:

```bash
# Run GCS storage tests
pytest tests/test_gcs_storage.py

# Run pattern storage tests
pytest tests/test_pattern_storage.py

# Run Dossier tests (includes GCS integration)
pytest tests/test_dossier.py
```

## Troubleshooting

### GCS Authentication Issues
- Verify GOOGLE_APPLICATION_CREDENTIALS points to valid JSON
- Check service account has Storage Admin role
- Verify bucket exists and is accessible

### SQLite Lock Issues
- Dossier class uses file locking for safety
- If locks persist, check for zombie processes
- Consider increasing timeout or using WAL mode

### Storage Space
- Monitor GCS bucket size in Cloud Console
- Implement cleanup policies for old audio files
- Archive or delete unused voice profiles

## Future Enhancements

- [ ] Implement bucket lifecycle policies for automatic cleanup
- [ ] Add Redis caching layer for frequently accessed patterns
- [ ] Support for multiple storage backends (AWS S3, Azure Blob)
- [ ] Compression for audio files before upload
- [ ] Batch operations for pattern updates
- [ ] Real-time sync between multiple app instances
