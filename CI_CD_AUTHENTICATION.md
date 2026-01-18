# CI/CD Authentication Configuration Guide

This guide explains how to configure authentication credentials for automated CI/CD workflows, container deployments, and serverless platforms.

## Overview

The Poker Therapist application requires proper authentication configuration in CI/CD pipelines to:
- Run automated tests with authentication
- Deploy to cloud platforms (Vercel, Google Cloud Platform, Azure)
- Access Google Cloud Storage for data persistence
- Validate OAuth flows in staging/production environments

## Security Principles

⚠️ **CRITICAL SECURITY REQUIREMENTS**:

1. **NEVER commit credentials to source control**
   - No API keys, secrets, or tokens in code
   - Use environment variables or secret managers
   - Keep `.env.local` and credential files in `.gitignore`

2. **Use separate credentials per environment**
   - Development: Local `.env.local` file
   - Staging: Staging-specific secrets
   - Production: Production-only credentials

3. **Rotate credentials regularly**
   - Azure client secrets: Every 12-24 months
   - Service account keys: Annually
   - JWT secrets: Periodically
   - Immediately rotate if compromised

4. **Apply principle of least privilege**
   - Grant minimum permissions needed
   - Use service accounts for automation
   - Restrict API access by IP when possible

## GitHub Actions Configuration

### Step 1: Add Repository Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

#### Authentication Secrets
```
JWT_SECRET_KEY
  Value: Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"

AUTHORIZED_EMAILS
  Value: m.fanelli1@icloud.com,maurofanellijr@gmail.com,mauro.fanelli@ctstate.edu,johndawalka@icloud.com,cooljack87@icloud.com,jdwalka@pm.me
```

#### Microsoft Azure AD Secrets
```
AZURE_TENANT_ID
  Value: Your Azure tenant ID from portal

AZURE_CLIENT_ID
  Value: Your Azure application (client) ID

AZURE_CLIENT_SECRET
  Value: Your Azure client secret (from Certificates & secrets)

AZURE_AUTHORITY
  Value: https://login.microsoftonline.com/common

INSTITUTIONAL_EMAIL_DOMAIN
  Value: ctstate.edu
```

#### Google Cloud Platform Secrets
```
GOOGLE_CLOUD_PROJECT_ID
  Value: Your GCP project ID

GOOGLE_CLIENT_ID
  Value: Your OAuth 2.0 client ID

GOOGLE_CLIENT_SECRET
  Value: Your OAuth 2.0 client secret

GOOGLE_STORAGE_BUCKET_NAME
  Value: poker-therapist-data-{unique-suffix}

GOOGLE_APPLICATION_CREDENTIALS_JSON
  Value: Entire contents of service account JSON file (paste as single line)
```

#### Apple Developer Secrets
```
APPLE_TEAM_ID
  Value: Your 10-character team ID

APPLE_SERVICES_ID
  Value: com.therapyrex.signin

APPLE_KEY_ID
  Value: Your Apple key ID

APPLE_PRIVATE_KEY
  Value: Entire contents of .p8 file (including BEGIN/END lines)
```

#### API Keys
```
OPENAI_API_KEY
  Value: Your OpenAI API key for chatbot

XAI_API_KEY
  Value: Your xAI/Grok API key (optional)

ANTHROPIC_API_KEY
  Value: Your Anthropic/Claude API key (optional)

GOOGLE_AI_API_KEY
  Value: Your Google AI/Gemini API key (optional)

PERPLEXITY_API_KEY
  Value: Your Perplexity API key (optional)
```

### Step 2: Create GitHub Actions Workflow

Create `.github/workflows/test-auth.yml`:

```yaml
name: Test Authentication

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-auth:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Create Google service account credentials
      run: |
        mkdir -p config
        echo '${{ secrets.GOOGLE_APPLICATION_CREDENTIALS_JSON }}' > config/google-service-account.json
    
    - name: Create Apple private key
      run: |
        mkdir -p config
        echo '${{ secrets.APPLE_PRIVATE_KEY }}' > config/apple-auth-key.p8
    
    - name: Run authentication tests
      env:
        # JWT Configuration
        JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}
        
        # Authorized emails
        AUTHORIZED_EMAILS: ${{ secrets.AUTHORIZED_EMAILS }}
        
        # Microsoft Azure AD
        AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
        AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
        AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
        AZURE_AUTHORITY: ${{ secrets.AZURE_AUTHORITY }}
        INSTITUTIONAL_EMAIL_DOMAIN: ${{ secrets.INSTITUTIONAL_EMAIL_DOMAIN }}
        
        # Google Cloud Platform
        GOOGLE_CLOUD_PROJECT_ID: ${{ secrets.GOOGLE_CLOUD_PROJECT_ID }}
        GOOGLE_CLIENT_ID: ${{ secrets.GOOGLE_CLIENT_ID }}
        GOOGLE_CLIENT_SECRET: ${{ secrets.GOOGLE_CLIENT_SECRET }}
        GOOGLE_STORAGE_BUCKET_NAME: ${{ secrets.GOOGLE_STORAGE_BUCKET_NAME }}
        GOOGLE_APPLICATION_CREDENTIALS: ./config/google-service-account.json
        
        # Apple Sign-In
        APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
        APPLE_SERVICES_ID: ${{ secrets.APPLE_SERVICES_ID }}
        APPLE_KEY_ID: ${{ secrets.APPLE_KEY_ID }}
        APPLE_PRIVATE_KEY_PATH: ./config/apple-auth-key.p8
        
        # API Keys
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        python tests/test_email_validation.py
        # Add more authentication tests here
    
    - name: Clean up credentials
      if: always()
      run: |
        rm -f config/google-service-account.json
        rm -f config/apple-auth-key.p8
```

