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
import logging

# Setup paths for proper package imports when running in Vercel
# Vercel sets cwd to the project root (Poker-Coach-Grind)
project_root = Path(__file__).parent.parent.absolute()
parent_of_root = project_root.parent

# Get package name from directory name, handling hyphens
package_name = project_root.name

# Add both paths to ensure imports work
for path in [str(project_root), str(parent_of_root)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Create a proper package context by loading the package
# This allows relative imports to work correctly
if package_name not in sys.modules:
    # Create empty package modules to establish the package hierarchy
    import types
    
    # Create the top-level package
    pkg = types.ModuleType(package_name)
    pkg.__package__ = package_name
    pkg.__path__ = [str(project_root)]
    sys.modules[package_name] = pkg
    
    # Create the api subpackage
    api_pkg = types.ModuleType(f'{package_name}.api')
    api_pkg.__package__ = f'{package_name}.api'
    api_pkg.__path__ = [str(project_root / 'api')]
    sys.modules[f'{package_name}.api'] = api_pkg
    
    # Create the database subpackage
    db_pkg = types.ModuleType(f'{package_name}.database')
    db_pkg.__package__ = f'{package_name}.database'
    db_pkg.__path__ = [str(project_root / 'database')]
    sys.modules[f'{package_name}.database'] = db_pkg

# Now we can import main which has relative imports
app = None
handler = None

try:
    # Load the main module with proper package context
    main_file = project_root / 'api' / 'main.py'
    
    if not main_file.exists():
        raise FileNotFoundError(f"Main module not found at {main_file}")
    
    spec = importlib.util.spec_from_file_location(
        f'{package_name}.api.main',
        main_file,
        submodule_search_locations=[str(project_root / 'api')]
    )
    
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to create spec for main module at {main_file}")
    
    main_module = importlib.util.module_from_spec(spec)
    main_module.__package__ = f'{package_name}.api'
    sys.modules[f'{package_name}.api.main'] = main_module
    spec.loader.exec_module(main_module)
    
    # Safely get the app attribute
    if not hasattr(main_module, 'app'):
        raise AttributeError("Main module does not have an 'app' attribute")
    
    app = main_module.app
    handler = main_module.app
    
except Exception as e:
    # Fallback: Create a simple FastAPI app with error message
    from fastapi import FastAPI

    # Log the exception with stack trace on the server side
    logger = logging.getLogger(__name__)
    logger.exception("Failed to load main application", exc_info=e)
    
    # Return a generic error message without exposing internal details
    app = FastAPI(title="Poker-Coach-Grind API (Import Error)")
    handler = app
    
    @app.get("/")
    async def root():
        # Do not expose the raw exception; report a generic degraded status
        return {"status": "degraded", "error": "Initialization failure"}
    
    @app.get("/health")
    async def health():
        return {"status": "degraded", "error": "Initialization failure"}

# Alternative exports for better framework detection
__all__ = ["app", "handler"]
