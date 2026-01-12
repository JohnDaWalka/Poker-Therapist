# n8n Integration Setup Guide

This guide will help you set up n8n workflow automation for Poker Therapist.

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Importing Workflows](#importing-workflows)
4. [Testing](#testing)
5. [Deployment](#deployment)
6. [Troubleshooting](#troubleshooting)

## Installation

### Option 1: Docker (Recommended)

```bash
# Pull the n8n Docker image
docker pull n8nio/n8n

# Run n8n with persistent data
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=your-secure-password \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### Option 2: npm

```bash
# Install n8n globally
npm install n8n -g

# Start n8n
n8n start
```

### Option 3: Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your-secure-password
      - WEBHOOK_URL=https://your-domain.com/
      - GENERIC_TIMEZONE=America/New_York
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

Then run:
```bash
docker-compose up -d
```

## Configuration

### 1. Access n8n

Open your browser and navigate to:
- Local: `http://localhost:5678`
- Production: `https://your-n8n-domain.com`

### 2. Set Up Credentials

#### Poker Therapist API Credentials

1. Go to **Credentials** → **New**
2. Select **Header Auth**
3. Configure:
   - **Name**: `Poker Therapist API`
   - **Header Name**: `Authorization`
   - **Header Value**: `Bearer YOUR_API_KEY` (if using API keys)
   
   Or leave empty if no authentication is required for webhooks.

#### Email Credentials (for notifications)

1. Go to **Credentials** → **New**
2. Select **SMTP**
3. Configure:
   - **Host**: Your SMTP server (e.g., `smtp.gmail.com`)
   - **Port**: `587` (for TLS)
   - **User**: Your email address
   - **Password**: Your email password or app-specific password

#### Slack Credentials (optional)

1. Go to **Credentials** → **New**
2. Select **Slack**
3. Follow OAuth flow or use webhook URL

#### Discord Credentials (optional)

1. Go to **Credentials** → **New**
2. Select **Discord**
3. Enter webhook URL from Discord settings

#### Twilio Credentials (optional - for SMS)

1. Go to **Credentials** → **New**
2. Select **Twilio**
3. Enter:
   - Account SID
   - Auth Token

### 3. Set Up Environment Variables

In n8n settings or your environment:

```bash
# Poker Therapist API
API_BASE_URL=http://localhost:8000

# If Poker Therapist is on a different server
# API_BASE_URL=https://your-api-domain.com

# Google Sheets (if using sheets integration)
GOOGLE_SHEET_ID=your-sheet-id
```

## Importing Workflows

### Method 1: Import from File

1. In n8n, click **Workflows** → **Import from File**
2. Navigate to `/n8n-workflows/` directory
3. Select a workflow JSON file:
   - `poker-hand-analysis.json`
   - `tilt-detection-alert.json`
   - `daily-coaching-report.json`
   - `ai-coach-discord-bot.json`
4. Click **Import**

### Method 2: Import from URL

1. Copy the workflow JSON content
2. In n8n, click **Workflows** → **Import from URL**
3. Paste the raw GitHub URL of the workflow JSON
4. Click **Import**

### Method 3: Copy and Paste

1. Open the workflow JSON file
2. Copy the entire content
3. In n8n, click **Workflows** → **Import from String**
4. Paste the JSON content
5. Click **Import**

## Configuring Imported Workflows

After importing, you need to configure each workflow:

### 1. Poker Hand Analysis Workflow

1. Open the workflow
2. Click on the **"Call Poker Therapist API"** node
3. Update the URL to your API endpoint
4. Select your authentication credentials
5. Click **"Send Success Email"** node
6. Configure your email credentials
7. Click **Save** and **Activate**

### 2. Tilt Detection Alert Workflow

1. Open the workflow
2. Click on **"Check Tilt Status"** node
3. Update the API URL
4. Configure the schedule trigger (default: every 15 minutes)
5. Set up email, Slack, and SMS nodes with your credentials
6. Click **Save** and **Activate**

### 3. Daily Coaching Report Workflow

1. Open the workflow
2. Update the schedule (default: 8 PM daily)
3. Configure API endpoint
4. Set up email template
5. (Optional) Configure Google Sheets integration
6. Click **Save** and **Activate**

### 4. AI Coach Discord Bot Workflow

1. Open the workflow
2. Click on **"Discord Webhook"** node
3. Copy the webhook URL
4. Go to Discord → Server Settings → Integrations → Webhooks
5. Create a new webhook and paste the n8n URL
6. Back in n8n, configure the **"Send Discord Response"** node
7. Click **Save** and **Activate**

## Testing

### Test Webhook Endpoint

```bash
# Test the connection
curl -X POST http://localhost:8000/api/webhooks/n8n/test

# Expected response:
# {"success": true, "message": "n8n webhook integration is working", ...}
```

### Test Poker Hand Analysis

```bash
curl -X POST http://localhost:5678/webhook/poker-hand-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "email": "test@example.com",
    "hand_data": {
      "position": "BTN",
      "cards": ["As", "Kd"],
      "action": "raise"
    }
  }'
```

### Test in n8n

1. Open a workflow
2. Click **"Execute Workflow"** button
3. Check the execution log
4. Verify each node executed successfully
5. Check output data

## Deployment

### Production Best Practices

#### 1. Use HTTPS

```bash
# Docker with Caddy reverse proxy
docker run -d \
  --name caddy \
  -p 80:80 -p 443:443 \
  -v caddy_data:/data \
  -v ./Caddyfile:/etc/caddy/Caddyfile \
  caddy
```

Caddyfile:
```
n8n.yourdomain.com {
    reverse_proxy n8n:5678
}
```

#### 2. Enable Authentication

Always use basic auth or OAuth in production:

```bash
-e N8N_BASIC_AUTH_ACTIVE=true \
-e N8N_BASIC_AUTH_USER=admin \
-e N8N_BASIC_AUTH_PASSWORD=strong-password
```

#### 3. Set Up Database (PostgreSQL)

For production, use PostgreSQL instead of SQLite:

```bash
-e DB_TYPE=postgresdb \
-e DB_POSTGRESDB_HOST=postgres \
-e DB_POSTGRESDB_PORT=5432 \
-e DB_POSTGRESDB_DATABASE=n8n \
-e DB_POSTGRESDB_USER=n8n \
-e DB_POSTGRESDB_PASSWORD=your-password
```

#### 4. Configure Webhooks

```bash
-e WEBHOOK_URL=https://n8n.yourdomain.com/
```

#### 5. Set Timezone

```bash
-e GENERIC_TIMEZONE=America/New_York
```

### Scaling n8n

For high-volume workflows:

1. **Queue Mode**: Use Redis for job queue
   ```bash
   -e EXECUTIONS_MODE=queue
   -e QUEUE_BULL_REDIS_HOST=redis
   ```

2. **Multiple Workers**: Run multiple n8n worker instances

3. **Monitoring**: Set up monitoring with Prometheus/Grafana

## Troubleshooting

### Workflow Not Executing

**Problem**: Workflow doesn't trigger automatically

**Solutions**:
1. Check if workflow is **Activated** (toggle should be blue)
2. Verify trigger node configuration
3. Check n8n logs: `docker logs n8n`
4. Test trigger manually with **Execute Workflow**

### Webhook Not Receiving Data

**Problem**: Webhook trigger not receiving data

**Solutions**:
1. Verify webhook URL is correct
2. Check firewall settings
3. Test with curl:
   ```bash
   curl -X POST https://n8n.yourdomain.com/webhook/test \
     -H "Content-Type: application/json" \
     -d '{"test": "data"}'
   ```
4. Check n8n execution log

### API Connection Errors

**Problem**: Cannot connect to Poker Therapist API

**Solutions**:
1. Verify `API_BASE_URL` is correct
2. Check if API is running: `curl http://localhost:8000/health`
3. Verify network connectivity between n8n and API
4. Check authentication credentials
5. Review API logs for errors

### Email Not Sending

**Problem**: Email nodes failing to send

**Solutions**:
1. Verify SMTP credentials
2. Check email provider settings (some require app passwords)
3. Test with a simple email workflow
4. Enable "Allow less secure apps" if using Gmail (or use app password)

### Schedule Not Triggering

**Problem**: Scheduled workflows not running

**Solutions**:
1. Verify cron expression is correct
2. Check timezone settings: `GENERIC_TIMEZONE`
3. Ensure n8n container/process is running continuously
4. Check system time is synchronized

### Database Errors

**Problem**: Database connection or migration errors

**Solutions**:
1. Check database credentials
2. Verify database is accessible
3. Check n8n logs for specific error messages
4. Try resetting database (caution: data loss)

### Memory Issues

**Problem**: n8n running out of memory

**Solutions**:
1. Increase container memory limit
2. Optimize workflows (reduce data processing)
3. Use queue mode for heavy workflows
4. Enable execution data pruning

## Advanced Configuration

### Custom Nodes

Install custom n8n nodes:

```bash
cd ~/.n8n
npm install n8n-nodes-custom-package
n8n restart
```

### Environment Variables

Full list of useful environment variables:

```bash
# Execution
EXECUTIONS_TIMEOUT=3600
EXECUTIONS_TIMEOUT_MAX=7200
EXECUTIONS_DATA_SAVE_ON_ERROR=all
EXECUTIONS_DATA_SAVE_ON_SUCCESS=all

# Security
N8N_JWT_AUTH_ACTIVE=true
N8N_JWT_AUTH_HEADER=Authorization
N8N_JWT_AUTH_HEADER_VALUE_PREFIX=Bearer

# Performance
N8N_PAYLOAD_SIZE_MAX=64
N8N_METRICS=true

# Logging
N8N_LOG_LEVEL=info
N8N_LOG_OUTPUT=console,file
```

### Backup and Restore

#### Backup Workflows

```bash
# Export all workflows
docker exec n8n n8n export:workflow --backup --output=/backup/

# Copy from container
docker cp n8n:/backup ./n8n-backup
```

#### Restore Workflows

```bash
# Copy to container
docker cp ./n8n-backup n8n:/restore/

# Import workflows
docker exec n8n n8n import:workflow --input=/restore/
```

## Security Checklist

- [ ] Enable HTTPS in production
- [ ] Set strong admin password
- [ ] Use API authentication
- [ ] Whitelist webhook IPs if possible
- [ ] Enable rate limiting
- [ ] Regular backups
- [ ] Monitor execution logs
- [ ] Rotate API keys regularly
- [ ] Use environment variables for secrets
- [ ] Keep n8n updated

## Next Steps

1. ✅ Install and configure n8n
2. ✅ Import workflow templates
3. ✅ Set up credentials
4. ✅ Test workflows
5. ✅ Deploy to production
6. 📚 Explore [n8n documentation](https://docs.n8n.io/)
7. 🎯 Create custom workflows
8. 🔄 Automate your poker coaching

## Support and Resources

- [n8n Documentation](https://docs.n8n.io/)
- [n8n Community Forum](https://community.n8n.io/)
- [n8n Workflow Templates](https://n8n.io/workflows/)
- [Poker Therapist GitHub](https://github.com/JohnDaWalka/Poker-Therapist)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

For issues specific to Poker Therapist integration, please open an issue on GitHub.
