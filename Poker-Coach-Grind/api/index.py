"""Vercel serverless function handler for Poker-Coach-Grind FastAPI application.

This module serves as the entry point for Vercel's Python runtime.
When deployed to Vercel with the root directory set to Poker-Coach-Grind,
this file will be at api/index.py and needs to handle imports correctly.

For Vercel deployment, we import from the main.py file which has all the proper
relative imports configured. We just need to ensure the package context is correct.
"""

import sys
import os
from pathlib import Path
import importlib.util

# Setup paths for proper package imports when running in Vercel
# Vercel sets cwd to the project root (Poker-Coach-Grind)
project_root = Path(__file__).parent.parent.absolute()
parent_of_root = project_root.parent

# Add both paths to ensure imports work
for path in [str(project_root), str(parent_of_root)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Create a proper package context by loading the Poker-Coach-Grind package
# This allows relative imports to work correctly
if 'Poker-Coach-Grind' not in sys.modules:
    # Create empty package modules to establish the package hierarchy
    import types
    
    # Create the top-level package
    pkg = types.ModuleType('Poker-Coach-Grind')
    pkg.__package__ = 'Poker-Coach-Grind'
    pkg.__path__ = [str(project_root)]
    sys.modules['Poker-Coach-Grind'] = pkg
    
    # Create the api subpackage
    api_pkg = types.ModuleType('Poker-Coach-Grind.api')
    api_pkg.__package__ = 'Poker-Coach-Grind.api'
    api_pkg.__path__ = [str(project_root / 'api')]
    sys.modules['Poker-Coach-Grind.api'] = api_pkg
    
    # Create the database subpackage
    db_pkg = types.ModuleType('Poker-Coach-Grind.database')
    db_pkg.__package__ = 'Poker-Coach-Grind.database'
    db_pkg.__path__ = [str(project_root / 'database')]
    sys.modules['Poker-Coach-Grind.database'] = db_pkg

# Now we can import main which has relative imports
try:
    # Load the main module with proper package context
    spec = importlib.util.spec_from_file_location(
        'Poker-Coach-Grind.api.main',
        project_root / 'api' / 'main.py',
        submodule_search_locations=[str(project_root / 'api')]
    )
    main_module = importlib.util.module_from_spec(spec)
    main_module.__package__ = 'Poker-Coach-Grind.api'
    sys.modules['Poker-Coach-Grind.api.main'] = main_module
    spec.loader.exec_module(main_module)
    
    app = main_module.app
    handler = main_module.app
    
except Exception as e:
    # Fallback: Create a simple FastAPI app with error message
    from fastapi import FastAPI
    
    app = FastAPI(title="Poker-Coach-Grind API (Import Error)")
    handler = app
    
    @app.get("/")
    async def root():
        return {
            "error": "Failed to load main application",
            "message": str(e),
            "note": "Check import configuration and dependencies"
        }
    
    @app.get("/health")
    async def health():
        return {"status": "degraded", "error": str(e)}

# Alternative exports for better framework detection
__all__ = ["app", "handler"]
