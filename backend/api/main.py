"""FastAPI main application."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.agent.memory.db_session import init_db
from backend.api.routes import analyze, deep_session, tracking, triage


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.
    
    Args:
        app: FastAPI application
        
    Yields:
        None
    """
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title="Therapy Rex API",
    description="Multi-platform poker mental game coaching system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware - Base origins for local development
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:5173",
]

# Add Vercel origins if deployed on Vercel or if explicitly configured
# VERCEL_URL is automatically set by Vercel and contains the deployment URL without protocol
# (e.g., "my-app-abc123.vercel.app" or "my-app.vercel.app")
vercel_url = os.environ.get("VERCEL_URL")
vercel_project_url = os.environ.get("VERCEL_PROJECT_URL", "poker-therapist.vercel.app")
if vercel_url:
    # Use set to automatically deduplicate if VERCEL_URL equals VERCEL_PROJECT_URL
    vercel_origins = {
        f"https://{vercel_url}",
        f"https://{vercel_project_url}",
    }
    allowed_origins.extend(list(vercel_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(triage.router, prefix="/api", tags=["Triage"])
app.include_router(deep_session.router, prefix="/api", tags=["Deep Session"])
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(tracking.router, prefix="/api", tags=["Tracking"])


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint.
    
    Returns:
        Welcome message
    """
    return {
        "message": "Therapy Rex API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
