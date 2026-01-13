# Deployment and Testing Guide

This guide explains how to deploy and test the Poker Therapist application with GCP persistent memory and authentication.

## Overview

The application now supports:
- **GCP Firestore** for persistent data storage
- **Microsoft Azure AD** authentication for institutional users
- **Google OAuth 2.0** for Google account and GCP API access
- **Hybrid storage** - works with both local SQLite and cloud Firestore

## Prerequisites

Before deploying, ensure you have completed:

1. ✅ [GCP Setup](GCP_SETUP.md) - Firestore and Cloud Storage configured
2. ✅ [Authentication Setup](AUTHENTICATION_SETUP.md) - Microsoft and Google OAuth configured
3. ✅ API keys configured for AI services (xAI, OpenAI, etc.)

## Local Development Setup

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import google.cloud.firestore; print('Firestore OK')"
python -c "import authlib; print('Authlib OK')"
```

### 2. Configure Environment

Create `.env.local`:

```bash
# AI API Keys
XAI_API_KEY=xai-your-key-here
OPENAI_API_KEY=sk-your-openai-key-here

# GCP Configuration
GCP_PROJECT_ID=poker-therapist-12345
GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json
FIRESTORE_DATABASE=(default)
GCS_BUCKET_NAME=poker-therapist-storage

# Authentication
AZURE_TENANT_ID=your-azure-tenant-id
AZURE_CLIENT_ID=your-azure-client-id
AZURE_CLIENT_SECRET=your-azure-client-secret
AZURE_REDIRECT_URI=http://localhost:8000/auth/callback/microsoft

GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback/google

SESSION_SECRET_KEY=your-session-secret-key
AUTHENTICATION_ENABLED=true
INSTITUTIONAL_EMAIL_DOMAINS=ctstate.edu

# Authorized emails
AUTHORIZED_EMAILS=m.fanelli1@icloud.com,johndawalka@icloud.com,mauro.fanelli@ctstate.edu
```

### 3. Test Local Setup

```bash
# Test FastAPI backend
uvicorn backend.api.main:app --reload --port 8000

# In another terminal, test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs  # API documentation
```

### 4. Test Streamlit Chatbot

```bash
# Run Streamlit app
streamlit run chatbot_app.py

# Access at http://localhost:8501
```

## Testing Authentication

### Test Microsoft SSO

1. Start the FastAPI server:
   ```bash
   uvicorn backend.api.main:app --reload --port 8000
   ```

2. Navigate to: `http://localhost:8000/auth/login/microsoft`

3. You should be redirected to Microsoft login page

4. Enter institutional email (e.g., `user@ctstate.edu`)

5. After authentication, you'll receive a JWT token

6. Test protected endpoint:
   ```bash
   TOKEN="your-jwt-token"
   curl -X POST http://localhost:8000/api/triage \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"emotion": "frustrated", "intensity": 7}'
   ```

### Test Google OAuth

1. Navigate to: `http://localhost:8000/auth/login/google`

2. Select your Google account

3. Grant permissions when prompted

4. You'll receive a JWT token with GCP API access

5. Test with the token as shown above

## Testing GCP Firestore

### Test Firestore Integration

Create a test script `test_firestore.py`:

```python
import asyncio
import os
from backend.agent.memory.firestore_adapter import firestore_adapter

async def test_firestore():
    print("Testing Firestore integration...")
    
    # Test 1: Create user
    print("\n1. Creating test user...")
    await firestore_adapter.create_user("test-user-123", "test@example.com")
    print("✅ User created")
    
    # Test 2: Retrieve user
    print("\n2. Retrieving user...")
    user = await firestore_adapter.get_user("test-user-123")
    print(f"✅ User retrieved: {user}")
    
    # Test 3: Save message
    print("\n3. Saving message...")
    msg_id = await firestore_adapter.save_message(
        "test-user-123", 
        "user", 
        "Hello, Rex!"
    )
    print(f"✅ Message saved with ID: {msg_id}")
    
    # Test 4: Retrieve messages
    print("\n4. Retrieving messages...")
    messages = await firestore_adapter.get_user_messages("test-user-123")
    print(f"✅ Messages retrieved: {len(messages)} messages")
    for msg in messages:
        print(f"  - {msg['role']}: {msg['content']}")
    
    # Test 5: Save session
    print("\n5. Saving therapy session...")
    session_data = {
        "user_id": "test-user-123",
        "session_type": "triage",
        "emotion": "frustrated",
        "intensity": 7,
        "severity": 6,
    }
    session_id = await firestore_adapter.save_session(session_data)
    print(f"✅ Session saved with ID: {session_id}")
    
    # Test 6: Retrieve sessions
    print("\n6. Retrieving sessions...")
    sessions = await firestore_adapter.get_user_sessions("test-user-123")
    print(f"✅ Sessions retrieved: {len(sessions)} sessions")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    # Check GCP is configured
    if not os.getenv("GCP_PROJECT_ID"):
        print("❌ GCP_PROJECT_ID not set. Please configure GCP first.")
        exit(1)
    
    asyncio.run(test_firestore())
```

