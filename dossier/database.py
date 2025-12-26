"""Database operations for dossier storage."""

import json
import os
from datetime import UTC, datetime
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from dossier.models import Dossier


class DossierDatabase:
    """Manages PostgreSQL database operations for dossiers."""

    def __init__(self, connection_string: str | None = None) -> None:
        """Initialize database connection."""
        self.connection_string = connection_string or os.getenv(
            "DATABASE_URL",
            "postgresql://localhost:5432/poker_therapist",
        )
        self._create_tables()

    def _get_connection(self) -> psycopg2.extensions.connection:
        """Get database connection."""
        return psycopg2.connect(self.connection_string)

    def _create_tables(self) -> None:
        """Create dossier table if it doesn't exist."""
        with self._get_connection() as conn, conn.cursor() as cursor:
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS dossiers (
                        id VARCHAR(255) PRIMARY KEY,
                        player_name VARCHAR(255) NOT NULL,
                        data JSONB NOT NULL DEFAULT '{}',
                        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                    )
                """)
            conn.commit()

    def get(self, dossier_id: str) -> Dossier | None:
        """Retrieve a dossier by ID."""
        with (
            self._get_connection() as conn,
            conn.cursor(cursor_factory=RealDictCursor) as cursor,
        ):
            cursor.execute(
                "SELECT * FROM dossiers WHERE id = %s",
                (dossier_id,),
            )
            row = cursor.fetchone()
            if row:
                return Dossier.from_dict(dict(row))
            return None

    def create(self, dossier: Dossier) -> Dossier:
        """Create a new dossier."""
        with self._get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                    INSERT INTO dossiers (id, player_name, data, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                (
                    dossier.id,
                    dossier.player_name,
                    json.dumps(dossier.data),
                    dossier.created_at,
                    dossier.updated_at,
                ),
            )
            conn.commit()
        return dossier

    def update(self, dossier_id: str, data: dict[str, Any]) -> Dossier | None:
        """Update a dossier with new data."""
        dossier = self.get(dossier_id)
        if not dossier:
            return None

        dossier.data = data
        dossier.updated_at = datetime.now(UTC)

        with self._get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                    UPDATE dossiers
                    SET data = %s, updated_at = %s
                    WHERE id = %s
                    """,
                (json.dumps(dossier.data), dossier.updated_at, dossier_id),
            )
            conn.commit()
        return dossier

    def delete(self, dossier_id: str) -> bool:
        """Delete a dossier."""
        with self._get_connection() as conn, conn.cursor() as cursor:
            cursor.execute("DELETE FROM dossiers WHERE id = %s", (dossier_id,))
            conn.commit()
            rowcount: int = cursor.rowcount or 0
            return rowcount > 0

    def list_all(self) -> list[Dossier]:
        """List all dossiers."""
        with (
            self._get_connection() as conn,
            conn.cursor(cursor_factory=RealDictCursor) as cursor,
        ):
            cursor.execute("SELECT * FROM dossiers ORDER BY updated_at DESC")
            rows = cursor.fetchall()
            return [Dossier.from_dict(dict(row)) for row in rows]
