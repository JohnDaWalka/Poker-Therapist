"""Vercel serverless function handler for FastAPI application."""

from backend.api.main import app

# Vercel expects a handler
handler = app