Run the test:

```bash
python test_firestore.py
```

### Test Hybrid Storage

Test that data is saved to both SQLite and Firestore:

```python
import asyncio
from backend.agent.memory.hybrid_store import hybrid_memory
from backend.agent.memory.db_session import get_db

async def test_hybrid():
    print("Testing hybrid storage...")
    
    async with get_db() as db_session:
        # Save session
        session_data = {
            "session_id": "test-session-456",
            "user_id": "test-user-123",
            "session_type": "deep",
            "start_time": "2024-01-13T10:00:00Z",
            "emotion": "anxious",
            "intensity": 8,
            "severity": 7,
        }
        
        session_id = await hybrid_memory.save_session(session_data, db_session)
        print(f"✅ Session saved to hybrid storage: {session_id}")
        
        # Retrieve from both stores
        sessions = await hybrid_memory.get_user_sessions(
            "test-user-123", 
            limit=10, 
            db_session=db_session
        )
        print(f"✅ Retrieved {len(sessions)} sessions")

if __name__ == "__main__":
    asyncio.run(test_hybrid())
```

## Vercel Deployment

### 1. Configure Environment Variables

In Vercel dashboard, add all environment variables:

```
XAI_API_KEY=<your-key>
OPENAI_API_KEY=<your-key>
GCP_PROJECT_ID=poker-therapist-12345
GOOGLE_APPLICATION_CREDENTIALS=<paste entire JSON>
FIRESTORE_DATABASE=(default)
GCS_BUCKET_NAME=poker-therapist-storage
AZURE_TENANT_ID=<your-tenant-id>
AZURE_CLIENT_ID=<your-client-id>
AZURE_CLIENT_SECRET=<your-secret>
AZURE_REDIRECT_URI=https://your-app.vercel.app/auth/callback/microsoft
GOOGLE_OAUTH_CLIENT_ID=<your-client-id>
GOOGLE_OAUTH_CLIENT_SECRET=<your-secret>
GOOGLE_OAUTH_REDIRECT_URI=https://your-app.vercel.app/auth/callback/google
SESSION_SECRET_KEY=<your-secret-key>
AUTHENTICATION_ENABLED=true
INSTITUTIONAL_EMAIL_DOMAINS=ctstate.edu
AUTHORIZED_EMAILS=<comma-separated-list>
```

### 2. Deploy

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

### 3. Verify Deployment

```bash
# Test health endpoint
curl https://your-app.vercel.app/health

# Test API docs
open https://your-app.vercel.app/docs
```

## End-to-End Testing

### Test Complete Authentication Flow

1. **Access the application**:
   ```
   https://your-app.vercel.app
   ```

2. **Login with Microsoft**:
   - Click "Login with Microsoft"
   - Enter institutional email
   - Verify redirection and token received

3. **Login with Google**:
   - Click "Login with Google"
   - Select Google account
   - Verify permissions and token received

4. **Test protected endpoints**:
   ```bash
   # Get token from login
   TOKEN="your-jwt-token"
   
   # Test triage endpoint
   curl -X POST https://your-app.vercel.app/api/triage \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "emotion": "frustrated",
       "intensity": 7,
       "body_sensation": "tight chest",
       "still_playing": true
     }'
   ```

### Test Data Persistence

1. **Create a session**:
   ```bash
   curl -X POST https://your-app.vercel.app/api/triage \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "emotion": "frustrated",
       "intensity": 7
     }'
   ```