## Vercel Deployment

### Step 1: Configure Environment Variables

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Navigate to **Settings** → **Environment Variables**
4. Add variables for each environment (Production, Preview, Development)

#### Required Variables
```bash
# JWT
JWT_SECRET_KEY=<generate-new-secret>

# Authorized emails
AUTHORIZED_EMAILS=m.fanelli1@icloud.com,maurofanellijr@gmail.com,mauro.fanelli@ctstate.edu

# Microsoft Azure
AZURE_TENANT_ID=<your-tenant-id>
AZURE_CLIENT_ID=<your-client-id>
AZURE_CLIENT_SECRET=<your-client-secret>
AZURE_AUTHORITY=https://login.microsoftonline.com/common

# Google Cloud
GOOGLE_CLOUD_PROJECT_ID=<your-project-id>
GOOGLE_CLIENT_ID=<your-client-id>
GOOGLE_CLIENT_SECRET=<your-client-secret>
GOOGLE_STORAGE_BUCKET_NAME=<your-bucket-name>
GOOGLE_APPLICATION_CREDENTIALS_JSON=<paste-json-content>

# Apple
APPLE_TEAM_ID=<your-team-id>
APPLE_SERVICES_ID=com.therapyrex.signin
APPLE_KEY_ID=<your-key-id>
APPLE_PRIVATE_KEY=<paste-key-content>

# API Keys
OPENAI_API_KEY=<your-key>
```

### Step 2: Update Vercel Configuration

Create or update `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "chatbot_app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "chatbot_app.py"
    }
  ],
  "env": {
    "ENABLE_MICROSOFT_AUTH": "true",
    "ENABLE_GOOGLE_AUTH": "true",
    "ENABLE_APPLE_AUTH": "true",
    "DEFAULT_AUTH_PROVIDER": "microsoft",
    "REQUIRE_AUTHENTICATION": "true"
  }
}
```

### Step 3: Create Build Hook

For handling credential files during build:

Create `.vercel/build.sh`:

```bash
#!/bin/bash
set -e

echo "Setting up authentication credentials..."

# Create config directory
mkdir -p config

# Create Google service account credentials from environment variable
if [ ! -z "$GOOGLE_APPLICATION_CREDENTIALS_JSON" ]; then
    echo "$GOOGLE_APPLICATION_CREDENTIALS_JSON" > config/google-service-account.json
    export GOOGLE_APPLICATION_CREDENTIALS=./config/google-service-account.json
    echo "✅ Google service account configured"
fi

# Create Apple private key from environment variable
if [ ! -z "$APPLE_PRIVATE_KEY" ]; then
    echo "$APPLE_PRIVATE_KEY" > config/apple-auth-key.p8
    export APPLE_PRIVATE_KEY_PATH=./config/apple-auth-key.p8
    echo "✅ Apple private key configured"
fi

echo "Authentication setup complete"
```

Make it executable:
```bash
chmod +x .vercel/build.sh
```

## Google Cloud Platform Deployment

### Step 1: Set up Secret Manager

```bash
# Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Create secrets
gcloud secrets create jwt-secret-key --data-file=- <<< "your-jwt-secret"
gcloud secrets create azure-client-secret --data-file=- <<< "your-azure-secret"
gcloud secrets create google-service-account --data-file=config/google-service-account.json
gcloud secrets create apple-private-key --data-file=config/apple-auth-key.p8

# Grant access to Cloud Run service account
gcloud secrets add-iam-policy-binding jwt-secret-key \
    --member="serviceAccount:YOUR-SERVICE-ACCOUNT@PROJECT.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### Step 2: Deploy to Cloud Run

```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT-ID/poker-therapist

