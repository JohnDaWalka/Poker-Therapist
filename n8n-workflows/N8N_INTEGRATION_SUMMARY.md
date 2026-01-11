# n8n Integration Summary

This document provides an overview of the n8n workflow automation integration for Poker Therapist.

## What Was Implemented

### 1. Backend API Integration

**File**: `backend/api/routes/n8n.py`

A complete FastAPI route module that provides webhook endpoints for n8n workflows:

- **Main webhook endpoint**: `/api/webhooks/n8n` (POST)
  - Handles multiple event types
  - Validates incoming webhook payloads
  - Routes to appropriate handlers
  
- **Test endpoint**: `/api/webhooks/n8n/test` (POST)
  - Quick connectivity test
  
- **Status endpoint**: `/api/webhooks/n8n/status` (GET)
  - Check integration status
  - List supported event types

**Supported Event Types**:
- `poker_analysis` - Analyze poker hands
- `triage_session` - Start tilt triage sessions
- `deep_session` - Start deep therapy sessions
- `user_notification` - Send user notifications
- `custom` - Custom workflow events

### 2. Workflow Templates

Four ready-to-use n8n workflow templates in JSON format:

1. **Poker Hand Analysis** (`poker-hand-analysis.json`)
   - Webhook trigger for hand submissions
   - API call to analyze hands
   - Email notification on completion
   - Slack logging for tracking

2. **Tilt Detection Alert** (`tilt-detection-alert.json`)
   - Scheduled checks every 15 minutes
   - Detects tilt levels ≥7/10
   - Multi-channel alerts (Email, SMS, Slack)
   - Automatic triage session creation
   - Database logging

3. **Daily Coaching Report** (`daily-coaching-report.json`)
   - Daily schedule (8 PM)
   - Fetches session data
   - Generates performance report
   - HTML email with statistics
   - Google Sheets export (optional)

4. **AI Coach Discord Bot** (`ai-coach-discord-bot.json`)
   - Discord webhook integration
   - Command parsing (!rex commands)
   - AI response generation
   - Special command handling

### 3. Documentation

Comprehensive documentation for setup and usage:

- **README.md** - Overview and workflow descriptions
- **SETUP_GUIDE.md** - Detailed installation and configuration
- **QUICKSTART.md** - 5-minute quick start guide

### 4. Deployment Tools

**Docker Compose** (`docker-compose.n8n.yml`):
- Pre-configured n8n container
- PostgreSQL for production use
- Network configuration for API access
- Persistent data volumes

**Testing Script** (`test_webhooks.py`):
- Automated webhook testing
- Tests all event types
- Clear success/failure reporting
- Can run against any API URL

### 5. Configuration

**Environment Variables** (`.env.example`):
- n8n server URL
- API keys for n8n
- External service credentials (Twilio, Slack, Discord)
- Google Sheets configuration

### 6. Main Application Update

**FastAPI Main** (`backend/api/main.py`):
- n8n router integrated into main app
- Available at `/api/webhooks/n8n/*` endpoints

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         n8n Server                          │
│                    (localhost:5678)                         │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Workflow   │  │   Workflow   │  │   Workflow   │    │
│  │   Triggers   │  │    Logic     │  │   Actions    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTP POST/GET
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Poker Therapist FastAPI Backend               │
│                    (localhost:8000)                         │
│                                                             │
│  /api/webhooks/n8n  ──┬──> poker_analysis                  │
│                       ├──> triage_session                   │
│                       ├──> deep_session                     │
│                       ├──> user_notification                │
│                       └──> custom                           │
│                                                             │
│  /api/webhooks/n8n/test    (connectivity test)             │
│  /api/webhooks/n8n/status  (integration status)            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ (Future: AI Orchestrator,
                            │  Session Manager integration)
                            ▼
                    [Backend Services]