2. **Verify in Firestore**:
   - Go to [Firestore Console](https://console.cloud.google.com/firestore)
   - Navigate to `sessions` collection
   - Verify your session is stored

3. **Retrieve session data**:
   ```bash
   curl https://your-app.vercel.app/api/tracking \
     -H "Authorization: Bearer $TOKEN"
   ```

### Test Multi-Model AI

Test that all AI models can access persistent context:

```bash
# Test with different models via the chatbot
# Each model should be able to access conversation history from Firestore

# Test xAI (Grok)
# Test OpenAI (GPT-4)
# Test Anthropic (Claude)
# Test Google (Gemini)
```

## Performance Testing

### Test Response Times

```bash
# Install Apache Bench
apt-get install apache2-utils  # Linux
brew install httpd  # Mac

# Test health endpoint
ab -n 100 -c 10 https://your-app.vercel.app/health

# Test authenticated endpoint (with token)
ab -n 50 -c 5 -H "Authorization: Bearer $TOKEN" \
   https://your-app.vercel.app/api/tracking
```

### Test Firestore Performance

```python
import asyncio
import time
from backend.agent.memory.firestore_adapter import firestore_adapter

async def benchmark_firestore():
    print("Benchmarking Firestore operations...")
    
    # Benchmark writes
    start = time.time()
    for i in range(100):
        await firestore_adapter.save_message(
            "benchmark-user",
            "user",
            f"Test message {i}"
        )
    write_time = time.time() - start
    print(f"✅ 100 writes: {write_time:.2f}s ({100/write_time:.1f} writes/sec)")
    
    # Benchmark reads
    start = time.time()
    for i in range(100):
        await firestore_adapter.get_user_messages("benchmark-user", limit=50)
    read_time = time.time() - start
    print(f"✅ 100 reads: {read_time:.2f}s ({100/read_time:.1f} reads/sec)")

asyncio.run(benchmark_firestore())
```

## Monitoring

### Check Application Logs

```bash
# Vercel logs
vercel logs --follow

# Filter for errors
vercel logs --follow | grep ERROR
```

### Monitor Firestore Usage

1. Go to [Cloud Console → Firestore](https://console.cloud.google.com/firestore)
2. Navigate to "Usage" tab
3. Monitor:
   - Read operations
   - Write operations
   - Storage size

### Monitor Authentication

1. **Microsoft Azure AD**:
   - Go to Azure Portal → Azure AD → Sign-in logs
   - Review authentication attempts

2. **Google OAuth**:
   - Go to [Google Cloud Console → APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials)
   - Review OAuth consent screen analytics

## Troubleshooting

### Common Issues

#### Authentication Fails

```
Error: Invalid redirect URI
```

**Solution**: Verify redirect URIs match exactly in Azure/Google console and environment variables.

#### Firestore Connection Fails

```
Error: Could not load credentials
```

**Solution**: 
- Check `GOOGLE_APPLICATION_CREDENTIALS` is set correctly
- Verify service account has required permissions
- Ensure Firestore API is enabled

#### Token Expired

```
Error: Token has expired
```

**Solution**: Implement token refresh or have user re-authenticate.

### Debug Mode

Enable debug logging:

```python
# In backend/api/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Checklist

Before going to production:

- [ ] All secrets stored in environment variables (not in code)
- [ ] HTTPS enabled (automatic with Vercel)
- [ ] Authentication enabled (`AUTHENTICATION_ENABLED=true`)
- [ ] Session secret key generated securely
- [ ] Firestore security rules configured
- [ ] GCP service account has minimal required permissions
- [ ] API rate limiting configured
- [ ] CORS configured for production domains only
- [ ] CodeQL security scan passed

## Next Steps

After successful deployment and testing:

1. **Monitor Usage**: Set up monitoring dashboards
2. **User Feedback**: Collect feedback from authorized users
3. **Performance Optimization**: Monitor and optimize slow queries
4. **Backup Strategy**: Configure automated backups
5. **Documentation**: Keep documentation updated with any changes

## Support

For deployment issues:
- Check [Vercel Status](https://www.vercel-status.com/)
- Review [GCP Status](https://status.cloud.google.com/)
- Check application logs in Vercel dashboard
- Review Firestore logs in Cloud Console

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Firestore Documentation](https://cloud.google.com/firestore/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
