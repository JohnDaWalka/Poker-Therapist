"""Vercel serverless function handler for Poker-Coach-Grind routes.

This is a lightweight proxy that forwards /grind requests to the main API.
For now, this returns a simple redirect or informational response.
The full Poker-Coach-Grind functionality should be accessed through dedicated deployment.
"""

from fastapi import FastAPI
import sys
from pathlib import Path
import importlib

app = FastAPI(
    title="Poker-Coach-Grind Gateway",
    description="Gateway to Poker-Coach-Grind functionality",
    version="1.0.0",
    redirect_slashes=True
)

@app.get("/grind")
async def grind_root():
    """Root endpoint for grind routes."""
    return {
        "name": "Poker-Coach-Grind Gateway",
        "message": "Poker-Coach-Grind API gateway",
        "status": "operational",
        "note": "For full Poker-Coach-Grind functionality, deploy separately or access via dedicated endpoint",
        "available_endpoints": {
            "health": "/grind/health",
            "info": "/grind/info"
        }
    }
# Import the Poker-Coach-Grind API module
# Using importlib to handle the hyphenated directory name
try:
    grind_api = importlib.import_module('Poker-Coach-Grind.api.main')
    app = grind_api.app
except (ImportError, AttributeError) as e:
    # Log the error immediately for visibility in Vercel logs
    logging.exception(f"Failed to import Poker-Coach-Grind API: {e}")
    
    # Create a minimal error response app
    # If the module or app cannot be imported, create a minimal error response
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
    
    # Re-raise the error for visibility in Vercel logs
    import logging
    logging.error(f"Failed to import Poker-Coach-Grind API: {e}")

@app.get("/grind/health")
async def health():
    """Health check endpoint for grind service."""
    return {"status": "healthy", "service": "poker-coach-grind-gateway"}

@app.get("/grind/info")
async def info():
    """Information about Poker-Coach-Grind."""
    return {
        "service": "Poker-Coach-Grind",
        "description": "Bankroll tracker and hand history reviewer with cryptocurrency integration",
        "features": [
            "Bankroll tracking",
            "Hand history analysis",
            "Cryptocurrency wallet tracking",
            "n8n webhook integration"
        ],
        "deployment_note": "Full API available at dedicated Poker-Coach-Grind deployment"
    }

# Export for Vercel
handler = app
__all__ = ["app", "handler"]
