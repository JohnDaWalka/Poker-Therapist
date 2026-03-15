"""
Player Stats Cache
==================
SQLite-backed storage for per-player poker statistics.

Schema (table: player_stats_cache):
    player_id   TEXT PRIMARY KEY
    vpip        REAL   – Voluntarily put money in pot (%)
    pfr         REAL   – Pre-flop raise (%)
    threebet    REAL   – Pre-flop 3-bet (%)
    af          REAL   – Aggression factor
    wtsd        REAL   – Went to showdown (%)
    hands       INTEGER – Total hands observed
    player_style TEXT  – Archetype label from classifier
    last_updated TEXT  – ISO-8601 UTC timestamp

Whenever stats are written the classifier runs automatically and the
``player_style`` column is kept up to date.

Usage:
    from player_stats_cache import PlayerStatsCache

    cache = PlayerStatsCache()                      # default: poker_stats.db
    cache.update_stats("Villain_87", vpip=31, pfr=24, threebet=9, hands=842)
    stats = cache.get_player_stats("Villain_87")
    print(stats["player_style"])                    # "LAG"

    cache.refresh_styles()                          # rerun classifier on all rows
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

from player_classifier import classify_player

# ---------------------------------------------------------------------------
# Default database location
# ---------------------------------------------------------------------------

DEFAULT_DB_PATH = Path(__file__).parent / "poker_stats.db"

# ---------------------------------------------------------------------------
# DDL
# ---------------------------------------------------------------------------

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS player_stats_cache (
    player_id    TEXT    PRIMARY KEY,
    vpip         REAL    NOT NULL DEFAULT 0,
    pfr          REAL    NOT NULL DEFAULT 0,
    threebet     REAL    NOT NULL DEFAULT 0,
    af           REAL    NOT NULL DEFAULT 0,
    wtsd         REAL    NOT NULL DEFAULT 0,
    hands        INTEGER NOT NULL DEFAULT 0,
    player_style TEXT,
    last_updated TEXT    NOT NULL
)
"""

_ADD_STYLE_COLUMN_SQL = """
ALTER TABLE player_stats_cache
ADD COLUMN player_style TEXT
"""


# ---------------------------------------------------------------------------
# Cache class
# ---------------------------------------------------------------------------

class PlayerStatsCache:
    """Manages the player stats SQLite cache with automatic style classification.

    Args:
        db_path: Path to the SQLite database file.  Created on first use.
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self._db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self._init_db()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Create the table and ensure the player_style column exists."""
        with self._connect() as conn:
            conn.execute(_CREATE_TABLE_SQL)
            # Idempotent: add column only when it doesn't already exist
            existing = {
                row[1]
                for row in conn.execute("PRAGMA table_info(player_stats_cache)")
            }
            if "player_style" not in existing:
                conn.execute(_ADD_STYLE_COLUMN_SQL)
            conn.commit()

    @staticmethod
    def _now_utc() -> str:
        return datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update_stats(
        self,
        player_id: str,
        *,
        vpip: float = 0.0,
        pfr: float = 0.0,
        threebet: float = 0.0,
        af: float = 0.0,
        wtsd: float = 0.0,
        hands: int = 0,
    ) -> Dict[str, Any]:
        """Insert or replace stats for *player_id*, then classify and persist style.

        Args:
            player_id: Unique identifier (screen name, UUID, etc.).
            vpip:      Voluntarily put money in pot (%).
            pfr:       Pre-flop raise (%).
            threebet:  Pre-flop 3-bet (%).
            af:        Aggression factor.
            wtsd:      Went to showdown (%).
            hands:     Total hands observed.

        Returns:
            The full stored row as a plain ``dict``.
        """
        style = classify_player(vpip, pfr, threebet)
        now = self._now_utc()

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO player_stats_cache
                    (player_id, vpip, pfr, threebet, af, wtsd, hands,
                     player_style, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(player_id) DO UPDATE SET
                    vpip         = excluded.vpip,
                    pfr          = excluded.pfr,
                    threebet     = excluded.threebet,
                    af           = excluded.af,
                    wtsd         = excluded.wtsd,
                    hands        = excluded.hands,
                    player_style = excluded.player_style,
                    last_updated = excluded.last_updated
                """,
                (player_id, vpip, pfr, threebet, af, wtsd, hands, style, now),
            )
            conn.commit()

        return self.get_player_stats(player_id)  # type: ignore[return-value]

    def get_player_stats(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Return the stats row for *player_id*, or ``None`` if not found.

        Args:
            player_id: Player identifier.

        Returns:
            A dict with all columns, or ``None``.
        """
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM player_stats_cache WHERE player_id = ?",
                (player_id,),
            ).fetchone()
        return dict(row) if row else None

    def get_all_players(self) -> List[Dict[str, Any]]:
        """Return all rows in the cache, ordered by hands descending.

        Returns:
            List of dicts, one per player.
        """
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM player_stats_cache ORDER BY hands DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def refresh_styles(self) -> int:
        """Re-run the classifier on every row and update ``player_style``.

        Useful after upgrading the classifier thresholds.

        Returns:
            Number of rows updated.
        """
        players = self.get_all_players()
        count = 0
        with self._connect() as conn:
            for player in players:
                new_style = classify_player(
                    player["vpip"], player["pfr"], player["threebet"]
                )
                conn.execute(
                    "UPDATE player_stats_cache SET player_style = ?, last_updated = ? "
                    "WHERE player_id = ?",
                    (new_style, self._now_utc(), player["player_id"]),
                )
                count += 1
            conn.commit()
        return count


