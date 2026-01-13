# Google Cloud Platform Integration Guide

This guide explains how to programmatically set up and use Google Cloud Platform (GCP) services with the Poker Therapist application, including Cloud Storage, APIs, and authentication.

## Table of Contents

1. [Overview](#overview)
2. [GCP Services Used](#gcp-services-used)
3. [Automated GCP Setup](#automated-gcp-setup)
4. [Cloud Storage Usage](#cloud-storage-usage)
5. [API Configuration](#api-configuration)
6. [Service Account Management](#service-account-management)
7. [Code Examples](#code-examples)
8. [Best Practices](#best-practices)
9. [Cost Optimization](#cost-optimization)

## Overview

The Poker Therapist application integrates with Google Cloud Platform for:
- **Authentication**: OAuth 2.0 for user sign-in
- **Cloud Storage**: Storing voice recordings, session data, and user files
- **APIs**: Accessing Google services programmatically

## GCP Services Used

### 1. Cloud Storage
- Store voice recordings
- Session transcripts
- User profile data
- Backup data

### 2. Cloud Identity Platform
- OAuth 2.0 authentication
- User management
- Token management

### 3. Optional Services
- Cloud Speech-to-Text (for voice transcription)
- Cloud Text-to-Speech (for voice responses)
- Cloud Functions (for serverless backend operations)

## Automated GCP Setup

### Prerequisites

1. Install Google Cloud SDK:
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # Windows
   # Download from https://cloud.google.com/sdk/docs/install
   
   # Linux
   curl https://sdk.cloud.google.com | bash
   ```

2. Authenticate:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

### Automated Setup Script

The following script automates GCP setup:

```bash
#!/bin/bash
# setup-gcp.sh - Automate Google Cloud Platform setup

set -e

# Configuration
PROJECT_ID="poker-therapist-prod"
PROJECT_NAME="Poker Therapist"
REGION="us-central1"
BUCKET_NAME="poker-therapist-data"
SERVICE_ACCOUNT_NAME="poker-therapist-sa"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Setting up Google Cloud Platform for Poker Therapist..."

# 1. Create project (if it doesn't exist)
echo "Creating GCP project..."
gcloud projects create $PROJECT_ID \
  --name="$PROJECT_NAME" \
  --set-as-default || echo "Project already exists"

gcloud config set project $PROJECT_ID

# 2. Enable billing (requires billing account)
echo "Note: Billing must be enabled manually at:"
echo "https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"

# 3. Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
  storage.googleapis.com \
  iam.googleapis.com \
  cloudidentity.googleapis.com \
  iamcredentials.googleapis.com

# 4. Create Cloud Storage bucket
echo "Creating Cloud Storage bucket..."
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME/ || echo "Bucket already exists"

# 5. Configure bucket
echo "Configuring bucket..."
gsutil uniformbucketlevelaccess set on gs://$BUCKET_NAME/
gsutil versioning set on gs://$BUCKET_NAME/

# 6. Set bucket lifecycle (delete files older than 90 days)
cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 90,
          "matchesPrefix": ["temp/"]
        }
      }
    ]
  }
}
EOF
gsutil lifecycle set lifecycle.json gs://$BUCKET_NAME/
rm lifecycle.json

# 7. Create service account
echo "Creating service account..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
  --display-name="Poker Therapist Service Account" \
  --description="Service account for backend API access to GCP" || echo "Service account already exists"

# 8. Grant permissions to service account
echo "Granting permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
  --role="roles/storage.objectAdmin"

# 9. Create and download service account key
echo "Creating service account key..."
mkdir -p config
gcloud iam service-accounts keys create config/google-service-account.json \
  --iam-account=$SERVICE_ACCOUNT_EMAIL

echo ""
echo "✅ GCP setup complete!"
echo ""
echo "Next steps:"
echo "1. Enable billing at: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
echo "2. Set up OAuth 2.0 credentials at: https://console.cloud.google.com/apis/credentials?project=$PROJECT_ID"
echo "3. Add config/google-service-account.json to .gitignore"
echo "4. Update .env.local with:"
echo "   GOOGLE_CLOUD_PROJECT_ID=$PROJECT_ID"
echo "   GOOGLE_STORAGE_BUCKET_NAME=$BUCKET_NAME"
echo "   GOOGLE_APPLICATION_CREDENTIALS=./config/google-service-account.json"
echo ""
echo "Service Account Email: $SERVICE_ACCOUNT_EMAIL"
echo "Bucket Name: gs://$BUCKET_NAME"
```

Save this as `scripts/setup-gcp.sh` and run:
```bash
chmod +x scripts/setup-gcp.sh
./scripts/setup-gcp.sh
```

## Cloud Storage Usage

### Uploading Files

```python
from backend.cloud import GoogleStorageService

# Initialize service
storage = GoogleStorageService()

# Upload a voice recording
storage.upload_file(
    file_path='local/recording.wav',
    destination_blob_name='users/user123/recordings/session_001.wav',
    content_type='audio/wav',
    metadata={
        'user_id': 'user123',
        'session_id': 'session_001',
        'timestamp': '2024-01-15T10:30:00Z'
    }
)

# Upload bytes data
audio_data = b'...'  # audio bytes
storage.upload_bytes(
    data=audio_data,
    destination_blob_name='users/user123/recordings/session_002.wav',
    content_type='audio/wav'
)
```

### Downloading Files

```python
# Download to file
storage.download_file(
    blob_name='users/user123/recordings/session_001.wav',
    destination_path='local/downloaded_recording.wav'
)

# Download as bytes
audio_bytes = storage.download_bytes(
    blob_name='users/user123/recordings/session_001.wav'
)
```

### Generating Signed URLs

For secure, temporary file access:

```python
# Generate a signed URL (valid for 1 hour)
signed_url = storage.generate_signed_url(
    blob_name='users/user123/recordings/session_001.wav',
    expiration_minutes=60,
    method='GET'
)

# Share this URL with client
# URL will expire after 60 minutes
```

### Listing Files

```python
# List all files for a user
files = storage.list_files(
    prefix='users/user123/recordings/',
    max_results=100
)

for file in files:
    print(f"Name: {file['name']}")
    print(f"Size: {file['size']} bytes")
    print(f"Created: {file['created']}")
```

## API Configuration

### Enabling APIs

Enable required APIs programmatically:

```bash
# Enable Cloud Storage API
gcloud services enable storage.googleapis.com

# Enable Speech-to-Text (optional)
gcloud services enable speech.googleapis.com

# Enable Text-to-Speech (optional)
gcloud services enable texttospeech.googleapis.com

# List enabled APIs
gcloud services list --enabled
```

### Using APIs in Code

```python
import os
from google.cloud import storage
from google.cloud import speech  # Optional

# Storage client (uses GOOGLE_APPLICATION_CREDENTIALS)
storage_client = storage.Client()

# Speech client (if enabled)
speech_client = speech.SpeechClient()
```

## Service Account Management

### Creating Service Accounts

```bash
# Create service account
gcloud iam service-accounts create poker-therapist-backend \
  --display-name="Backend API Service Account"

# Get service account email
SA_EMAIL=$(gcloud iam service-accounts list \
  --filter="displayName:Backend API Service Account" \
  --format="value(email)")

echo "Service Account: $SA_EMAIL"
```

### Granting Permissions

```bash
# Grant Storage Object Admin role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.objectAdmin"

# Grant Storage Admin role (broader permissions)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.admin"
```

### Managing Keys

```bash
# Create key
gcloud iam service-accounts keys create key.json \
  --iam-account=$SA_EMAIL

# List keys
gcloud iam service-accounts keys list \
  --iam-account=$SA_EMAIL

# Delete old keys
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=$SA_EMAIL
```

## Code Examples

### Complete Upload/Download Example

```python
from backend.cloud import GoogleStorageService
from pathlib import Path
import datetime

class SessionStorageManager:
    """Manage session data in Google Cloud Storage."""
    
    def __init__(self, user_id: str):
        self.storage = GoogleStorageService()
        self.user_id = user_id
        
    def save_voice_recording(self, audio_bytes: bytes, session_id: str) -> str:
        """Save voice recording to cloud storage.
        
        Returns:
            Public URL or signed URL of the uploaded file
        """
        timestamp = datetime.datetime.now().isoformat()
        blob_name = f"users/{self.user_id}/recordings/{session_id}_{timestamp}.wav"
        
        url = self.storage.upload_bytes(
            data=audio_bytes,
            destination_blob_name=blob_name,
            content_type='audio/wav',
            metadata={
                'user_id': self.user_id,
                'session_id': session_id,
                'timestamp': timestamp,
                'type': 'voice_recording'
            }
        )
        
        # Generate signed URL for secure access
        signed_url = self.storage.generate_signed_url(
            blob_name=blob_name,
            expiration_minutes=60
        )
        
        return signed_url
    
    def save_session_transcript(self, transcript: str, session_id: str) -> str:
        """Save session transcript."""
        blob_name = f"users/{self.user_id}/transcripts/{session_id}.txt"
        
        return self.storage.upload_bytes(
            data=transcript.encode('utf-8'),
            destination_blob_name=blob_name,
            content_type='text/plain',
            metadata={
                'user_id': self.user_id,
                'session_id': session_id,
                'type': 'transcript'
            }
        )
    
    def get_user_recordings(self, limit: int = 10) -> list:
        """Get list of user's recordings."""
        return self.storage.list_files(
            prefix=f"users/{self.user_id}/recordings/",
            max_results=limit
        )
    
    def delete_old_recordings(self, days: int = 90):
        """Delete recordings older than specified days."""
        files = self.storage.list_files(
            prefix=f"users/{self.user_id}/recordings/"
        )
        
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        
        for file in files:
            if file['created'] < cutoff_date:
                self.storage.delete_file(file['name'])
                print(f"Deleted old recording: {file['name']}")
```

### Integration with FastAPI

```python
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from backend.cloud import GoogleStorageService
from backend.auth import AuthService

app = FastAPI()
storage = GoogleStorageService()
auth = AuthService()

@app.post("/api/upload-recording")
async def upload_recording(
    file: UploadFile = File(...),
    user_id: str = Depends(auth.get_current_user_id)
):
    """Upload voice recording to cloud storage."""
    
    # Validate file type
    if not file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be audio")
    
    # Read file data
    file_data = await file.read()
    
    # Upload to GCS
    blob_name = f"users/{user_id}/recordings/{file.filename}"
    url = storage.upload_bytes(
        data=file_data,
        destination_blob_name=blob_name,
        content_type=file.content_type
    )
    
    # Generate signed URL for access
    signed_url = storage.generate_signed_url(
        blob_name=blob_name,
        expiration_minutes=60
    )
    
    return {
        "message": "Upload successful",
        "url": signed_url,
        "blob_name": blob_name
    }
```

## Best Practices

### 1. Security

- **Never commit service account keys**: Add `config/*.json` to `.gitignore`
- **Use service accounts**: Don't use personal credentials
- **Rotate keys regularly**: Create new keys annually
- **Principle of least privilege**: Grant minimum necessary permissions
- **Use signed URLs**: For temporary, secure file access

### 2. Organization

```
Bucket structure:
poker-therapist-data/
├── users/
│   └── {user_id}/
│       ├── recordings/
│       │   └── {session_id}_{timestamp}.wav
│       ├── transcripts/
│       │   └── {session_id}.txt
│       └── profile/
│           └── avatar.jpg
├── temp/
│   └── {temp_files}  # Auto-deleted after 1 day
└── backups/
    └── {backup_files}
```

### 3. Performance

- **Use regional buckets**: Choose region closest to users
- **Enable caching**: For frequently accessed files
- **Compress files**: Before uploading (if applicable)
- **Batch operations**: Upload/download multiple files together

### 4. Cost Optimization

- **Lifecycle policies**: Auto-delete old files
- **Storage class**: Use Standard for hot data, Nearline for cool data
- **Data transfer**: Minimize cross-region transfers
- **Monitor usage**: Use GCP cost tracking

Example lifecycle policy:
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 90, "matchesPrefix": ["temp/"]}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 30, "matchesPrefix": ["users/"]}
      }
    ]
  }
}
```

## Cost Optimization

### Estimated Costs

Based on typical usage:

**Cloud Storage:**
- Standard Storage: $0.020 per GB/month
- Nearline Storage: $0.010 per GB/month
- Storage operations: ~$0.05 per 10,000 operations

**Example calculation:**
- 1000 users
- Average 10 MB per user per month (voice recordings)
- Total: 10 GB/month = $0.20/month storage
- Operations: ~50,000/month = $0.25/month
- **Total: ~$0.45/month**

### Cost Saving Tips

1. **Implement lifecycle policies** to auto-delete old files
2. **Compress audio files** before uploading
3. **Use Nearline storage** for archived recordings
4. **Cache frequently accessed files** on CDN
5. **Monitor and set budgets** in GCP console

### Setting Budget Alerts

```bash
# Set budget alert at $10/month
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Poker Therapist Monthly Budget" \
  --budget-amount=10.00 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

## Monitoring and Logging

### View Storage Metrics

```bash
# View bucket size
gsutil du -sh gs://poker-therapist-data

# View object count
gsutil ls -r gs://poker-therapist-data/** | wc -l

# View storage metrics in dashboard
gcloud monitoring dashboards list
```

### Enable Logging

```python
import logging
from google.cloud import logging as gcp_logging

# Set up Cloud Logging
logging_client = gcp_logging.Client()
logging_client.setup_logging()

# Use standard Python logging
logger = logging.getLogger(__name__)
logger.info("File uploaded successfully")
```

## Support and Resources

- **GCP Documentation**: https://cloud.google.com/docs
- **Storage Pricing**: https://cloud.google.com/storage/pricing
- **Storage Best Practices**: https://cloud.google.com/storage/docs/best-practices
- **Python Client Library**: https://googleapis.dev/python/storage/latest/

## Troubleshooting

**Error: "Permission denied"**
- Check service account has correct IAM roles
- Verify `GOOGLE_APPLICATION_CREDENTIALS` points to valid JSON

**Error: "Bucket does not exist"**
- Create bucket with `gsutil mb`
- Check bucket name in environment variables

**Error: "Quota exceeded"**
- Check GCP quotas and limits
- Increase quotas if needed
- Implement rate limiting

For additional support, contact Google Cloud Support or refer to the GCP documentation.
