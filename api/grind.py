"""Vercel serverless function handler for Poker-Coach-Grind FastAPI application.

This module serves as the entry point for Vercel's Python runtime.
With the experimental framework preset (PR #14646), Vercel can automatically
detect and optimize ASGI applications like FastAPI.
"""

import sys
from pathlib import Path
import importlib
import logging

# Add the project root to sys.path to enable proper module imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the Poker-Coach-Grind API module
# Using importlib to handle the hyphenated directory name
try:
    grind_api = importlib.import_module('Poker-Coach-Grind.api.main')
    app = grind_api.app
except (ImportError, AttributeError) as e:
    # Log the error immediately for visibility in Vercel logs
    logging.exception(f"Failed to import Poker-Coach-Grind API: {e}")
    
    # Create a minimal error response app
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="Poker-Coach-Grind API (Error)")
    
    @app.get("/")
    async def error_root():
        return JSONResponse(
            status_code=500,
            content={
                "error": "Failed to load Poker-Coach-Grind API",
                "detail": str(e),
                "message": "Please check the application logs"
            }
        )

# Export the ASGI application
# Vercel's experimental framework preset automatically detects 'app' as the ASGI application
# The handler name is maintained for backward compatibility
handler = app

# Alternative exports for better framework detection
__all__ = ["app", "handler"]
