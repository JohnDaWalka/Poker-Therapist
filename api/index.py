"""Vercel serverless function handler for FastAPI application."""

import sys
import os

# Ensure the project root is on sys.path so `backend` package is importable
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from backend.api.main import app  # noqa: E402

# Vercel expects a handler
handler = app
