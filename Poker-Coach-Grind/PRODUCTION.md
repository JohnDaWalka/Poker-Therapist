# Production Deployment Guide

## Environment Configuration

Create a production `.env` file with secure settings:

```bash
# Environment
ENVIRONMENT=production

# Database (use PostgreSQL in production)
GRIND_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/poker_grind

# API Security
GRIND_API_KEY=your_secure_random_api_key_here
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
ENABLE_SQL_QUERIES=false  # Disable direct SQL access in production

# Crypto APIs
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
COINGECKO_API_KEY=your_coingecko_pro_api_key

# n8n
N8N_WEBHOOK_URL=https://your-n8n-instance.com
N8N_WEBHOOK_SECRET=your_webhook_verification_secret

# Monitoring
SENTRY_DSN=your_sentry_dsn  # Optional: for error tracking
LOG_LEVEL=INFO
```

## Docker Production Setup

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8001

# Run with gunicorn for production
CMD ["gunicorn", "Poker-Coach-Grind.api.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8001", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: poker_grind
      POSTGRES_USER: pokeruser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - poker_network

  poker-coach-grind:
    build: ./Poker-Coach-Grind
    ports:
      - "8001:8001"
    environment:
      GRIND_DATABASE_URL: postgresql+asyncpg://pokeruser:${DB_PASSWORD}@postgres:5432/poker_grind
      ENVIRONMENT: production
      GRIND_API_KEY: ${GRIND_API_KEY}
      ALLOWED_ORIGINS: ${ALLOWED_ORIGINS}
      COINGECKO_API_KEY: ${COINGECKO_API_KEY}
      ETHEREUM_RPC_URL: ${ETHEREUM_RPC_URL}
      SOLANA_RPC_URL: ${SOLANA_RPC_URL}
    depends_on:
      - postgres
    restart: unless-stopped
    networks:
      - poker_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - WEBHOOK_URL=https://your-n8n-domain.com
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped
    networks:
      - poker_network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - poker-coach-grind
      - n8n
    restart: unless-stopped
    networks:
      - poker_network

networks:
  poker_network:
    driver: bridge

volumes:
  postgres_data:
  n8n_data:
```

## Nginx Configuration

```nginx
upstream poker_api {
    server poker-coach-grind:8001;
}

upstream n8n {
    server n8n:5678;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    location / {
        proxy_pass http://poker_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl http2;
    server_name n8n.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    location / {
        proxy_pass http://n8n;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Database Migration

### Switch to PostgreSQL

1. Update `requirements.txt`:
```txt
asyncpg>=0.29.0
```

2. Update connection string in `.env`:
```bash
GRIND_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/poker_grind
```

3. Run migrations:
```bash
python -m Poker-Coach-Grind.cli.main init-db
```

## Security Hardening

### 1. API Key Middleware

Add to `Poker-Coach-Grind/api/main.py`:

```python
from fastapi import Header, HTTPException, Security
from fastapi.security import APIKeyHeader
import os

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key for protected endpoints."""
    expected_key = os.getenv("GRIND_API_KEY")
    if not expected_key:
        return  # No API key configured, allow access
    
    if api_key != expected_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API key"
        )

# Apply to routes:
@app.post("/api/bankroll/transaction", dependencies=[Depends(verify_api_key)])
async def create_transaction(...):
    ...
```

### 2. Rate Limiting

Install and configure:
```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/n8n/webhook/bankroll-transaction")
@limiter.limit("10/minute")
async def n8n_bankroll_transaction(request: Request):
    ...
```

### 3. Webhook Signature Verification

```python
import hmac
import hashlib
from fastapi import Header, HTTPException

async def verify_webhook_signature(
    request: Request,
    x_webhook_signature: str = Header(None)
):
    """Verify webhook signature from n8n."""
    webhook_secret = os.getenv("N8N_WEBHOOK_SECRET")
    if not webhook_secret:
        return  # No signature verification configured
    
    body = await request.body()
    expected_sig = hmac.new(
        webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(x_webhook_signature or "", expected_sig):
        raise HTTPException(status_code=403, detail="Invalid signature")
```

## Monitoring

### Health Checks

The API includes a `/health` endpoint for monitoring:

```bash
curl https://api.yourdomain.com/health
```

### Logging

Configure structured logging:

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_obj)

# Configure logging
logging.basicConfig(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.getLogger().addHandler(handler)
```

## Backup Strategy

### 1. Database Backups

```bash
# PostgreSQL backup
pg_dump poker_grind > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated with cron
0 2 * * * pg_dump poker_grind | gzip > /backups/poker_grind_$(date +\%Y\%m\%d).sql.gz
```

### 2. Configuration Backups

```bash
# Backup n8n workflows
docker exec n8n n8n export:workflow --all --output=/backups/

# Backup environment config
cp .env /backups/.env.$(date +%Y%m%d)
```

## Performance Optimization

### 1. Database Indexing

Add indexes for frequently queried columns:

```python
# In database/models.py
class BankrollTransaction(Base):
    ...
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
    )

class HandHistoryGrind(Base):
    ...
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'date_played'),
        Index('idx_session', 'session_id'),
    )
```

### 2. Caching

Add Redis for caching crypto prices:

```python
import redis
import json
from datetime import timedelta

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

async def get_crypto_prices_cached(symbols):
    cache_key = f"crypto_prices:{','.join(sorted(symbols))}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    prices = await get_crypto_prices(symbols)
    redis_client.setex(cache_key, timedelta(minutes=5), json.dumps(prices))
    return prices
```

## Deployment Checklist

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Configure `ALLOWED_ORIGINS` with actual domains
- [ ] Set strong `GRIND_API_KEY`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Configure rate limiting
- [ ] Set up database backups
- [ ] Configure logging and monitoring
- [ ] Test health checks
- [ ] Verify n8n webhook authentication
- [ ] Set up firewall rules
- [ ] Enable fail2ban for SSH
- [ ] Configure alerts for errors
- [ ] Test disaster recovery procedure
- [ ] Document runbooks for common issues
- [ ] Set up automated security updates

## Maintenance

### Regular Tasks

- **Daily**: Monitor logs for errors
- **Weekly**: Review API usage and performance
- **Monthly**: Update dependencies
- **Quarterly**: Security audit and penetration testing

### Update Process

```bash
# Pull latest code
git pull origin main

# Backup database
pg_dump poker_grind > backup_before_update.sql

# Update dependencies
pip install -r requirements.txt --upgrade

# Run migrations if needed
python -m Poker-Coach-Grind.cli.main init-db

# Restart services
docker-compose restart poker-coach-grind
```

## Support

For production issues:
1. Check logs: `docker-compose logs -f poker-coach-grind`
2. Verify health: `curl http://localhost:8001/health`
3. Check database connectivity
4. Review recent changes in git log
