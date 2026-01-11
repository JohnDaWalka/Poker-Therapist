"""
Database migration: Add pattern storage tables

This migration adds tables for:
- user_patterns: User behavioral patterns
- conversation_context: Conversation context and history
- user_insights: AI-generated insights

These tables extend the existing RexVoice.db database.
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path for imports if needed
# This allows the migration to run both as a script and when imported
_parent_dir = str(Path(__file__).parent.parent)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from python_src.services.pattern_storage_schema import create_tables


def upgrade(db_path: Path | str = "RexVoice.db") -> None:
    """
    Apply migration to add pattern storage tables.
    
    Args:
        db_path: Path to SQLite database file
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        print(f"Applying migration to {db_path}...")
        
        # Use shared schema definition
        create_tables(cursor)
        
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
