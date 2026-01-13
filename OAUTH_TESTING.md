# OAuth Authentication Testing Guide

This document provides step-by-step testing procedures for OAuth/SSO authentication in Poker Therapist.

## Prerequisites

Before testing, ensure you have:

1. ✅ Installed dependencies: `pip install -r requirements.txt`
2. ✅ Configured at least one OAuth provider in `.env.local`
3. ✅ Set up redirect URIs in provider portal(s)

## Test Suite

### 1. Environment Configuration Test

**Purpose**: Verify OAuth configuration is loaded correctly.

**Steps**:

```bash
# Test 1: Check if environment variables are loaded
python -c "
from python_src.services.auth_service import AuthConfig
config = AuthConfig.from_env()
print(f'Microsoft configured: {bool(config.microsoft_client_id)}')
print(f'Google configured: {bool(config.google_client_id)}')
print(f'Apple configured: {bool(config.apple_client_id)}')
print(f'JWT secret: {bool(config.jwt_secret)}')
"
```

**Expected Result**:
- At least one provider should show `True`
- JWT secret should show `True`

---

### 2. Authentication Service Test

**Purpose**: Verify authentication service initialization.

**Steps**:

```bash
# Test 2: Initialize authentication service
python -c "
from python_src.services.auth_service import AuthenticationService
auth = AuthenticationService()
providers = auth.get_available_providers()
print(f'Available providers: {providers}')
print(f'Number of providers: {len(providers)}')
"
```

**Expected Result**:
- Should list configured providers (e.g., `['microsoft', 'google']`)
- No exceptions should be raised

---

### 3. Microsoft OAuth Flow Test

**Prerequisites**: Microsoft Azure AD configured

**Steps**:

```bash
# Test 3a: Generate Microsoft authorization URL
python -c "
from python_src.services.auth_service import AuthenticationService
auth = AuthenticationService()
if auth.microsoft:
    url, state = auth.microsoft.get_authorization_url()
    print(f'Auth URL: {url}')
    print(f'State: {state}')
    print(f'\\nOpen this URL in your browser to test:')
    print(url)
else:
    print('Microsoft not configured')
"
```

**Manual Test**:
1. Copy the generated URL
2. Open in browser
3. Sign in with Microsoft account
4. Grant permissions
5. Note the authorization code in redirect URL

**Test 3b: Verify callback URL format**
- Redirect URL should be: `http://localhost:8501/?code=...&state=...`

---

### 4. Google OAuth Flow Test

**Prerequisites**: Google OAuth configured

**Steps**:

```bash
# Test 4a: Generate Google authorization URL
python -c "
from python_src.services.auth_service import AuthenticationService
auth = AuthenticationService()
if auth.google:
    url, state = auth.google.get_authorization_url()
    print(f'Auth URL: {url}')
    print(f'State: {state}')
    print(f'\\nOpen this URL in your browser to test:')
    print(url)
else:
    print('Google not configured')
"
```

**Manual Test**:
1. Copy the generated URL
2. Open in browser
3. Sign in with Google account
4. Grant permissions
5. Note the authorization code in redirect URL

---

### 5. JWT Token Generation Test

**Purpose**: Verify JWT token creation and validation.

**Steps**:

```bash
# Test 5: Create and verify JWT token
python -c "
from python_src.services.auth_service import AuthenticationService, UserInfo

auth = AuthenticationService()

# Create a test user
user = UserInfo(
    provider='test',
    email='test@example.com',
    name='Test User',
    user_id='12345'
)

# Create token
token = auth.create_session_token(user)
print(f'Generated token: {token[:50]}...')

# Verify token
payload = auth.verify_session_token(token)
if payload:
    print(f'Token valid!')
    print(f'Email: {payload[\"email\"]}')
    print(f'Provider: {payload[\"provider\"]}')
else:
    print('Token validation failed!')
"
```

**Expected Result**:
- Token should be generated successfully
- Token should validate successfully
- Email and provider should match

---

### 6. Streamlit Integration Test

**Purpose**: Test OAuth authentication in Streamlit application.

**Steps**:

```bash
# Start Streamlit app
streamlit run chatbot_app.py
```

**Manual Test Checklist**:

1. ✅ App loads without errors
2. ✅ Sidebar shows "Account Login" section
3. ✅ OAuth login buttons appear (if configured)
4. ✅ Click "Sign in with Microsoft" (or Google)
5. ✅ Redirected to provider login page
6. ✅ Complete authentication
7. ✅ Redirected back to app
8. ✅ User profile shows in sidebar
9. ✅ VIP badge shows (if authorized email)
10. ✅ Chat functionality works with OAuth user

**Screenshot Test**:
- Take screenshot of successful login
- Take screenshot of user profile display

---

### 7. FastAPI Backend Test

**Purpose**: Test OAuth authentication in FastAPI backend.

**Steps**:

```bash
# Start FastAPI server
cd backend
uvicorn api.main:app --reload
```

**Test 7a: Health Check**

```bash
curl http://localhost:8000/api/auth/health
```

**Expected Response**:
```json
{
  "oauth_enabled": true,
  "jwt_configured": true,
  "auth_required": false
}
```

**Test 7b: Optional Auth Endpoint**

```bash
# Without auth
curl http://localhost:8000/api/auth/test-optional

# Expected: {"status": "guest", "email": null, "provider": null}
```

**Test 7c: Required Auth Endpoint**

First, get a JWT token from the Streamlit app (check browser dev tools or session state).

```bash
# With JWT token
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/auth/me
```

**Expected Response**:
```json
{
  "email": "user@example.com",
  "name": "User Name",
  "provider": "microsoft",
  "is_authorized": true,
  "is_vip": true
}
```

**Test 7d: VIP Check**

```bash
# With JWT token from authorized user
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/auth/vip-check
```

**Expected Response** (if VIP):
```json
{
  "message": "VIP access confirmed for user@example.com",
  "status": "vip"
}
```

**Expected Response** (if not VIP):
```json
{
  "detail": "VIP access required"
}
```

---

### 8. Error Handling Tests

**Purpose**: Verify error handling for invalid credentials.

**Test 8a: Invalid JWT Token**

```bash
curl -H "Authorization: Bearer invalid_token" \
     http://localhost:8000/api/auth/me
```

**Expected**: 401 Unauthorized

**Test 8b: Expired Token**

Create a token with very short expiration:

```python
from python_src.services.auth_service import AuthenticationService, UserInfo, AuthConfig
from datetime import datetime, timedelta

config = AuthConfig.from_env()
config.session_timeout_minutes = 0  # Immediate expiry

auth = AuthenticationService(config)
user = UserInfo(provider='test', email='test@example.com')
token = auth.create_session_token(user)

# Wait a moment, then verify
import time
time.sleep(2)
result = auth.verify_session_token(token)
print(f"Expected None, got: {result}")
```

**Expected**: `None` or expiration error

**Test 8c: Missing State Parameter**

In Streamlit app, manually set query params without state:

```python
st.query_params = {"code": "test_code"}
```

**Expected**: Error message about invalid state

---

### 9. Production Readiness Test

**Purpose**: Verify configuration for production deployment.

**Checklist**:

- [ ] HTTPS redirect URIs configured in provider portals
- [ ] Production environment variables set
- [ ] JWT secret key is strong and unique
- [ ] Session timeout is appropriate (default: 60 minutes)
- [ ] CORS origins configured correctly
- [ ] No secrets committed to git
- [ ] `.env.local` is in `.gitignore`
- [ ] Documentation is up to date

**Test Script**:

```bash
# Check for secrets in git
git grep -i "client_secret\|private_key" -- ':!*.example' ':!*.md'

# Should return no results
```

---

## Common Issues and Solutions

### Issue 1: "OAuth provider not configured"

**Cause**: Environment variables not loaded

**Solution**:
1. Check `.env.local` exists
2. Verify variable names match exactly
3. Restart application to reload environment

### Issue 2: "Invalid redirect URI"

**Cause**: Redirect URI mismatch

