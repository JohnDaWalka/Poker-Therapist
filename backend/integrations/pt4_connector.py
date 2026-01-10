"""PokerTracker 4 PostgreSQL database connector.

This module provides integration with PokerTracker 4's PostgreSQL database
to read hand histories, player statistics, and session data for analysis
by Therapy Rex.

PT4 Database Connection Details:
- Default Host: localhost
- Default Port: 5432
- Default Database: PT4 DB
- User: postgres (or custom)
- Password: Set during PT4 installation
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


@dataclass
class PT4Config:
    """PokerTracker 4 database configuration."""
    host: str = "localhost"
    port: int = 5432
    database: str = "PT4 DB"
    user: str = "postgres"
    password: str = ""
    
    @classmethod
    def from_env(cls) -> PT4Config:
        """Load PT4 configuration from environment variables."""
        return cls(
            host=os.getenv("PT4_DB_HOST", "localhost"),
            port=int(os.getenv("PT4_DB_PORT", "5432")),
            database=os.getenv("PT4_DB_NAME", "PT4 DB"),
            user=os.getenv("PT4_DB_USER", "postgres"),
            password=os.getenv("PT4_DB_PASSWORD", ""),
        )


@dataclass
class PT4HandSummary:
    """Summary of a hand from PT4 database."""
    hand_id: str
    site_name: str
    game_type: str
    stakes: str
    date_played: datetime
    player_name: str
    position: Optional[str]
    hole_cards: Optional[str]
    board: Optional[str]
    won_amount: Optional[float]
    pot_size: Optional[float]
    raw_text: Optional[str]


class PT4Connector:
    """Connector for PokerTracker 4 PostgreSQL database."""
    
    def __init__(self, config: Optional[PT4Config] = None):
        """Initialize PT4 connector.
        
        Args:
            config: PT4 database configuration. If None, loads from environment.
        
        Raises:
            ImportError: If psycopg2 is not installed.
        """
        if not PSYCOPG2_AVAILABLE:
            raise ImportError(
                "psycopg2 is required for PT4 integration. "
                "Install with: pip install psycopg2-binary"
            )
        
        self.config = config or PT4Config.from_env()
        self._conn = None
    
    def connect(self) -> None:
        """Establish connection to PT4 database."""
        self._conn = psycopg2.connect(
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
            user=self.config.user,
            password=self.config.password,
        )
    
    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def __enter__(self) -> PT4Connector:
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
    
    def test_connection(self) -> bool:
        """Test if connection to PT4 database is working.
        
        Returns:
            True if connection successful, False otherwise.
        """
        try:
            with self._conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()
                return version is not None
        except Exception:
            return False
    
    def get_player_names(self) -> list[str]:
        """Get list of player names in the database.
        
        Returns:
            List of player names.
        """
        query = """
            SELECT DISTINCT player_name
            FROM player
            WHERE player_name IS NOT NULL
            ORDER BY player_name
        """
        
        with self._conn.cursor() as cur:
            cur.execute(query)
            return [row[0] for row in cur.fetchall()]
    
    def get_recent_hands(
        self,
        player_name: str,
        limit: int = 100,
        site_filter: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Get recent hands for a player.
        
        Args:
            player_name: Player name to filter by.
            limit: Maximum number of hands to return.
            site_filter: Optional site name filter (e.g., 'Americas Cardroom').
        
        Returns:
            List of hand dictionaries with parsed data.
        """
        query = """
            SELECT 
                h.id_hand,
                s.site_name,
                gt.game_type_name,
                h.amt_bb,
                h.date_played,
                p.player_name,
                chps.position,
                chps.holecards,
                h.board,
                chps.amt_won,
                h.amt_pot,
                h.str_aggressors,
                h.str_actors
            FROM cash_hand_player_statistics chps
            JOIN player p ON chps.id_player = p.id_player
            JOIN cash_hand_summary h ON chps.id_hand = h.id_hand
            JOIN game_type gt ON h.id_gametype = gt.id_gametype
            JOIN sitename s ON h.id_site = s.id_site
            WHERE p.player_name = %s
        """
        
        params = [player_name]
        
        if site_filter:
            query += " AND s.site_name = %s"
            params.append(site_filter)
        
        query += """
            ORDER BY h.date_played DESC
            LIMIT %s
        """
        params.append(limit)
        
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]
    
    def get_hands_by_session(
        self,
        player_name: str,
        session_start: datetime,
        session_end: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """Get hands for a player within a session time range.
        
        Args:
            player_name: Player name to filter by.
            session_start: Session start time.
            session_end: Session end time. If None, uses current time.
        
        Returns:
            List of hand dictionaries.
        """
        if session_end is None:
            session_end = datetime.utcnow()
        
        query = """
            SELECT 
                h.id_hand,
                s.site_name,
                gt.game_type_name,
                h.amt_bb,
                h.date_played,
                p.player_name,
                chps.position,
                chps.holecards,
                h.board,
                chps.amt_won,
                h.amt_pot,
                h.str_aggressors,
                h.str_actors
            FROM cash_hand_player_statistics chps
            JOIN player p ON chps.id_player = p.id_player
            JOIN cash_hand_summary h ON chps.id_hand = h.id_hand
            JOIN game_type gt ON h.id_gametype = gt.id_gametype
            JOIN sitename s ON h.id_site = s.id_site
            WHERE p.player_name = %s
                AND h.date_played >= %s
                AND h.date_played <= %s
            ORDER BY h.date_played ASC
        """
        
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (player_name, session_start, session_end))
            return [dict(row) for row in cur.fetchall()]
    
    def get_hand_history_text(self, hand_id: int) -> Optional[str]:
        """Get the raw hand history text for a specific hand.
        
        Args:
            hand_id: PT4 hand ID.
        
        Returns:
            Raw hand history text, or None if not found.
        """
        query = """
            SELECT history
            FROM cash_hand_histories
            WHERE id_hand = %s
        """
        
        with self._conn.cursor() as cur:
            cur.execute(query, (hand_id,))
            result = cur.fetchone()
            return result[0] if result else None
    
    def get_session_stats(
        self,
        player_name: str,
        session_start: datetime,
        session_end: Optional[datetime] = None,
    ) -> dict[str, Any]:
        """Get aggregated statistics for a session.
        
        Args:
            player_name: Player name.
            session_start: Session start time.
            session_end: Session end time. If None, uses current time.
        
        Returns:
            Dictionary with session statistics.
        """
        if session_end is None:
            session_end = datetime.utcnow()
        
        query = """
            SELECT 
                COUNT(*) as hands_played,
                SUM(chps.amt_won) as total_won,
                AVG(chps.amt_won) as avg_won_per_hand,
                SUM(CASE WHEN chps.amt_won > 0 THEN 1 ELSE 0 END) as hands_won,
                AVG(h.amt_pot) as avg_pot_size
            FROM cash_hand_player_statistics chps
            JOIN player p ON chps.id_player = p.id_player
            JOIN cash_hand_summary h ON chps.id_hand = h.id_hand
            WHERE p.player_name = %s
                AND h.date_played >= %s
                AND h.date_played <= %s
        """
        
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (player_name, session_start, session_end))
            result = cur.fetchone()
            return dict(result) if result else {}
    
    def get_sites(self) -> list[dict[str, Any]]:
        """Get list of poker sites in the database.
        
        Returns:
            List of site dictionaries with id and name.
        """
        query = """
            SELECT id_site, site_name
            FROM sitename
            ORDER BY site_name
        """
        
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return [dict(row) for row in cur.fetchall()]


def convert_pt4_hand_to_summary(pt4_hand: dict[str, Any]) -> PT4HandSummary:
    """Convert PT4 hand dictionary to standardized summary.
    
    Args:
        pt4_hand: Hand data from PT4 database query.
    
    Returns:
        PT4HandSummary object.
    """
    return PT4HandSummary(
        hand_id=str(pt4_hand.get("id_hand", "")),
        site_name=pt4_hand.get("site_name", ""),
        game_type=pt4_hand.get("game_type_name", ""),
        stakes=f"${pt4_hand.get('amt_bb', 0) / 2}/{pt4_hand.get('amt_bb', 0)}",
        date_played=pt4_hand.get("date_played", datetime.utcnow()),
        player_name=pt4_hand.get("player_name", ""),
        position=pt4_hand.get("position"),
        hole_cards=pt4_hand.get("holecards"),
        board=pt4_hand.get("board"),
        won_amount=float(pt4_hand.get("amt_won", 0)) if pt4_hand.get("amt_won") else None,
        pot_size=float(pt4_hand.get("amt_pot", 0)) if pt4_hand.get("amt_pot") else None,
        raw_text=None,
    )
