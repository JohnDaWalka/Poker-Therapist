# Poker-Coach-Grind Integration Guide

Complete guide for integrating Poker-Coach-Grind with Therapy Rex and n8n workflows.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Poker Player                             │
└───────────────┬─────────────────────────────────────────────┘
                │
                ↓
┌───────────────────────────────────────────────────────────────┐
│                  Poker-Coach-Grind API                         │
│                  (Port 8001)                                   │
│                                                                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │ Bankroll   │  │   Hands    │  │   Crypto   │             │
│  │  Tracker   │  │  Reviewer  │  │  Portfolio │             │
│  └────────────┘  └────────────┘  └────────────┘             │
│                                                                │
│  ┌────────────────────────────────────────────────┐          │
│  │         n8n Integration Layer                   │          │
│  │  • Webhook Endpoints                            │          │
│  │  • Workflow Triggers                            │          │
│  │  • Event Broadcasting                           │          │
│  └────────────────────────────────────────────────┘          │
└──────────┬────────────────────────────────┬──────────────────┘
           │                                 │
           ↓                                 ↓
┌──────────────────────┐         ┌─────────────────────────┐
│    n8n Workflows     │         │     Therapy Rex         │
│    (Port 5678)       │←────────│    (Port 8000)          │
│                      │         │                         │
│ • Automation         │         │  • Mental Game Coach    │
│ • Notifications      │         │  • Tilt Detection       │
│ • Data Processing    │         │  • Session Analysis     │
└──────────────────────┘         └─────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────────────┐
│           External Services                      │
│                                                  │
│  • Discord / Telegram                           │
│  • Email / SMS                                  │
│  • Google Sheets                                │
│  • CoinGecko (crypto prices)                   │
│  • Ethereum / Solana RPCs                      │
└─────────────────────────────────────────────────┘
```

## Quick Start (All Systems)

### 1. Start Therapy Rex Backend

```bash
cd /home/runner/work/Poker-Therapist/Poker-Therapist/backend
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start Poker-Coach-Grind API

```bash
cd /home/runner/work/Poker-Therapist/Poker-Therapist
pip install -r Poker-Coach-Grind/requirements.txt
python -m Poker-Coach-Grind.cli.main init-db
uvicorn Poker-Coach-Grind.api.main:app --reload --port 8001
```

### 3. Start n8n

```bash
npx n8n
# Runs on http://localhost:5678
```

### 4. Import n8n Workflows

1. Open http://localhost:5678
2. Click "Workflows" → "Import from File"
3. Import workflows from `Poker-Coach-Grind/n8n-workflows/`:
   - `bankroll-tracker.json`
   - `crypto-portfolio-monitor.json`
   - `therapy-rex-trigger.json`

### 5. Configure Environment Variables

Create `.env` in the root directory:

```bash
# Poker-Coach-Grind
GRIND_DATABASE_URL=sqlite+aiosqlite:///poker_grind.db

# Therapy Rex
DATABASE_URL=sqlite:///therapy_rex.db
XAI_API_KEY=xai-your-key-here
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# n8n
N8N_WEBHOOK_URL=http://localhost:5678

# Crypto APIs
ETHEREUM_RPC_URL=https://eth.llamarpc.com
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
COINGECKO_API_KEY=your_coingecko_key

# Notifications
DISCORD_WEBHOOK_URL=your_discord_webhook
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id
```

## Integration Scenarios

### Scenario 1: Automated Session Tracking

**Flow:**
1. You finish a poker session on CoinPoker
2. Export hand history file
3. n8n workflow detects the file
4. Imports hands to Poker-Coach-Grind
5. Calculates session statistics
6. Updates bankroll
7. Checks for downswing conditions
8. Triggers Therapy Rex if needed
9. Sends notification with session summary

**Setup:**

1. **Create n8n workflow** (File Monitor):
   ```json
   {
     "trigger": "File Watcher",
     "path": "~/Downloads/pokerhands/",
     "pattern": "*.txt"
   }
   ```

2. **Process File**:
   - Parse hand history
   - POST to `/api/n8n/webhook/hand-import`

3. **Update Bankroll**:
   - Calculate net profit from session
   - POST to `/api/n8n/webhook/bankroll-transaction`

