# GCP Persistent Memory Setup Guide

This guide explains how to configure Google Cloud Platform (GCP) persistent memory for the Poker Therapist application.

## Overview

The application uses GCP Firestore for persistent data storage and Cloud Storage for file storage. This provides:

- **Scalable NoSQL database** - Firestore for user data, sessions, and chat history
- **File storage** - Cloud Storage for audio files, hand histories, and exports
- **Global availability** - Low-latency access from anywhere
- **Real-time sync** - Live updates across devices
- **Automatic backups** - Point-in-time recovery

## Prerequisites

1. Google Cloud Platform account
2. GCP project created
3. Billing enabled on the project
4. GCP CLI (`gcloud`) installed (optional, for local setup)

## Step 1: Create GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: `poker-therapist`
4. Note the Project ID (e.g., `poker-therapist-12345`)

## Step 2: Enable Required APIs

Enable the following APIs in your GCP project:

```bash
gcloud services enable firestore.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable iam.googleapis.com
```

Or enable via Console:
- Firestore API
- Cloud Storage API
- Identity and Access Management (IAM) API

## Step 3: Set Up Firestore

1. Go to [Firestore](https://console.cloud.google.com/firestore)
2. Click "Create database"
3. Select "Native mode" (recommended for new projects)
4. Choose a location (e.g., `us-central`)
5. Click "Create database"

### Firestore Collections

The application automatically creates these collections:

- `users` - User profiles and authentication data
- `sessions` - Therapy session records
- `messages` - Chat message history
- `tilt_profiles` - User tilt detection profiles
- `playbooks` - Mental game playbooks
- `hand_histories` - Poker hand records

## Step 4: Set Up Cloud Storage

1. Go to [Cloud Storage](https://console.cloud.google.com/storage)
2. Click "Create bucket"
3. Bucket name: `poker-therapist-storage` (must be globally unique)
4. Location: Same as Firestore (e.g., `us-central`)
5. Storage class: `Standard`
6. Access control: `Uniform`
7. Click "Create"

## Step 5: Create Service Account

1. Go to [IAM & Admin → Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click "Create Service Account"
3. Name: `poker-therapist-api`
4. Description: "Service account for Poker Therapist API"
5. Click "Create and continue"

### Assign Roles

Grant these roles to the service account:

- **Cloud Datastore User** - Read/write access to Firestore
- **Storage Object Admin** - Read/write access to Cloud Storage
- **Service Account Token Creator** - For authentication

## Step 6: Generate Service Account Key

1. Click on the created service account
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Select "JSON" format
5. Click "Create"
6. Save the downloaded JSON file as `gcp-credentials.json`

⚠️ **Important**: Keep this file secure and never commit it to version control!

## Step 7: Configure Environment Variables

### For Local Development

Create a `.env.local` file:

```bash
# GCP Configuration
GCP_PROJECT_ID=poker-therapist-12345
GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json
FIRESTORE_DATABASE=(default)
GCS_BUCKET_NAME=poker-therapist-storage
```

### For Vercel Deployment

Add environment variables in Vercel dashboard:

1. Go to your project settings in Vercel
2. Navigate to "Environment Variables"
3. Add the following variables:

```
GCP_PROJECT_ID=poker-therapist-12345
GOOGLE_APPLICATION_CREDENTIALS=<paste entire JSON content>
FIRESTORE_DATABASE=(default)
GCS_BUCKET_NAME=poker-therapist-storage
```

**Note**: For `GOOGLE_APPLICATION_CREDENTIALS` in Vercel, paste the entire JSON content as a single-line string.

## Step 8: Test the Configuration

Run the following test script:

```python
import asyncio
from backend.agent.memory.firestore_adapter import firestore_adapter

async def test_firestore():
    # Test user creation
    await firestore_adapter.create_user("test-user-123", "test@example.com")
    
    # Test user retrieval
    user = await firestore_adapter.get_user("test-user-123")
    print(f"User created: {user}")
    
    # Test message save
    msg_id = await firestore_adapter.save_message(
        "test-user-123", 
        "user", 
        "Hello, Rex!"
    )
    print(f"Message saved: {msg_id}")
    
    # Test message retrieval
    messages = await firestore_adapter.get_user_messages("test-user-123")
    print(f"Messages: {messages}")

asyncio.run(test_firestore())
```

## Security Best Practices

### Service Account Permissions

- ✅ Use principle of least privilege
- ✅ Create separate service accounts for different environments
- ✅ Rotate service account keys regularly (every 90 days)
- ✅ Monitor service account usage

### Credentials Management

- ❌ Never commit `gcp-credentials.json` to Git
- ❌ Never share credentials in chat or email
- ✅ Use environment variables
- ✅ Enable secrets encryption in Vercel
- ✅ Use GCP Secret Manager for production

### Firestore Security Rules

Set up security rules in Firestore:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    match /sessions/{sessionId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
    
    match /messages/{messageId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
  }
}
```

## Monitoring and Costs

### Monitor Usage

1. Go to [Cloud Console → Monitoring](https://console.cloud.google.com/monitoring)
2. Create dashboards for:
   - Firestore read/write operations
   - Cloud Storage bandwidth
   - API request counts

### Cost Optimization

**Firestore Free Tier** (per day):
- 50,000 reads
- 20,000 writes
- 20,000 deletes
- 1 GB storage

**Cloud Storage Free Tier**:
- 5 GB storage (US regions)
- 1 GB network egress to Americas

**Tips**:
- Use Firestore indexes efficiently
- Cache frequently accessed data
- Compress files before storing
- Set lifecycle policies for old data

## Troubleshooting

### Authentication Errors

```
Error: Could not load the default credentials
```

**Solution**: Check that `GOOGLE_APPLICATION_CREDENTIALS` points to valid JSON file.

### Permission Denied

```
Error: Missing or insufficient permissions
```

**Solution**: Verify service account has required roles (Datastore User, Storage Object Admin).

### Firestore Not Initialized

```
Error: Database not found
```

**Solution**: Create Firestore database in Console and ensure `FIRESTORE_DATABASE` is set.

## Backup and Recovery

### Automatic Backups

Firestore automatically backs up data. Enable point-in-time recovery:

```bash
gcloud firestore databases update --enable-pitr
```

### Manual Export

```bash
gcloud firestore export gs://poker-therapist-backups
```

### Restore from Backup

```bash
gcloud firestore import gs://poker-therapist-backups/[TIMESTAMP]
```

## Migration from SQLite

The application uses a hybrid approach:

1. **Development**: Uses SQLite locally
2. **Production**: Uses Firestore in GCP/Vercel
3. **Hybrid Mode**: Can use both simultaneously

Data is automatically synced between SQLite and Firestore when both are configured.

## Additional Resources

- [Firestore Documentation](https://cloud.google.com/firestore/docs)
- [Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Service Account Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)
- [GCP Pricing Calculator](https://cloud.google.com/products/calculator)

## Support

For issues with GCP setup:
- Check [GCP Status Dashboard](https://status.cloud.google.com/)
- Review [Cloud Console Logs](https://console.cloud.google.com/logs)
- Contact GCP Support (if using paid plan)
