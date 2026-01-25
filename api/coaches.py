"""Vercel serverless function handler for Poker-Coach-Grind API.

This module serves as the entry point for the Poker-Coach-Grind API
(Versace Poker coaches) deployment on Vercel.

Requirements:
- Poker_Coach_Grind symlink → Poker-Coach-Grind (tracked in Git)
- This symlink enables Python to import the package (directory names with hyphens
  are not valid Python package names)
"""

from Poker_Coach_Grind.api.main import app

# Export the ASGI application
# Vercel's experimental framework preset automatically detects 'app' as the ASGI application
handler = app

# Alternative exports for better framework detection
__all__ = ["app", "handler"]
