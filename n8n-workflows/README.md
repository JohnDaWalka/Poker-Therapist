# n8n Workflow Automation for Poker Therapist

This directory contains n8n workflow templates for automating various aspects of the Poker Therapist application.

## What is n8n?

n8n is an open-source workflow automation platform that allows you to connect different services and APIs together. It provides a visual interface for building complex automation workflows without writing code.

## Quick Start

### 1. Install n8n

```bash
# Using npm
npm install n8n -g

# Using Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### 2. Configure Poker Therapist API

1. Start your Poker Therapist backend:
   ```bash
   cd /path/to/Poker-Therapist
   uvicorn backend.api.main:app --reload
   ```

2. Note your API endpoint (e.g., `http://localhost:8000`)

### 3. Import Workflow Templates

1. Open n8n in your browser (default: `http://localhost:5678`)
2. Click "Import" → "From File"
3. Select one of the JSON workflow files from this directory
4. Configure the webhook URLs to point to your Poker Therapist API

## Available Workflows

### 1. Poker Hand Analysis Automation (`poker-hand-analysis.json`)
Automatically analyzes poker hands when triggered by external events.

**Use Cases:**
- Batch analyze hands from database
- Real-time hand analysis triggered by game events
- Scheduled analysis of daily sessions

**Required Nodes:**
- Webhook (trigger)
- HTTP Request (to Poker Therapist API)
- Email/Slack notification (optional)

### 2. Tilt Detection & Alert (`tilt-detection-alert.json`)
Monitors player behavior and sends alerts when tilt is detected.

**Use Cases:**
- Real-time tilt monitoring
- Send SMS/email alerts to coach
- Log tilt incidents to database

**Required Nodes:**
- Schedule Trigger (periodic checks)
- HTTP Request (check player status)
- Conditional logic
- Notification nodes (SMS, Email, Slack)

### 3. Daily Coaching Report (`daily-coaching-report.json`)
Generates and sends daily coaching reports to players.

**Use Cases:**
- Daily performance summaries
- Weekly progress reports
- Monthly analytics

**Required Nodes:**
- Cron Trigger (daily at specific time)
- HTTP Request (fetch session data)
- Data transformation
- Email/PDF generation

### 4. User Onboarding Automation (`user-onboarding.json`)
Automates the user onboarding process.

**Use Cases:**
- Welcome email sequences
- Account setup reminders
- Initial assessment scheduling

**Required Nodes:**
- Webhook (new user trigger)
- Email sequences
- Database updates
- Calendar integration

### 5. AI Coach Integration (`ai-coach-integration.json`)
Connects external platforms to the AI coaching system.

**Use Cases:**
- Discord/Slack bot integration
- Telegram coaching bot
- WhatsApp coaching notifications

**Required Nodes:**
- Message platform webhook
- HTTP Request (to AI coach API)
- Response formatting

## Webhook Endpoints

The Poker Therapist API provides the following n8n webhook endpoints:

### Main Webhook Endpoint
```
POST /api/webhooks/n8n
```

**Supported Event Types:**
- `poker_analysis` - Analyze poker hands
- `triage_session` - Start tilt triage session
- `deep_session` - Start deep therapy session
- `user_notification` - Send user notifications
- `custom` - Custom events

**Example Payload:**
```json
{
  "event_type": "poker_analysis",
  "user_id": "user123",
  "email": "player@example.com",
  "data": {
    "hand_data": {
      "position": "BTN",
      "cards": ["As", "Kd"],
      "action": "raise",
      "pot_size": 100
    }
  }
}
```

### Test Endpoint
```
POST /api/webhooks/n8n/test
```

Use this to verify your n8n workflow can reach the API.

### Status Endpoint
```
GET /api/webhooks/n8n/status
```

Check integration status and supported event types.

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# n8n Configuration
N8N_WEBHOOK_URL=http://localhost:5678/webhook
N8N_API_KEY=your-n8n-api-key-here

# Poker Therapist API
API_BASE_URL=http://localhost:8000
XAI_API_KEY=xai-your-key-here
```

### Security

1. **API Authentication**: Ensure your n8n webhooks use proper authentication
2. **HTTPS**: Use HTTPS in production environments
3. **Rate Limiting**: Configure rate limits on webhook endpoints
4. **Webhook Validation**: Validate incoming webhook signatures

## Best Practices

1. **Error Handling**: Always include error handling nodes in workflows
2. **Logging**: Add logging nodes to track workflow execution
3. **Testing**: Test workflows in development before deploying to production
4. **Monitoring**: Set up monitoring and alerting for critical workflows
5. **Version Control**: Keep workflow JSON files in version control
6. **Documentation**: Document custom workflows and their purpose

## Example Workflow Structure

```
n8n Workflow
│
├── Trigger Node (Webhook, Schedule, etc.)
│   └── Configure trigger conditions
│
├── Input Processing
│   └── Extract and validate data
│
├── API Call to Poker Therapist
│   └── HTTP Request with authentication
│
├── Response Processing
│   └── Transform and format response
│
├── Action Nodes (conditional)
│   ├── Send Email
│   ├── Update Database
│   └── Trigger another workflow
│
└── Error Handling
    └── Log errors and send alerts
```

## Advanced Use Cases

### Multi-Platform Integration
Connect Poker Therapist with:
- **Discord**: Poker strategy bot
- **Telegram**: Daily tips and reminders
- **Slack**: Team coaching notifications
- **Google Sheets**: Analytics export
- **Notion**: Session notes and insights

### Automated Coaching Flows
1. Player finishes session → Automatic analysis
2. Tilt detected → Send calming exercises
3. Milestone achieved → Celebration notification
4. Losing streak → Schedule coaching call

### Data Pipeline
1. Export hands from poker sites → n8n
2. Batch analysis via API → n8n
3. Store results in database → n8n
4. Generate visualizations → n8n
5. Email weekly report → n8n

## Troubleshooting

### Webhook Not Triggering
- Check firewall settings
- Verify webhook URL is correct
- Check n8n logs for errors
- Test with `/api/webhooks/n8n/test` endpoint

### API Authentication Errors
- Verify API keys are correct
- Check environment variables are loaded
- Ensure Bearer token format is correct

### Rate Limiting
- Implement exponential backoff
- Use queue nodes for batch operations
- Monitor API usage

## Support

For issues or questions:
1. Check the [n8n documentation](https://docs.n8n.io/)
2. Review [Poker Therapist API docs](../docs/)
3. Open an issue on GitHub

## Contributing

To contribute new workflows:
1. Create your workflow in n8n
2. Export as JSON
3. Add to this directory with descriptive name
4. Update this README with workflow description
5. Submit pull request

## Resources

- [n8n Documentation](https://docs.n8n.io/)
- [n8n Community Workflows](https://n8n.io/workflows/)
- [Poker Therapist API Reference](../docs/API.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