# ---------------------------------------------------------------------------
# CLI / self-test
# ---------------------------------------------------------------------------

def _run_tests() -> None:
    """Run built-in player stats cache tests."""
    import tempfile
    import os

    print("Running player stats cache tests...")

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test_stats.db"
        cache = PlayerStatsCache(db_path=db_path)

        # Insert a LAG player
        result = cache.update_stats(
            "Villain_87", vpip=31, pfr=24, threebet=9, af=2.5, wtsd=28, hands=842
        )
        assert result["player_id"] == "Villain_87", "player_id mismatch"
        assert result["player_style"] == "LAG", f"Expected LAG, got {result['player_style']}"
        assert result["hands"] == 842, "hands mismatch"
        print("  ✓ Update stats and classify LAG")

        # Insert a Nit
        cache.update_stats("NitPlayer", vpip=12, pfr=9, threebet=2, hands=300)
        nit = cache.get_player_stats("NitPlayer")
        assert nit is not None, "NitPlayer not found"
        assert nit["player_style"] == "Nit", f"Expected Nit, got {nit['player_style']}"
        print("  ✓ Nit player stored correctly")

        # get_all_players ordering
        all_players = cache.get_all_players()
        assert len(all_players) == 2, f"Expected 2 players, got {len(all_players)}"
        assert all_players[0]["player_id"] == "Villain_87", "Ordering by hands failed"
        print("  ✓ get_all_players returns correct count and ordering")

        # get_player_stats returns None for unknown player
        assert cache.get_player_stats("Ghost") is None, "Expected None for unknown player"
        print("  ✓ get_player_stats returns None for unknown player")

        # refresh_styles after manual stat change
        with cache._connect() as conn:
            conn.execute(
                "UPDATE player_stats_cache SET vpip=50, pfr=8, threebet=2 "
                "WHERE player_id='NitPlayer'"
            )
            conn.commit()
        updated = cache.refresh_styles()
        assert updated == 2, f"Expected 2 updated rows, got {updated}"
        refreshed = cache.get_player_stats("NitPlayer")
        assert refreshed["player_style"] == "Loose Passive", \
            f"Expected Loose Passive after refresh, got {refreshed['player_style']}"
        print("  ✓ refresh_styles reclassifies correctly")

        # Upsert updates existing row
        cache.update_stats("Villain_87", vpip=12, pfr=9, threebet=1, hands=1000)
        updated_row = cache.get_player_stats("Villain_87")
        assert updated_row["player_style"] == "Nit", "Upsert reclassification failed"
        assert updated_row["hands"] == 1000, "Upsert hands mismatch"
        print("  ✓ Upsert updates and reclassifies existing player")

    print("\n✅ All player stats cache tests passed!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        _run_tests()
        sys.exit(0)

    print("Usage:")
    print("  python player_stats_cache.py test   Run tests")