# Deploy with secrets
gcloud run deploy poker-therapist \
    --image gcr.io/PROJECT-ID/poker-therapist \
    --platform managed \
    --region us-central1 \
    --set-secrets="JWT_SECRET_KEY=jwt-secret-key:latest,AZURE_CLIENT_SECRET=azure-client-secret:latest" \
    --set-env-vars="AZURE_TENANT_ID=your-tenant,AZURE_CLIENT_ID=your-client,AUTHORIZED_EMAILS=m.fanelli1@icloud.com,maurofanellijr@gmail.com"
```

### Step 3: Create Cloud Build Configuration

Create `cloudbuild.yaml`:

```yaml
steps:
  # Build the container
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/poker-therapist', '.']
  
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/poker-therapist']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'poker-therapist'
      - '--image=gcr.io/$PROJECT_ID/poker-therapist'
      - '--region=us-central1'
      - '--platform=managed'
      - '--set-secrets=JWT_SECRET_KEY=jwt-secret-key:latest'

images:
  - 'gcr.io/$PROJECT_ID/poker-therapist'
```

## Docker Container Deployment

### Step 1: Create Docker Secrets

```bash
# Create Docker secrets
echo "your-jwt-secret" | docker secret create jwt_secret_key -
echo "your-azure-secret" | docker secret create azure_client_secret -

# Run container with secrets
docker run -d \
  --name poker-therapist \
  --secret jwt_secret_key \
  --secret azure_client_secret \
  -e AZURE_TENANT_ID=your-tenant \
  -e AZURE_CLIENT_ID=your-client \
  -e AUTHORIZED_EMAILS=m.fanelli1@icloud.com,maurofanellijr@gmail.com \
  poker-therapist:latest
```

### Step 2: Docker Compose with Secrets

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  poker-therapist:
    build: .
    ports:
      - "8501:8501"
    secrets:
      - jwt_secret_key
      - azure_client_secret
      - google_service_account
      - apple_private_key
    environment:
      - JWT_SECRET_KEY_FILE=/run/secrets/jwt_secret_key
      - AZURE_TENANT_ID=${AZURE_TENANT_ID}
      - AZURE_CLIENT_ID=${AZURE_CLIENT_ID}
      - AZURE_CLIENT_SECRET_FILE=/run/secrets/azure_client_secret
      - AUTHORIZED_EMAILS=${AUTHORIZED_EMAILS}
      - GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/google_service_account
      - APPLE_PRIVATE_KEY_PATH=/run/secrets/apple_private_key

secrets:
  jwt_secret_key:
    file: ./secrets/jwt_secret_key.txt
  azure_client_secret:
    file: ./secrets/azure_client_secret.txt
  google_service_account:
    file: ./config/google-service-account.json
  apple_private_key:
    file: ./config/apple-auth-key.p8
```

## Azure DevOps Pipeline

Create `azure-pipelines.yml`:

```yaml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  - group: poker-therapist-secrets

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'

- script: |
    pip install -r requirements.txt
  displayName: 'Install dependencies'

- script: |
    mkdir -p config
    echo "$(GOOGLE_SERVICE_ACCOUNT_JSON)" > config/google-service-account.json
    echo "$(APPLE_PRIVATE_KEY)" > config/apple-auth-key.p8
  displayName: 'Setup credentials'

- script: |
    python tests/test_email_validation.py
  displayName: 'Run tests'
  env:
    JWT_SECRET_KEY: $(JWT_SECRET_KEY)
    AUTHORIZED_EMAILS: $(AUTHORIZED_EMAILS)
    AZURE_TENANT_ID: $(AZURE_TENANT_ID)
    AZURE_CLIENT_ID: $(AZURE_CLIENT_ID)
    AZURE_CLIENT_SECRET: $(AZURE_CLIENT_SECRET)
    GOOGLE_APPLICATION_CREDENTIALS: ./config/google-service-account.json

- script: |
    rm -f config/google-service-account.json
    rm -f config/apple-auth-key.p8
  displayName: 'Cleanup credentials'
  condition: always()
```

## Kubernetes Deployment

### Step 1: Create Kubernetes Secrets

```bash
# Create namespace
kubectl create namespace poker-therapist

# Create secrets
kubectl create secret generic poker-therapist-auth \
  --from-literal=jwt-secret-key="your-jwt-secret" \
  --from-literal=azure-client-secret="your-azure-secret" \
  --from-file=google-service-account=./config/google-service-account.json \
  --from-file=apple-private-key=./config/apple-auth-key.p8 \
  -n poker-therapist

# Create ConfigMap for non-sensitive config
kubectl create configmap poker-therapist-config \
  --from-literal=azure-tenant-id="your-tenant" \
  --from-literal=azure-client-id="your-client" \
  --from-literal=authorized-emails="m.fanelli1@icloud.com,maurofanellijr@gmail.com" \
  -n poker-therapist
```