**Solution**:
1. Check redirect URI in provider portal
2. Ensure it matches exactly (including trailing `/`)
3. For localhost, use `http://localhost:8501/`
4. For production, use HTTPS URL

### Issue 3: "State parameter mismatch"

**Cause**: Session expired or CSRF attack

**Solution**:
1. Clear browser session
2. Try authentication flow again
3. Check if session state is persisting correctly

### Issue 4: Token validation fails in backend

**Cause**: JWT secret key mismatch

**Solution**:
1. Ensure same JWT_SECRET_KEY in both frontend and backend environments
2. Verify environment variables are loaded correctly
3. Restart both services

---

## Integration Testing

### End-to-End Test

**Scenario**: User authenticates and uses the application

1. **Start Services**:
   ```bash
   # Terminal 1: Start Streamlit
   streamlit run chatbot_app.py
   
   # Terminal 2: Start FastAPI
   cd backend && uvicorn api.main:app --reload
   ```

2. **Authenticate**:
   - Open `http://localhost:8501`
   - Click OAuth login button
   - Complete authentication

3. **Use Chat**:
   - Send a message to the chatbot
   - Verify response is received
   - Check conversation history persists

4. **Test API**:
   - Extract JWT token from browser session
   - Make API call with token
   - Verify authenticated response

5. **Test VIP Features**:
   - If authorized email, verify VIP badge shows
   - Test voice features (if enabled)
   - Verify restricted features work

---

## Performance Testing

### Load Test

Test with multiple concurrent users:

```python
import asyncio
import aiohttp

async def test_auth_endpoint(token):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}"}
        async with session.get(
            "http://localhost:8000/api/auth/me",
            headers=headers
        ) as response:
            return response.status

async def main():
    # Generate test token
    from python_src.services.auth_service import AuthenticationService, UserInfo
    auth = AuthenticationService()
    user = UserInfo(provider='test', email='test@example.com')
    token = auth.create_session_token(user)
    
    # Test with 100 concurrent requests
    tasks = [test_auth_endpoint(token) for _ in range(100)]
    results = await asyncio.gather(*tasks)
    
    success = sum(1 for r in results if r == 200)
    print(f"Success rate: {success}/100")

asyncio.run(main())
```

---

## Automated Testing

### Unit Tests

Create `tests/test_auth.py`:

```python
import pytest
from python_src.services.auth_service import (
    AuthenticationService,
    AuthConfig,
    UserInfo,
)

def test_auth_config_from_env():
    """Test authentication configuration loading."""
    config = AuthConfig.from_env()
    assert config.jwt_algorithm == "HS256"
    assert config.session_timeout_minutes > 0

def test_create_session_token():
    """Test JWT token creation."""
    auth = AuthenticationService()
    user = UserInfo(
        provider="test",
        email="test@example.com",
        name="Test User",
    )
    
    token = auth.create_session_token(user)
    assert isinstance(token, str)
    assert len(token) > 0

def test_verify_session_token():
    """Test JWT token verification."""
    auth = AuthenticationService()
    user = UserInfo(
        provider="test",
        email="test@example.com",
    )
    
    token = auth.create_session_token(user)
    payload = auth.verify_session_token(token)
    
    assert payload is not None
    assert payload["email"] == "test@example.com"
    assert payload["provider"] == "test"

def test_invalid_token():
    """Test invalid token handling."""
    auth = AuthenticationService()
    payload = auth.verify_session_token("invalid_token")
    assert payload is None
```

Run tests:

```bash
pytest tests/test_auth.py -v
```

---

## Success Criteria

The OAuth authentication is ready for production when:

- ✅ All unit tests pass
- ✅ Manual integration tests complete successfully
- ✅ No secrets in git repository
- ✅ Production environment variables configured
- ✅ HTTPS redirect URIs registered
- ✅ Documentation complete and reviewed
- ✅ Security checklist completed
- ✅ End-to-end test successful

---

## Support

For issues during testing:

1. Check this testing guide
2. Review [OAUTH_SETUP.md](OAUTH_SETUP.md)
3. Check [OAUTH_QUICKSTART.md](OAUTH_QUICKSTART.md)
4. Open GitHub issue with test results
