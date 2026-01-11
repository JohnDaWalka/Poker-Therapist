# Poker-Coach-Grind 🎰💰

A comprehensive bankroll tracker, hand history reviewer, and SQL live hand viewer with cryptocurrency integration.

## Features

### 💰 Bankroll Tracker
- Track poker bankroll across multiple platforms
- Real-time balance updates
- Historical balance tracking
- Win/loss tracking by session
- ROI and profit calculations
- Cryptocurrency wallet integration

### 📊 Hand History Reviewer
- Import hand histories from multiple poker sites
- SQL-based hand querying and filtering
- Advanced hand analysis
- Session review and statistics
- Hand replay functionality

### 🔍 SQL Live Hand Viewer
- Real-time hand viewing with SQL queries
- Filter by date, stakes, position, results
- Advanced search capabilities
- Export filtered results

### 🪙 Cryptocurrency Integration
Track your crypto poker winnings and manage funds across:
- **Ethereum (ETH)** - EVM-compatible blockchain
- **Render (RNDR)** - GPU rendering token
- **SUI** - Layer 1 blockchain
- **Uniswap (UNI)** - DEX governance token
- **Litecoin (LTC)** - Fast payment network
- **Ondo (ONDO)** - Institutional DeFi
- **Polygon (POL)** - Ethereum scaling
- **Virtuals Protocol (VIRTUAL)** - AI agent protocol
- **Solana (SOL)** - High-performance blockchain
- **Jupiter (JUP)** - Solana DEX aggregator
- **AIxBET** - AI-powered betting platform token

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m Poker-Coach-Grind.database.init_db

# Start the API server
uvicorn Poker-Coach-Grind.api.main:app --reload --port 8001

# Or use the CLI
python -m Poker-Coach-Grind.cli.main --help
```

## API Endpoints

### Bankroll Management
- `GET /api/bankroll/{user_id}` - Get current bankroll
- `POST /api/bankroll/transaction` - Record transaction
- `GET /api/bankroll/history/{user_id}` - Get bankroll history
- `GET /api/bankroll/stats/{user_id}` - Get bankroll statistics

### Hand History
- `POST /api/hands/import` - Import hand histories
- `POST /api/hands/query` - SQL query for hands
- `GET /api/hands/{hand_id}` - Get specific hand
- `GET /api/hands/session/{session_id}` - Get session hands

### Cryptocurrency
- `GET /api/crypto/prices` - Get current crypto prices
- `POST /api/crypto/wallet/add` - Add wallet for tracking
- `GET /api/crypto/wallet/{user_id}` - Get wallet balances
- `GET /api/crypto/portfolio/{user_id}` - Get portfolio value

## Database Schema

### Tables
- `bankroll_transactions` - All bankroll changes
- `hand_histories_grind` - Imported hand histories
- `crypto_wallets` - User cryptocurrency wallets
- `crypto_prices` - Historical price data
- `session_stats` - Aggregated session statistics

## Architecture

```
Poker-Coach-Grind/
├── api/              # FastAPI routes
├── models/           # Data models and schemas
├── database/         # Database setup and migrations
├── crypto/           # Cryptocurrency integrations
├── ui/               # Streamlit UI components
└── cli/              # Command-line interface
```

## Configuration

Create a `.env` file with:

```bash
DATABASE_URL=sqlite:///poker_grind.db
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
COINGECKO_API_KEY=your_key_here
```

## Usage Examples

### Track a Cash Game Session
```python
from Poker-Coach-Grind.models.bankroll import BankrollTracker

tracker = BankrollTracker(user_id="user123")
tracker.add_transaction(
    amount=250.00,
    transaction_type="cash_game",
    stakes="1/2",
    notes="Good session at local casino"
)
```

### Query Hand Histories
```python
from Poker-Coach-Grind.api.hands import query_hands

hands = query_hands(
    user_id="user123",
    sql_query="""
        SELECT * FROM hand_histories_grind 
        WHERE stakes = '1/2' 
        AND date_played >= '2026-01-01'
        AND won_amount > 0
        ORDER BY date_played DESC
    """
)
```

### Track Crypto Winnings
```python
from Poker-Coach-Grind.crypto.tracker import CryptoTracker

tracker = CryptoTracker(user_id="user123")
tracker.add_wallet("ethereum", "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb")
tracker.add_wallet("solana", "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs")

portfolio = tracker.get_portfolio_value()
print(f"Total crypto value: ${portfolio['total_usd']:.2f}")
```

## Integration with Therapy Rex

Poker-Coach-Grind integrates seamlessly with the Therapy Rex mental game coaching system:
- Session statistics feed into tilt detection
- Downswing alerts trigger therapeutic interventions
- Bankroll management rules enforcement
- Performance analytics for coaching insights

## n8n Workflow Automation

Poker-Coach-Grind includes powerful n8n workflow integration for automation:

### Automated Workflows
- **Bankroll Tracking**: Auto-log transactions from multiple sources
- **Hand History Processing**: Automatically import and analyze hands
- **Crypto Portfolio Monitoring**: Track prices and wallet balances
- **Therapy Rex Triggers**: Auto-initiate coaching sessions based on performance
- **Multi-Platform Aggregation**: Combine data from different poker sites

### Webhook Endpoints
```
POST /api/n8n/webhook/bankroll-transaction
POST /api/n8n/webhook/hand-import
POST /api/n8n/webhook/crypto-alert
POST /api/n8n/webhook/therapy-session
```

### Example Workflows
See the `n8n-workflows/` directory for ready-to-use workflow examples:
- `bankroll-tracker.json` - Automated bankroll tracking with alerts
- `crypto-portfolio-monitor.json` - Hourly crypto portfolio monitoring
- `therapy-rex-trigger.json` - Smart therapy session triggering

For complete n8n integration guide, see [n8n-workflows/README.md](n8n-workflows/README.md)

## License

MIT License - See main repository LICENSE file
