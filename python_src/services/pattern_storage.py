"""SQLite storage for user patterns and conversation context."""

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional


class PatternStorage:
    """
    Storage for user patterns and conversation context in SQLite.
    
    This stores:
    - User behavioral patterns (betting patterns, emotional triggers, etc.)
    - Conversation context and history
    - User preferences and settings
    - Session analytics and insights
    """
    
    def __init__(self, db_path: Path | str = "RexVoice.db") -> None:
        """
        Initialize pattern storage.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._init_tables()
    
    def _init_tables(self) -> None:
        """Initialize database tables for pattern storage."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User patterns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_key TEXT NOT NULL,
                    pattern_value TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, pattern_type, pattern_key)
                )
            """)
            
            # Conversation context table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    context_key TEXT NOT NULL,
                    context_value TEXT NOT NULL,
                    session_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # User insights table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    insight_type TEXT NOT NULL,
                    insight_data TEXT NOT NULL,
                    importance REAL DEFAULT 0.5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_patterns_user_type 
                ON user_patterns(user_id, pattern_type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_context_user 
                ON conversation_context(user_id, session_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_insights_user 
                ON user_insights(user_id, insight_type)
            """)
            
            conn.commit()
    
    def save_pattern(
        self,
        user_id: int,
        pattern_type: str,
        pattern_key: str,
        pattern_value: Any,
        confidence: float = 1.0,
    ) -> None:
        """
        Save or update a user pattern.
        
        Args:
            user_id: User identifier
            pattern_type: Type of pattern (e.g., "betting", "emotion", "preference")
            pattern_key: Pattern key (e.g., "aggression_level", "tilt_trigger")
            pattern_value: Pattern value (will be JSON serialized if not string)
            confidence: Confidence level (0.0 to 1.0)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Serialize value if needed
            if not isinstance(pattern_value, str):
                pattern_value = json.dumps(pattern_value)
            
            # Upsert pattern
            cursor.execute("""
                INSERT INTO user_patterns 
                (user_id, pattern_type, pattern_key, pattern_value, confidence, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, pattern_type, pattern_key) 
                DO UPDATE SET 
                    pattern_value = excluded.pattern_value,
                    confidence = excluded.confidence,
                    updated_at = excluded.updated_at
            """, (
                user_id,
                pattern_type,
                pattern_key,
                pattern_value,
                confidence,
                datetime.now(UTC).isoformat(),
            ))
            
            conn.commit()
    
    def get_pattern(
        self,
        user_id: int,
        pattern_type: str,
        pattern_key: str,
        default: Any = None,
    ) -> Any:
        """
        Get a user pattern.
        
        Args:
            user_id: User identifier
            pattern_type: Type of pattern
            pattern_key: Pattern key
            default: Default value if pattern not found
            
        Returns:
            Pattern value (deserialized from JSON if needed)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT pattern_value FROM user_patterns
                WHERE user_id = ? AND pattern_type = ? AND pattern_key = ?
            """, (user_id, pattern_type, pattern_key))
            
            result = cursor.fetchone()
            
            if result is None:
                return default
            
            value = result[0]
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
    
    def get_patterns_by_type(
        self,
        user_id: int,
        pattern_type: str,
    ) -> dict[str, Any]:
        """
        Get all patterns of a specific type for a user.
        
        Args:
            user_id: User identifier
            pattern_type: Type of pattern
            
        Returns:
            Dictionary of pattern_key -> pattern_value
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT pattern_key, pattern_value, confidence 
                FROM user_patterns
                WHERE user_id = ? AND pattern_type = ?
                ORDER BY updated_at DESC
            """, (user_id, pattern_type))
            
            patterns = {}
            for row in cursor.fetchall():
                key, value, confidence = row
                
                # Try to deserialize JSON
                try:
                    patterns[key] = {
                        "value": json.loads(value),
                        "confidence": confidence,
                    }
                except (json.JSONDecodeError, TypeError):
                    patterns[key] = {
                        "value": value,
                        "confidence": confidence,
                    }
            
            return patterns
    
    def save_context(
        self,
        user_id: int,
        context_key: str,
        context_value: Any,
        session_id: Optional[str] = None,
        expires_minutes: Optional[int] = None,
    ) -> None:
        """
        Save conversation context.
        
        Args:
            user_id: User identifier
            context_key: Context key
            context_value: Context value (will be JSON serialized if not string)
            session_id: Optional session identifier
            expires_minutes: Optional expiration time in minutes
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Serialize value if needed
            if not isinstance(context_value, str):
                context_value = json.dumps(context_value)
            
            # Calculate expiration
            expires_at = None
            if expires_minutes:
                from datetime import timedelta
                expires_at = (
                    datetime.now(UTC) + timedelta(minutes=expires_minutes)
                ).isoformat()
            
            # Use explicit timestamp for proper ordering
            created_at = datetime.now(UTC).isoformat()
            
            cursor.execute("""
                INSERT INTO conversation_context 
                (user_id, context_key, context_value, session_id, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, context_key, context_value, session_id, created_at, expires_at))
            
            conn.commit()
    
    def get_context(
        self,
        user_id: int,
        context_key: str,
        session_id: Optional[str] = None,
    ) -> list[Any]:
        """
        Get conversation context entries.
        
        Args:
            user_id: User identifier
            context_key: Context key
            session_id: Optional session identifier to filter by
            
        Returns:
            List of context values (most recent first)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Clean up expired context
            cursor.execute("""
                DELETE FROM conversation_context
                WHERE expires_at IS NOT NULL AND expires_at < ?
            """, (datetime.now(UTC).isoformat(),))
            
            # Query context
            if session_id:
                cursor.execute("""
                    SELECT context_value FROM conversation_context
                    WHERE user_id = ? AND context_key = ? AND session_id = ?
                    ORDER BY created_at DESC
                """, (user_id, context_key, session_id))
            else:
                cursor.execute("""
                    SELECT context_value FROM conversation_context
                    WHERE user_id = ? AND context_key = ?
                    ORDER BY created_at DESC
                """, (user_id, context_key))
            
            results = []
            for row in cursor.fetchall():
                value = row[0]
                
                # Try to deserialize JSON
                try:
                    results.append(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    results.append(value)
            
            return results
    
    def save_insight(
        self,
        user_id: int,
        insight_type: str,
        insight_data: dict[str, Any],
        importance: float = 0.5,
    ) -> None:
        """
        Save a user insight.
        
        Args:
            user_id: User identifier
            insight_type: Type of insight (e.g., "tilt_pattern", "win_correlation")
            insight_data: Insight data dictionary
            importance: Importance level (0.0 to 1.0)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Use explicit timestamp for proper ordering
            created_at = datetime.now(UTC).isoformat()
            
            cursor.execute("""
                INSERT INTO user_insights 
                (user_id, insight_type, insight_data, importance, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, insight_type, json.dumps(insight_data), importance, created_at))
            
            conn.commit()
    
    def get_insights(
        self,
        user_id: int,
        insight_type: Optional[str] = None,
        min_importance: float = 0.0,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Get user insights.
        
        Args:
            user_id: User identifier
            insight_type: Optional insight type filter
            min_importance: Minimum importance level
            limit: Maximum number of insights to return
            
        Returns:
            List of insights with metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if insight_type:
                cursor.execute("""
                    SELECT insight_type, insight_data, importance, created_at
                    FROM user_insights
                    WHERE user_id = ? AND insight_type = ? AND importance >= ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (user_id, insight_type, min_importance, limit))
            else:
                cursor.execute("""
                    SELECT insight_type, insight_data, importance, created_at
                    FROM user_insights
                    WHERE user_id = ? AND importance >= ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (user_id, min_importance, limit))
            
            insights = []
            for row in cursor.fetchall():
                insight_type, data, importance, created_at = row
                insights.append({
                    "type": insight_type,
                    "data": json.loads(data),
                    "importance": importance,
                    "created_at": created_at,
                })
            
            return insights
    
    def clear_user_patterns(self, user_id: int) -> None:
        """Clear all patterns for a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_patterns WHERE user_id = ?", (user_id,))
            conn.commit()
    
    def clear_user_context(
        self,
        user_id: int,
        session_id: Optional[str] = None,
    ) -> None:
        """
        Clear conversation context for a user.
        
        Args:
            user_id: User identifier
            session_id: Optional session ID to clear specific session
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if session_id:
                cursor.execute(
                    "DELETE FROM conversation_context WHERE user_id = ? AND session_id = ?",
                    (user_id, session_id),
                )
            else:
                cursor.execute(
                    "DELETE FROM conversation_context WHERE user_id = ?",
                    (user_id,),
                )
            
            conn.commit()


def get_pattern_storage(db_path: Path | str = "RexVoice.db") -> PatternStorage:
    """
    Get pattern storage instance.
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        PatternStorage instance
    """
    return PatternStorage(db_path=db_path)
