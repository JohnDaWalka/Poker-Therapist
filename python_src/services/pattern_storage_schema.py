"""Shared schema definitions for pattern storage tables.

This module provides a single source of truth for the pattern storage schema,
ensuring consistency between runtime initialization and database migrations.
"""

# Table creation statements
USER_PATTERNS_TABLE = """
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
"""

CONVERSATION_CONTEXT_TABLE = """
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
"""

USER_INSIGHTS_TABLE = """
    CREATE TABLE IF NOT EXISTS user_insights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        insight_type TEXT NOT NULL,
        insight_data TEXT NOT NULL,
        importance REAL DEFAULT 0.5,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
"""

# Index creation statements
USER_PATTERNS_INDEX = """
    CREATE INDEX IF NOT EXISTS idx_user_patterns_user_type 
    ON user_patterns(user_id, pattern_type)
"""

CONVERSATION_CONTEXT_INDEX = """
    CREATE INDEX IF NOT EXISTS idx_conversation_context_user 
    ON conversation_context(user_id, session_id)
"""

USER_INSIGHTS_INDEX = """
    CREATE INDEX IF NOT EXISTS idx_user_insights_user 
    ON user_insights(user_id, insight_type)
"""


def create_tables(cursor) -> None:
    """
    Create all pattern storage tables and indexes.
    
    Args:
        cursor: SQLite database cursor (sqlite3.Cursor)
    """
    # Create tables
    cursor.execute(USER_PATTERNS_TABLE)
    cursor.execute(CONVERSATION_CONTEXT_TABLE)
    cursor.execute(USER_INSIGHTS_TABLE)
    
    # Create indexes
    cursor.execute(USER_PATTERNS_INDEX)
    cursor.execute(CONVERSATION_CONTEXT_INDEX)
    cursor.execute(USER_INSIGHTS_INDEX)
