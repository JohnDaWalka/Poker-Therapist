# n8n Quick Start for Poker Therapist

Get up and running with n8n workflow automation in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- Poker Therapist API running (or accessible)

## Quick Start Steps

### 1. Start n8n with Docker Compose

```bash
# From the Poker-Therapist root directory
docker-compose -f docker-compose.n8n.yml up -d
```

This will:
- Start n8n on port 5678
- Create persistent storage for workflows
- Configure n8n to connect to your local API

### 2. Access n8n

Open your browser to: http://localhost:5678

**Default Credentials:**
- Username: `admin`
- Password: `changeme123`

⚠️ **Important**: Change the password in `docker-compose.n8n.yml` before production use!

### 3. Import a Workflow

1. Click **"Workflows"** in the left sidebar
2. Click **"Import from File"**
3. Select one of these files from `n8n-workflows/`:
   - `poker-hand-analysis.json` - Automate hand analysis
   - `tilt-detection-alert.json` - Monitor for tilt
   - `daily-coaching-report.json` - Daily reports
   - `ai-coach-discord-bot.json` - Discord bot integration

### 4. Configure the Workflow

1. Open the imported workflow
2. Click on the **HTTP Request** node
3. Verify the URL points to: `http://host.docker.internal:8000/api/webhooks/n8n`
4. Click **"Save"**

### 5. Test the Workflow

Click the **"Execute Workflow"** button to test it.

### 6. Activate the Workflow

Toggle the **"Active"** switch in the top right to enable automatic execution.

## Testing from Command Line

### Start the Poker Therapist API

```bash
# In a new terminal
cd /path/to/Poker-Therapist
uvicorn backend.api.main:app --reload
```

### Test the Webhooks

```bash
# Run the test script
python n8n-workflows/test_webhooks.py
```

Or test manually:

```bash
# Test the n8n test endpoint
curl -X POST http://localhost:8000/api/webhooks/n8n/test

# Test poker analysis
curl -X POST http://localhost:8000/api/webhooks/n8n \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "poker_analysis",
    "user_id": "test_user",
    "email": "test@example.com",
    "data": {
      "hand_data": {
        "position": "BTN",
        "cards": ["As", "Kd"]
      }
    }
  }'
```

## Available Workflows

### 1. Poker Hand Analysis
- **File**: `poker-hand-analysis.json`
- **Trigger**: Webhook
- **Purpose**: Analyze poker hands automatically
- **Setup**: Configure email notifications

### 2. Tilt Detection Alert
- **File**: `tilt-detection-alert.json`
- **Trigger**: Schedule (every 15 minutes)
- **Purpose**: Monitor for tilt and send alerts
- **Setup**: Configure SMS/email/Slack notifications

### 3. Daily Coaching Report
- **File**: `daily-coaching-report.json`
- **Trigger**: Schedule (daily at 8 PM)
- **Purpose**: Generate daily performance reports
- **Setup**: Configure email template

### 4. AI Coach Discord Bot
- **File**: `ai-coach-discord-bot.json`
- **Trigger**: Discord webhook
- **Purpose**: Rex coaching bot for Discord
- **Setup**: Configure Discord webhook URL

## Common Commands

```bash
# Start n8n
docker-compose -f docker-compose.n8n.yml up -d

# Stop n8n
docker-compose -f docker-compose.n8n.yml down

# View logs
docker-compose -f docker-compose.n8n.yml logs -f

# Restart n8n
docker-compose -f docker-compose.n8n.yml restart

# Stop and remove all data
docker-compose -f docker-compose.n8n.yml down -v
```

## Environment Variables

Edit `docker-compose.n8n.yml` to customize:

```yaml
environment:
  # Change admin password
  - N8N_BASIC_AUTH_PASSWORD=your-secure-password
  
  # Update API URL if not using localhost
  - API_BASE_URL=https://your-api-domain.com
  
  # Set your timezone
  - GENERIC_TIMEZONE=America/New_York
```

## Production Setup

For production deployment:

1. **Enable PostgreSQL**:
   ```bash
   docker-compose -f docker-compose.n8n.yml --profile production up -d
   ```

2. **Configure environment**:
   - Set strong passwords
   - Use HTTPS
   - Configure proper webhook URLs
   - Set up backups

3. **See full guide**: [n8n-workflows/SETUP_GUIDE.md](n8n-workflows/SETUP_GUIDE.md)

## Troubleshooting

### n8n can't connect to API

**Solution**: Make sure the API is running and accessible:
```bash
curl http://localhost:8000/health
```

If using Docker for both, use `host.docker.internal` instead of `localhost`.

### Workflow not triggering

**Solution**: 
1. Check if workflow is **Active** (toggle in top right)
2. Verify trigger configuration
3. Check n8n logs: `docker-compose -f docker-compose.n8n.yml logs -f`

### Webhook returns 404

**Solution**: Ensure the API is running and the route is correct:
```bash
curl http://localhost:8000/api/webhooks/n8n/status
```

## Next Steps

1. ✅ n8n is running
2. ✅ Workflows imported
3. 📚 Read the [full setup guide](n8n-workflows/SETUP_GUIDE.md)
4. 🎨 Customize workflows for your needs
5. 🚀 Create your own automation workflows!

## Support

- [n8n Documentation](https://docs.n8n.io/)
- [n8n Community](https://community.n8n.io/)
- [Poker Therapist GitHub](https://github.com/JohnDaWalka/Poker-Therapist)

Happy automating! 🎰🤖
