"""
Database migration: Add pattern storage tables

This migration adds tables for:
- user_patterns: User behavioral patterns
- conversation_context: Conversation context and history
- user_insights: AI-generated insights

These tables extend the existing RexVoice.db database.
"""

import sqlite3
from pathlib import Path


def upgrade(db_path: Path | str = "RexVoice.db") -> None:
    """
    Apply migration to add pattern storage tables.
    
    Args:
        db_path: Path to SQLite database file
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        print(f"Applying migration to {db_path}...")
        
        # Create user_patterns table
        print("Creating user_patterns table...")
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
        
        # Create conversation_context table
        print("Creating conversation_context table...")
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
        
        # Create user_insights table
        print("Creating user_insights table...")
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
        print("Creating indexes...")
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
        print("Migration completed successfully!")


def downgrade(db_path: Path | str = "RexVoice.db") -> None:
    """
    Rollback migration by dropping pattern storage tables.
    
    Args:
        db_path: Path to SQLite database file
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        print(f"Rolling back migration from {db_path}...")
        
        # Drop tables in reverse order
        print("Dropping user_insights table...")
        cursor.execute("DROP TABLE IF EXISTS user_insights")
        
        print("Dropping conversation_context table...")
        cursor.execute("DROP TABLE IF EXISTS conversation_context")
        
        print("Dropping user_patterns table...")
        cursor.execute("DROP TABLE IF EXISTS user_patterns")
        
        conn.commit()
        print("Rollback completed successfully!")


def check_migration_status(db_path: Path | str = "RexVoice.db") -> dict[str, bool]:
    """
    Check which tables exist in the database.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        Dictionary mapping table names to existence status
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN (
                'user_patterns', 
                'conversation_context', 
                'user_insights'
            )
        """)
        
        existing_tables = {row[0] for row in cursor.fetchall()}
        
        return {
            "user_patterns": "user_patterns" in existing_tables,
            "conversation_context": "conversation_context" in existing_tables,
            "user_insights": "user_insights" in existing_tables,
        }


if __name__ == "__main__":
    import sys
    
    # Default database path
    db_path = "RexVoice.db"
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if len(sys.argv) > 2:
            db_path = sys.argv[2]
        
        if command == "upgrade":
            upgrade(db_path)
        elif command == "downgrade":
            downgrade(db_path)
        elif command == "status":
            status = check_migration_status(db_path)
            print(f"\nMigration status for {db_path}:")
            for table, exists in status.items():
                status_str = "✓ EXISTS" if exists else "✗ MISSING"
                print(f"  {table}: {status_str}")
        else:
            print("Unknown command. Use: upgrade, downgrade, or status")
            sys.exit(1)
    else:
        print("Usage:")
        print("  python 001_add_pattern_storage.py upgrade [db_path]")
        print("  python 001_add_pattern_storage.py downgrade [db_path]")
        print("  python 001_add_pattern_storage.py status [db_path]")
        print("\nDefault db_path: RexVoice.db")
