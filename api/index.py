"""Vercel serverless function handler for FastAPI application.

This module serves as the entry point for Vercel's Python runtime.
With the experimental framework preset (PR #14646), Vercel can automatically
detect and optimize ASGI applications like FastAPI.
"""

from backend.api.main import app

# Export the ASGI application
# Vercel's experimental framework preset automatically detects 'app' as the ASGI application
# The handler name is maintained for backward compatibility
handler = app

# Alternative exports for better framework detection
__all__ = ["app", "handler"]