### Step 2: Create Deployment

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: poker-therapist
  namespace: poker-therapist
spec:
  replicas: 3
  selector:
    matchLabels:
      app: poker-therapist
  template:
    metadata:
      labels:
        app: poker-therapist
    spec:
      containers:
      - name: poker-therapist
        image: gcr.io/PROJECT-ID/poker-therapist:latest
        ports:
        - containerPort: 8501
        env:
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: poker-therapist-auth
              key: jwt-secret-key
        - name: AZURE_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: poker-therapist-auth
              key: azure-client-secret
        - name: AZURE_TENANT_ID
          valueFrom:
            configMapKeyRef:
              name: poker-therapist-config
              key: azure-tenant-id
        - name: AUTHORIZED_EMAILS
          valueFrom:
            configMapKeyRef:
              name: poker-therapist-config
              key: authorized-emails
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: /var/secrets/google/google-service-account.json
        - name: APPLE_PRIVATE_KEY_PATH
          value: /var/secrets/apple/apple-auth-key.p8
        volumeMounts:
        - name: google-credentials
          mountPath: /var/secrets/google
          readOnly: true
        - name: apple-credentials
          mountPath: /var/secrets/apple
          readOnly: true
      volumes:
      - name: google-credentials
        secret:
          secretName: poker-therapist-auth
          items:
          - key: google-service-account
            path: google-service-account.json
      - name: apple-credentials
        secret:
          secretName: poker-therapist-auth
          items:
          - key: apple-private-key
            path: apple-auth-key.p8
```

## Testing Automated Authentication

### Test 1: Verify Secret Injection

```bash
# For Kubernetes
kubectl exec -it deployment/poker-therapist -n poker-therapist -- env | grep JWT

# For Docker
docker exec poker-therapist env | grep JWT

# For Cloud Run
gcloud run services describe poker-therapist --format="value(spec.template.spec.containers[0].env)"
```

### Test 2: Test Authentication Endpoints

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe poker-therapist --format="value(status.url)")

# Test Microsoft OAuth
curl "$SERVICE_URL/auth/microsoft/authorize"

# Test Google OAuth
curl "$SERVICE_URL/auth/google/authorize"
```

### Test 3: Verify Authorized Emails

Create test script `test-auth-ci.py`:

```python
import os
import sys

# Check authorized emails are loaded
authorized = os.getenv("AUTHORIZED_EMAILS", "").split(",")
required_emails = [
    "m.fanelli1@icloud.com",
    "maurofanellijr@gmail.com",
    "mauro.fanelli@ctstate.edu",
]

print("Checking authorized emails...")
for email in required_emails:
    if email in authorized:
        print(f"✅ {email} is authorized")
    else:
        print(f"❌ {email} is NOT authorized")
        sys.exit(1)

print("\n✅ All required emails are authorized!")
```

## Security Audit Checklist

Before deploying to production:

- [ ] All secrets stored in secret manager (not environment variables)
- [ ] No credentials in source code or version control
- [ ] Separate credentials for dev/staging/production
- [ ] JWT secret is strong random string (32+ characters)
- [ ] Azure client secret rotated within last 12 months
- [ ] Google service account key rotated within last 12 months
- [ ] HTTPS enforced in production (`FORCE_HTTPS=true`)
- [ ] CORS configured for specific origins (no wildcard `*`)
- [ ] Rate limiting enabled
- [ ] All OAuth redirect URIs match exactly
- [ ] Service accounts have minimum required permissions
- [ ] Logs don't contain sensitive information
- [ ] Secret access audited regularly
- [ ] Incident response plan in place

## Troubleshooting

### "Secret not found" in CI/CD
- **Cause**: Secret not configured in platform
- **Solution**: Add secret in GitHub Actions, Vercel, or cloud platform settings

### "Permission denied" accessing secrets
- **Cause**: Service account lacks secret accessor role
- **Solution**: Grant `roles/secretmanager.secretAccessor` role

### "Invalid credentials" in deployment
- **Cause**: Credentials formatted incorrectly or expired
- **Solution**: 
  - Check JSON formatting (no extra spaces/newlines)
  - Verify credentials are current and not expired
  - Rotate credentials if compromised

### "OAuth redirect_uri mismatch" in production
- **Cause**: Production URL not added to OAuth providers
- **Solution**: Add production URL to Azure portal, Google Cloud Console, Apple Developer portal

## Support

For deployment-specific issues:
- GitHub Actions: https://docs.github.com/en/actions
- Vercel: https://vercel.com/docs
- Google Cloud: https://cloud.google.com/docs
- Azure DevOps: https://docs.microsoft.com/azure/devops

For authentication issues, refer to `AUTHENTICATION_VERIFICATION.md`.

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-18  
**Purpose**: CI/CD authentication configuration for Poker Therapist
