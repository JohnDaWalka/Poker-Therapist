"""Configuration tests for PostgreSQL default URL."""

import importlib
import os


def test_default_postgres_port(monkeypatch):
    """Default builder should use PokerTracker port 5432 when unspecified."""
    # Clear env that influence DB URL
    for key in [
        "DATABASE_URL",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
    ]:
        monkeypatch.delenv(key, raising=False)

    from backend.agent.memory import db_session

    importlib.reload(db_session)

    url = db_session._build_default_postgres_url()
    assert ":5432/" in url
    assert url.startswith("postgresql+asyncpg://")
