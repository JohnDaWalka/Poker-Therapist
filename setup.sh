#!/bin/bash
# Quick setup script for Poker Therapist Voice Integration

set -e

echo "=================================="
echo "Poker Therapist Voice Setup 🎰🎤"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $python_version"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"
echo ""

# Check for API keys
echo "Checking API keys..."
if [ -z "$XAI_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  No API keys found in environment"
    echo ""
    echo "Please set your API keys:"
    echo "  export XAI_API_KEY='xai-your-key-here'"
    echo "  export OPENAI_API_KEY='sk-your-key-here'"
    echo ""
    echo "Or create a .env file with:"
    echo "  XAI_API_KEY=xai-your-key-here"
    echo "  OPENAI_API_KEY=sk-your-key-here"
    echo ""
else
    if [ ! -z "$XAI_API_KEY" ]; then
        echo "✅ XAI_API_KEY found"
    fi
    if [ ! -z "$OPENAI_API_KEY" ]; then
        echo "✅ OPENAI_API_KEY found"
    fi
fi
echo ""

# Create .streamlit directory if it doesn't exist
if [ ! -d ".streamlit" ]; then
    echo "Creating .streamlit directory..."
    mkdir -p .streamlit
    echo "✅ .streamlit directory created"
fi
echo ""

# Check if secrets.toml exists
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "⚠️  .streamlit/secrets.toml not found"
    echo "Creating from environment variables..."
    
    cat > .streamlit/secrets.toml << EOF
# Streamlit secrets file
# Add your API keys here

XAI_API_KEY = "${XAI_API_KEY:-your_xai_api_key_here}"
OPENAI_API_KEY = "${OPENAI_API_KEY:-your_openai_api_key_here}"

ENABLE_STREAMING = true
ENABLE_THINKING = true
EOF
    echo "✅ .streamlit/secrets.toml created"
    echo "   Please edit .streamlit/secrets.toml to add your API keys"
else
    echo "✅ .streamlit/secrets.toml already exists"
fi
echo ""

echo "=================================="
echo "Setup Complete! 🎉"
echo "=================================="
echo ""
echo "To start the application:"
echo "  1. Activate venv: source venv/bin/activate"
echo "  2. Set API keys (if not already set)"
echo "  3. Run: streamlit run chatbot_app.py"
echo ""
echo "For voice features, you'll need:"
echo "  - XAI_API_KEY for Grok chat"
echo "  - OPENAI_API_KEY for voice (TTS/STT)"
echo ""
echo "See VOICE_INTEGRATION.md for detailed setup guide"
echo ""
