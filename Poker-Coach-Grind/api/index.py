"""Vercel serverless function handler for Poker-Coach-Grind FastAPI application.

This module serves as the entry point for Vercel's Python runtime.
When deployed to Vercel with the root directory set to Poker-Coach-Grind,
this file will be at api/index.py and can directly import from the api module.
"""

# Import the FastAPI app from main.py in the same directory
from .main import app

# Export the ASGI application for Vercel
handler = app

# Alternative exports for better framework detection
__all__ = ["app", "handler"]