4. **Check Conditions**:
   - GET `/api/bankroll/stats/{user_id}`
   - If downswing detected, trigger Therapy Rex

### Scenario 2: Crypto Portfolio Alerts

**Flow:**
1. n8n checks crypto prices every 4 hours
2. Fetches portfolio value from Poker-Coach-Grind
3. Calculates change percentage
4. If significant change (>10%), sends alert
5. Logs to Google Sheets for tracking

**Setup:**

1. **Use provided workflow**: `crypto-portfolio-monitor.json`

2. **Configure wallets** via API:
   ```bash
   curl -X POST http://localhost:8001/api/crypto/wallet/add \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "your_user_id",
       "blockchain": "ethereum",
       "address": "0x...",
       "label": "Main Wallet"
     }'
   ```

3. **Set up Discord webhook** in n8n credentials

### Scenario 3: Mental Game Check-ins

**Flow:**
1. Scheduled trigger (daily at 10 PM)
2. Fetch today's bankroll transactions
3. Analyze performance patterns
4. Determine if intervention needed
5. Trigger appropriate Therapy Rex session type
6. Send reminder notification

**Setup:**

1. **Create n8n workflow**:
   ```json
   {
     "trigger": "Schedule Trigger",
     "cron": "0 22 * * *",
     "timezone": "America/New_York"
   }
   ```

2. **Fetch Performance Data**:
   - GET `/api/bankroll/history/{user_id}?limit=10`
   - Analyze last 10 transactions

3. **Trigger Therapy Rex**:
   - POST to `/api/n8n/webhook/therapy-session`
   - Include performance context

### Scenario 4: Multi-Site Hand Aggregation

**Flow:**
1. Play on multiple poker sites
2. Each site exports to different format
3. n8n normalizes all formats
4. Imports to unified Poker-Coach-Grind database
5. Generates combined session report
6. Cross-references blockchain data (for crypto sites)

**Setup:**

1. **Create parsers for each site** in n8n
2. **Normalize to common format**:
   ```json
   {
     "hand_id": "...",
     "date_played": "2026-01-11T...",
     "stakes": "1/2",
     "won_amount": 50.00,
     "platform": "CoinPoker|PokerStars|..."
   }
   ```

3. **Import via API**:
   - POST to `/api/hands/import`

## API Integration Examples

### From n8n to Poker-Coach-Grind

**Record Bankroll Transaction:**
```javascript
// In n8n HTTP Request node
{
  "method": "POST",
  "url": "http://localhost:8001/api/n8n/webhook/bankroll-transaction",
  "body": {
    "user_id": "{{ $json.user_id }}",
    "amount": {{ $json.amount }},
    "transaction_type": "cash_game",
    "stakes": "{{ $json.stakes }}",
    "notes": "{{ $json.notes }}"
  }
}
```

**Query Hands via SQL:**
```javascript
{
  "method": "POST",
  "url": "http://localhost:8001/api/hands/query",
  "body": {
    "user_id": "user123",
    "sql_query": "SELECT * FROM hand_histories_grind WHERE stakes = '1/2' AND date_played >= '2026-01-01' AND user_id = 'user123' ORDER BY date_played DESC",
    "limit": 100
  }
}
```

**Get Crypto Prices:**
```javascript
{
  "method": "GET",
  "url": "http://localhost:8001/api/crypto/prices?symbols=ETH,SOL,ONDO"
}
```

### From Poker-Coach-Grind to n8n

**Trigger Alert Workflow:**
```python
from Poker-Coach-Grind.api.n8n_integration import N8NClient, trigger_bankroll_alert

# Initialize client
n8n = N8NClient(
    n8n_url="http://localhost:5678",
    api_key="optional_api_key"
)

# Trigger alert
await trigger_bankroll_alert(
    n8n_client=n8n,
    user_id="user123",
    alert_type="low_balance",
    data={
        "current_balance": 500.00,
        "threshold": 1000.00
    }
)
```

### From Poker-Coach-Grind to Therapy Rex

