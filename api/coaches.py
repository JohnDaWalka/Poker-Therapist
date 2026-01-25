"""Vercel serverless function handler for Poker-Coach-Grind API.

This module serves as the entry point for the Poker-Coach-Grind API
(Versace Poker coaches) deployment on Vercel.

Note: Requires Poker_Coach_Grind symlink to Poker-Coach-Grind directory
for Python package compatibility.
"""

from Poker_Coach_Grind.api.main import app

# Export the ASGI application
# Vercel's experimental framework preset automatically detects 'app' as the ASGI application
handler = app

# Alternative exports for better framework detection
__all__ = ["app", "handler"]
