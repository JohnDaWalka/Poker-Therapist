"""Vercel serverless function handler for Poker-Coach-Grind FastAPI application.

This module serves as the entry point for Vercel's Python runtime.
With the experimental framework preset (PR #14646), Vercel can automatically
detect and optimize ASGI applications like FastAPI.
"""

import sys
from pathlib import Path
import importlib

# Add the project root to sys.path to enable proper module imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the Poker-Coach-Grind API module
# Using importlib to handle the hyphenated directory name
grind_api = importlib.import_module('Poker-Coach-Grind.api.main')

# Get the FastAPI app instance
app = grind_api.app

# Export the ASGI application
# Vercel's experimental framework preset automatically detects 'app' as the ASGI application
# The handler name is maintained for backward compatibility
handler = app

# Alternative exports for better framework detection
__all__ = ["app", "handler"]