**Trigger Therapy Session:**
```python
import httpx

async def trigger_therapy_session(user_id: str, trigger_reason: str, context: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/triage",
            json={
                "user_id": user_id,
                "trigger_reason": trigger_reason,
                "context": context
            }
        )
        return response.json()

# Example: Downswing detected
await trigger_therapy_session(
    user_id="user123",
    trigger_reason="downswing_detected",
    context={
        "losing_streak": 5,
        "total_loss": -1500.00,
        "sessions_analyzed": 10
    }
)
```

## Webhook Security

### Secure Your Webhooks

1. **API Key Authentication**:
   ```python
   # In Poker-Coach-Grind/api/main.py
   from fastapi import Header, HTTPException
   
   async def verify_api_key(x_api_key: str = Header(...)):
       if x_api_key != os.getenv("GRIND_API_KEY"):
           raise HTTPException(status_code=401, detail="Invalid API key")
   ```

2. **IP Whitelist** (for production):
   ```python
   ALLOWED_IPS = ["127.0.0.1", "your-n8n-ip"]
   
   @app.middleware("http")
   async def ip_whitelist(request: Request, call_next):
       client_ip = request.client.host
       if client_ip not in ALLOWED_IPS:
           raise HTTPException(status_code=403)
       return await call_next(request)
   ```

3. **HMAC Signature Verification**:
   ```python
   import hmac
   import hashlib
   
   def verify_webhook_signature(payload: str, signature: str, secret: str):
       expected = hmac.new(
           secret.encode(),
           payload.encode(),
           hashlib.sha256
       ).hexdigest()
       return hmac.compare_digest(signature, expected)
   ```

## Monitoring & Debugging

### Check API Health

```bash
# Poker-Coach-Grind
curl http://localhost:8001/health

# Therapy Rex
curl http://localhost:8000/health
```

### View API Documentation

- Poker-Coach-Grind: http://localhost:8001/docs
- Therapy Rex: http://localhost:8000/docs

### n8n Execution Logs

1. Open n8n: http://localhost:5678
2. Click on workflow
3. View "Executions" tab
4. Click on any execution to see detailed logs

### Database Inspection

```bash
# Poker-Coach-Grind database
sqlite3 poker_grind.db
sqlite> .tables
sqlite> SELECT * FROM bankroll_transactions LIMIT 5;

# Therapy Rex database
sqlite3 therapy_rex.db
sqlite> .tables
sqlite> SELECT * FROM sessions LIMIT 5;
```

## Troubleshooting

### Issue: Webhook not receiving data

**Solution:**
1. Check n8n is running: `curl http://localhost:5678`
2. Verify webhook URL in configuration
3. Check n8n execution logs for errors
4. Ensure workflow is activated (toggle in n8n UI)

### Issue: Crypto prices not updating

**Solution:**
1. Check CoinGecko API status
2. Verify `COINGECKO_API_KEY` in .env
3. Test manually: `python -m Poker-Coach-Grind.cli.main prices ETH`
4. Check rate limits (free tier: 10-50 calls/minute)

### Issue: Therapy Rex not triggering

**Solution:**
1. Verify Therapy Rex backend is running
2. Check connection: `curl http://localhost:8000/health`
3. Review n8n workflow logic for trigger conditions
4. Check Therapy Rex logs for errors

## Production Deployment

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  therapy-rex:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - XAI_API_KEY=${XAI_API_KEY}
    
  poker-coach-grind:
    build: ./Poker-Coach-Grind
    ports:
      - "8001:8001"
    environment:
      - GRIND_DATABASE_URL=postgresql://...
      - COINGECKO_API_KEY=${COINGECKO_API_KEY}
    depends_on:
      - therapy-rex
  
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

Run with:
```bash
docker-compose up -d
```

## Support

- **Poker-Coach-Grind**: Check `/docs` at http://localhost:8001/docs
- **n8n**: https://community.n8n.io
- **Therapy Rex**: See backend/README.md

## Next Steps

1. ✅ Set up all three services (Therapy Rex, Poker-Coach-Grind, n8n)
2. ✅ Import example workflows
3. ✅ Configure your wallets and API keys
4. ✅ Test with sample data
5. ✅ Customize workflows for your needs
6. ✅ Set up notifications (Discord, Telegram, etc.)
7. ✅ Deploy to production
