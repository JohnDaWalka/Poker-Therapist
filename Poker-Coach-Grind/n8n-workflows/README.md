# n8n Workflow Integration for Poker-Coach-Grind

This directory contains example n8n workflow configurations that integrate with Poker-Coach-Grind and Therapy Rex.

## Overview

n8n is a workflow automation tool that allows you to connect different services and automate tasks. These workflows enable:

- **Automated Bankroll Tracking**: Automatically log transactions from various sources
- **Hand History Processing**: Import and analyze hands from poker sites
- **Crypto Monitoring**: Track wallet balances and price alerts
- **Therapy Rex Integration**: Trigger mental game coaching sessions based on conditions
- **Notifications**: Send alerts via Discord, Telegram, Email, or SMS

## Setup

### 1. Install n8n

```bash
# Using npx (recommended for testing)
npx n8n

# Or install globally
npm install -g n8n
n8n start

# Or using Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### 2. Configure Poker-Coach-Grind Connection

In your n8n instance:

1. Go to Settings → Credentials
2. Add a new "HTTP Header Auth" credential
3. Name: `Poker-Coach-Grind API`
4. Header Name: `X-API-Key`
5. Header Value: Your API key (if configured)

### 3. Set Base URL

In each workflow, update the HTTP Request nodes to point to your Poker-Coach-Grind API:
- Local: `http://localhost:8001`
- Production: `https://your-domain.com`

## Available Workflows

### 1. Bankroll Tracker Automation (`bankroll-tracker.json`)

**Triggers:**
- Manual trigger
- Webhook from poker sites
- Scheduled daily summary

**Actions:**
- Create bankroll transaction
- Calculate current balance
- Send notification if balance crosses threshold
- Trigger Therapy Rex if significant loss detected

### 2. Hand History Processor (`hand-history-processor.json`)

**Triggers:**
- File upload (hand history file)
- Email attachment (hand history)
- API webhook

**Actions:**
- Parse hand history file
- Import hands to database
- Calculate session statistics
- Generate session review report
- Optionally trigger Therapy Rex session review

### 3. Crypto Portfolio Monitor (`crypto-portfolio-monitor.json`)

**Triggers:**
- Scheduled (every hour)
- Price alert trigger

**Actions:**
- Fetch current crypto prices
- Check wallet balances
- Calculate portfolio value
- Send alert if portfolio changes significantly
- Update portfolio tracking spreadsheet

### 4. Therapy Rex Session Trigger (`therapy-rex-trigger.json`)

**Triggers:**
- Downswing detected (3+ losing sessions)
- Large loss (> 5 buy-ins)
- Manual trigger
- Scheduled mental game check-in

**Actions:**
- Gather recent session data
- Analyze tilt indicators
- Trigger appropriate Therapy Rex session type
- Send session summary to user

### 5. Multi-Platform Hand Aggregator (`multi-platform-aggregator.json`)

**Triggers:**
- Webhook from CoinPoker
- Webhook from PokerStars (via tracker)
- Manual file import

**Actions:**
- Normalize hand data from different formats
- Import to unified database
- Cross-reference with blockchain data (for CoinPoker)
- Generate combined session report

## Webhook Endpoints

Your Poker-Coach-Grind API exposes these webhook endpoints for n8n:

### Incoming (n8n calls Poker-Coach-Grind)

```
POST /api/n8n/webhook/bankroll-transaction
POST /api/n8n/webhook/hand-import
POST /api/n8n/webhook/crypto-alert
POST /api/n8n/webhook/therapy-session
```

### Outgoing (Poker-Coach-Grind calls n8n)

Configure webhooks in your n8n workflows:

```
POST https://your-n8n-instance.com/webhook/bankroll-alert
POST https://your-n8n-instance.com/webhook/session-complete
POST https://your-n8n-instance.com/webhook/crypto-portfolio-update
```

## Example Workflow Scenarios

### Scenario 1: Automated Daily Report

