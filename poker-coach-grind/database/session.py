"""Database session management for Poker-Coach-Grind."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

# Get database URL from environment or use default
DATABASE_URL = os.getenv("GRIND_DATABASE_URL", "sqlite+aiosqlite:///poker_grind.db")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

# Create async session maker
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_database():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_grind_db() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session.
    
    Usage:
        async with get_grind_db() as db:
            # Use db for queries
            result = await db.execute(...)
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
