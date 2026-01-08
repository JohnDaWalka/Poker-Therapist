"""Tests for PokerTracker hand history logging."""

import asyncio
from pathlib import Path

import pytest


@pytest.fixture
def hand_history_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Prepare isolated database for hand history logging."""
    db_url = f"sqlite+aiosqlite:///{tmp_path}/handlogs.db"
    monkeypatch.setenv("DATABASE_URL", db_url)

    import backend.agent.memory.database as database
    import backend.agent.memory.db_session as db_session
    import backend.agent.memory.hand_history_logger as hand_logger

    asyncio.run(db_session.init_db())
    return database, db_session, hand_logger


def test_log_hand_history_persists(hand_history_env) -> None:
    """Ensure PokerTracker hand histories are persisted with metadata."""
    database, db_session, hand_logger = hand_history_env

    async def run() -> None:
        log_id = await hand_logger.log_hand_history_entry(
            user_id="user-123",
            hand_history="PokerStars Hand #123456: Hold'em No Limit ($1/$2)",
            emotional_context="tilted after bad beat",
            analysis={
                "gto_analysis": "Fold turn vs aggression.",
                "meta_context": "Population over-bluffs this node.",
                "hud_insights": "Villain 3-bets 14%.",
                "models": ["perplexity", "openai"],
            },
        )

        async with db_session.get_db() as session:
            record = await session.get(database.HandHistory, log_id)

        assert record is not None
        assert record.user_id == "user-123"
        assert record.source == "PokerTracker"
        assert record.source_version == "4.18.16"
        assert "Hold'em" in record.hand_history
        assert record.emotional_context.startswith("tilted")
        assert record.models == ["perplexity", "openai"]

    asyncio.run(run())