1. **Trigger**: Schedule (daily at 11 PM)
2. **Get Data**: Fetch today's transactions and hands
3. **Calculate**: Total profit/loss, hands played, win rate
4. **Generate Report**: Format as markdown or HTML
5. **Send**: Email or Discord message with daily summary

### Scenario 2: Downswing Alert & Therapy

1. **Trigger**: New bankroll transaction
2. **Check**: Last 5 sessions all negative?
3. **If Yes**:
   - Send alert notification
   - Trigger Therapy Rex tilt triage session
   - Suggest session break
4. **If No**: Continue normal flow

### Scenario 3: Crypto Profit Taking

1. **Trigger**: Schedule (every 4 hours)
2. **Check**: Portfolio up more than 20%?
3. **If Yes**:
   - Send profit-taking suggestion
   - Calculate recommended withdrawal amount
   - Prepare transaction for review
4. **Log**: Record portfolio value for tracking

### Scenario 4: Hand History Auto-Import

1. **Trigger**: New email with attachment
2. **Check**: Email from poker site?
3. **Extract**: Download hand history file
4. **Process**: Parse and import hands
5. **Analyze**: Generate quick session stats
6. **Notify**: Send import confirmation with stats

## Integration with Therapy Rex

Poker-Coach-Grind can automatically trigger Therapy Rex sessions based on:

- **Performance Triggers**:
  - Losing streak (3+ sessions)
  - Large single-session loss
  - Downswing threshold crossed
  
- **Behavioral Triggers**:
  - Playing outside recommended hours
  - Stakes above bankroll management rules
  - Short sessions with losses (quit tilt)
  
- **Scheduled Triggers**:
  - Weekly mental game check-in
  - Post-tournament debrief
  - Monthly goal review

## Environment Variables

Set these in your n8n instance or `.env` file:

```bash
# Poker-Coach-Grind API
GRIND_API_URL=http://localhost:8001
GRIND_API_KEY=your_api_key_here

# n8n Configuration
N8N_WEBHOOK_URL=https://your-n8n-instance.com

# Notification Services
DISCORD_WEBHOOK_URL=your_discord_webhook
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token

# Therapy Rex
THERAPY_REX_API_URL=http://localhost:8000
```

## Testing Workflows

### Test Bankroll Transaction

```bash
curl -X POST http://localhost:5678/webhook/test-bankroll \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "amount": 250.00,
    "transaction_type": "cash_game",
    "stakes": "1/2",
    "notes": "Test session"
  }'
```

### Test Hand Import

```bash
curl -X POST http://localhost:5678/webhook/test-hand-import \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "platform": "CoinPoker",
    "hands": [
      {
        "hand_id": "12345",
        "date_played": "2026-01-11T03:00:00",
        "stakes": "1/2",
        "won_amount": 50.0
      }
    ]
  }'
```

## Security Best Practices

1. **Use HTTPS**: Always use HTTPS for production webhooks
2. **API Keys**: Implement API key authentication
3. **IP Whitelist**: Restrict webhook access to known IPs
4. **Validate Payloads**: Always validate incoming webhook data
5. **Rate Limiting**: Implement rate limits on webhook endpoints
6. **Secrets Management**: Use n8n's credential system for sensitive data

## Troubleshooting

### Webhook Not Receiving Data

1. Check n8n is running and accessible
2. Verify webhook URL is correct
3. Check firewall/security group settings
4. Review n8n execution logs

### Authentication Errors

1. Verify API key is correctly set
2. Check credential configuration in n8n
3. Ensure header name matches (case-sensitive)

### Workflow Not Triggering

1. Check trigger configuration
2. Verify schedule/cron expression
3. Review workflow activation status
4. Check n8n logs for errors

## Support

For workflow-specific questions:
- n8n Community: https://community.n8n.io
- n8n Docs: https://docs.n8n.io

For Poker-Coach-Grind integration:
- See API documentation at `/docs`
- Check workflow examples in this directory
