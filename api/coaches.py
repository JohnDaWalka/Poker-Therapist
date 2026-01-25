"""Vercel serverless function handler for Poker-Coach-Grind API.

This module serves as the entry point for the Poker-Coach-Grind API
(Versace Poker coaches) deployment on Vercel.
"""

import sys
from pathlib import Path

# Add Poker-Coach-Grind to Python path for imports
project_root = Path(__file__).parent.parent
grind_path = project_root / "Poker-Coach-Grind"
sys.path.insert(0, str(grind_path))

from api.main import app

# Export the ASGI application
# Vercel's experimental framework preset automatically detects 'app' as the ASGI application
handler = app

# Alternative exports for better framework detection
__all__ = ["app", "handler"]
