#!/bin/bash
# Quick Start Script for Poker Training Suite

echo "============================================"
echo "   Poker Training Suite - Quick Start"
echo "============================================"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo "Starting Poker Training Suite..."
echo ""
echo "Available interfaces:"
echo "  Main Training:      http://localhost:5000"
echo "  Advanced Tools:     http://localhost:5000/advanced"
echo "  HUD Overlay:        http://localhost:5000/hud"
echo "  Simple Calculator:  http://localhost:5001 (run: python web_ui.py)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 poker_server.py
