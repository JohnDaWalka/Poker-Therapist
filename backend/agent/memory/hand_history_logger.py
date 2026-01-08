"""Utilities for logging PokerTracker hand histories."""

from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agent.memory.database import HandHistory
from backend.agent.memory.db_session import get_db

DEFAULT_SOURCE = "PokerTracker"
DEFAULT_SOURCE_VERSION = "4.18.16"


async def log_hand_history_entry(
    *,
    user_id: str,
    hand_history: str,
    emotional_context: str = "",
    hand_id: Optional[str] = None,
    analysis: Optional[Dict[str, Any]] = None,
    source: str = DEFAULT_SOURCE,
    source_version: str = DEFAULT_SOURCE_VERSION,
) -> int:
    """Persist a PokerTracker 4.18.16 hand history entry.

    Args:
        user_id: User identifier
        hand_history: Raw hand history text
        emotional_context: Optional emotional notes
        hand_id: Optional hand identifier from tracker
        analysis: Optional analysis payload (gto/meta/hud/models)
        source: Data source name
        source_version: Data source version (defaults to PokerTracker 4.18.16)

    Returns:
        Database row ID of the persisted hand history
    """
    payload = analysis or {}

    async with get_db() as db:
        entry = HandHistory(
            user_id=user_id,
            source=source or DEFAULT_SOURCE,
            source_version=source_version or DEFAULT_SOURCE_VERSION,
            hand_id=hand_id,
            hand_history=hand_history,
            emotional_context=emotional_context,
            gto_analysis=payload.get("gto_analysis"),
            meta_context=payload.get("meta_context"),
            hud_insights=payload.get("hud_insights"),
            models=payload.get("models"),
        )
        db.add(entry)
        await db.flush()
        await db.commit()
        return entry.id


async def fetch_hand_histories(
    db: AsyncSession, user_id: str, limit: int = 20
) -> list[HandHistory]:
    """Fetch recent hand histories for a user."""
    result = await db.execute(
        select(HandHistory)
        .where(HandHistory.user_id == user_id)
        .order_by(HandHistory.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
