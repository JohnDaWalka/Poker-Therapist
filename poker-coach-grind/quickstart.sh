#!/bin/bash
# Quick start script for poker-coach-grind with n8n integration

set -e

echo "=========================================="
echo "poker-coach-grind Quick Start"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from correct directory
if [ ! -d "poker-coach-grind" ]; then
    echo "Error: Please run this script from the repository root"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo "Error: Python 3 is required but not installed"
    exit 1
fi

if ! command_exists pip3; then
    echo "Error: pip3 is required but not installed"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found${NC}"

# Check for Node.js (optional, for n8n)
if command_exists node; then
    echo -e "${GREEN}✓ Node.js found (for n8n)${NC}"
else
    echo -e "${YELLOW}⚠ Node.js not found. Install it to use n8n workflows${NC}"
fi

echo ""

# Install dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip3 install -q -r poker-coach-grind/requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Initialize database
echo -e "${BLUE}Initializing database...${NC}"
python3 -m poker-coach-grind.cli.main init-db
echo -e "${GREEN}✓ Database initialized${NC}"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file not found. Creating from example...${NC}"
    cat > .env << 'EOF'
# poker-coach-grind Configuration
GRIND_DATABASE_URL=sqlite+aiosqlite:///poker_grind.db

# Crypto API Keys (optional)
COINGECKO_API_KEY=
ETHEREUM_RPC_URL=https://eth.llamarpc.com
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com

# n8n Configuration (optional)
N8N_WEBHOOK_URL=http://localhost:5678

# Notifications (optional)
DISCORD_WEBHOOK_URL=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}  → Edit .env to add your API keys${NC}"
else
    echo -e "${GREEN}✓ .env file found${NC}"
fi
echo ""

# Test crypto prices
echo -e "${BLUE}Testing crypto price API...${NC}"
python3 -m poker-coach-grind.cli.main prices ETH,SOL,ONDO 2>/dev/null || echo "Note: Crypto API test skipped (no internet or rate limited)"
echo ""

# Display next steps
echo -e "${GREEN}=========================================="
echo "Setup Complete!"
echo -e "==========================================${NC}"
echo ""
echo -e "${BLUE}Quick Start Commands:${NC}"
echo ""
echo "1. Start the API server:"
echo -e "   ${YELLOW}python3 -m uvicorn poker-coach-grind.api.main:app --reload --port 8001${NC}"
echo ""
echo "2. View API documentation:"
echo -e "   ${YELLOW}http://localhost:8001/docs${NC}"
echo ""
echo "3. Use CLI tools:"
echo -e "   ${YELLOW}python3 -m poker-coach-grind.cli.main help${NC}"
echo ""
echo "4. Start Streamlit UI:"
echo -e "   ${YELLOW}streamlit run poker-coach-grind/ui/grind_app.py${NC}"
echo ""
echo "5. Set up n8n workflows (if Node.js installed):"
echo -e "   ${YELLOW}npx n8n${NC}"
echo -e "   Then import workflows from: ${YELLOW}poker-coach-grind/n8n-workflows/${NC}"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "  • README: poker-coach-grind/README.md"
echo "  • Integration Guide: poker-coach-grind/INTEGRATION_GUIDE.md"
echo "  • n8n Workflows: poker-coach-grind/n8n-workflows/README.md"
echo ""
echo -e "${GREEN}Happy grinding! 🎰💰${NC}"