```

## Use Cases

### Automated Coaching Workflows

1. **Real-time Hand Analysis**
   - Player submits hand via app
   - n8n triggers analysis workflow
   - AI analyzes hand strategy
   - Results emailed to player
   - Performance logged

2. **Tilt Management**
   - n8n monitors player metrics
   - Detects tilt indicators
   - Sends immediate alerts
   - Creates triage session
   - Notifies coach via Slack

3. **Daily Performance Reports**
   - Scheduled at end of day
   - Aggregates session data
   - Generates statistics
   - Emails formatted report
   - Exports to Google Sheets

4. **Multi-Platform Coaching**
   - Discord/Slack bot integration
   - Players ask questions
   - Rex AI responds
   - Conversation logged
   - Analytics tracked

### Integration Possibilities

The n8n integration enables connections with:

**Communication Platforms**:
- Discord
- Slack
- Telegram
- WhatsApp
- SMS (Twilio)

**Productivity Tools**:
- Google Sheets
- Notion
- Airtable
- Trello

**Data & Analytics**:
- PostgreSQL
- MongoDB
- InfluxDB
- Grafana

**Marketing & CRM**:
- Mailchimp
- SendGrid
- HubSpot
- Salesforce

## Getting Started

### For Users

1. **Quick Start** (5 minutes):
   ```bash
   docker-compose -f docker-compose.n8n.yml up -d
   ```
   Then visit http://localhost:5678 and import workflows.

2. **Read**: `n8n-workflows/QUICKSTART.md`

### For Developers

1. **Explore the API**:
   ```bash
   uvicorn backend.api.main:app --reload
   ```
   Visit http://localhost:8000/docs for API documentation

2. **Test webhooks**:
   ```bash
   python n8n-workflows/test_webhooks.py
   ```

3. **Read**: `n8n-workflows/SETUP_GUIDE.md`

### For Advanced Users

1. Create custom workflows in n8n
2. Extend the webhook handlers in `backend/api/routes/n8n.py`
3. Add new event types as needed
4. Integrate additional external services

## Future Enhancements

Potential additions to the n8n integration:

1. **Authentication & Security**
   - Webhook signature verification
   - API key authentication
   - Rate limiting

2. **Advanced Workflows**
   - Bankroll management automation
   - Tournament strategy adjustments
   - Player network analysis
   - Competitor tracking

3. **AI Integration**
   - GPT-4 analysis in workflows
   - Voice response generation
   - Image processing for hand screenshots
   - Sentiment analysis

4. **Analytics**
   - Custom dashboards
   - Performance tracking
   - Trend analysis
   - Predictive modeling

5. **Mobile Integration**
   - Push notifications
   - iOS shortcuts
   - Android automation

## Files Added/Modified

### New Files
- `backend/api/routes/n8n.py` - Webhook endpoints
- `n8n-workflows/README.md` - Workflow documentation
- `n8n-workflows/SETUP_GUIDE.md` - Setup instructions
- `n8n-workflows/QUICKSTART.md` - Quick start guide
- `n8n-workflows/poker-hand-analysis.json` - Workflow template
- `n8n-workflows/tilt-detection-alert.json` - Workflow template
- `n8n-workflows/daily-coaching-report.json` - Workflow template
- `n8n-workflows/ai-coach-discord-bot.json` - Workflow template
- `n8n-workflows/test_webhooks.py` - Testing script
- `docker-compose.n8n.yml` - Docker deployment
- `n8n-workflows/N8N_INTEGRATION_SUMMARY.md` - This file

### Modified Files
- `backend/api/main.py` - Added n8n router
- `.env.example` - Added n8n configuration
- `README.md` - Added n8n feature section

## Support & Resources

- **n8n Documentation**: https://docs.n8n.io/
- **n8n Community**: https://community.n8n.io/
- **n8n Workflows Library**: https://n8n.io/workflows/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Poker Therapist Repository**: https://github.com/JohnDaWalka/Poker-Therapist

## Conclusion

The n8n integration provides Poker Therapist with powerful workflow automation capabilities. Users can now:

✅ Automate repetitive coaching tasks
✅ Create custom workflows without coding
✅ Integrate with dozens of external services
✅ Monitor players in real-time
✅ Generate automated reports
✅ Build multi-platform bots
✅ Scale coaching operations

The system is designed to be:
- **Easy to use** - Quick start in minutes
- **Flexible** - Customize any workflow
- **Extensible** - Add new integrations easily
- **Scalable** - Handle high-volume operations
- **Well-documented** - Comprehensive guides included

Start automating your poker coaching today! 🎰🤖
