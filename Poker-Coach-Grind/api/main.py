"""FastAPI application for Poker-Coach-Grind."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..database.session import init_database
from .bankroll import router as bankroll_router
from .crypto import router as crypto_router
from .hands import router as hands_router
from .n8n_integration import router as n8n_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    # Startup: Initialize database
    await init_database()
    yield
    # Shutdown: Cleanup if needed


app = FastAPI(
    title="Poker-Coach-Grind API",
    description="Bankroll tracker and hand history reviewer with cryptocurrency integration",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(bankroll_router, prefix="/api/bankroll", tags=["Bankroll"])
app.include_router(hands_router, prefix="/api/hands", tags=["Hand History"])
app.include_router(crypto_router, prefix="/api/crypto", tags=["Cryptocurrency"])
app.include_router(n8n_router, prefix="/api/n8n", tags=["n8n Integration"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Poker-Coach-Grind API",
        "version": "1.0.0",
        "endpoints": {
            "bankroll": "/api/bankroll",
            "hands": "/api/hands",
            "crypto": "/api/crypto",
            "n8n": "/api/n8n",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
