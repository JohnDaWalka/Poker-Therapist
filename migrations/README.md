# Database Migrations

This directory contains database migration scripts for the Poker Therapist application.

## Overview

Migrations are used to evolve the database schema over time in a controlled and reversible way. Each migration is numbered sequentially and can be applied (upgraded) or rolled back (downgraded).

## Available Migrations

### 001_add_pattern_storage.py

Adds pattern storage tables to support persistent memory features:

- **user_patterns**: Stores user behavioral patterns (betting patterns, emotional triggers, preferences)
- **conversation_context**: Stores conversation context and history with optional expiration
- **user_insights**: Stores AI-generated insights about user behavior

## Running Migrations

### Apply Migration (Upgrade)

```bash
# Use default database (RexVoice.db)
python migrations/001_add_pattern_storage.py upgrade

# Use custom database path
python migrations/001_add_pattern_storage.py upgrade /path/to/database.db
```

### Rollback Migration (Downgrade)

```bash
# Use default database
python migrations/001_add_pattern_storage.py downgrade

# Use custom database path
python migrations/001_add_pattern_storage.py downgrade /path/to/database.db
```

### Check Migration Status

```bash
# Check default database
python migrations/001_add_pattern_storage.py status

# Check custom database
python migrations/001_add_pattern_storage.py status /path/to/database.db
```

## Automatic Migration

The application automatically applies migrations when the pattern storage service is initialized. No manual intervention is required in most cases.

```python
from python_src.services.pattern_storage import get_pattern_storage

# This will automatically create tables if they don't exist
pattern_storage = get_pattern_storage("RexVoice.db")
```

## Creating New Migrations

When adding new database features:

1. Create a new migration file: `migrations/00X_description.py`
2. Implement `upgrade()` and `downgrade()` functions
3. Document the migration in this README
4. Test both upgrade and downgrade paths

### Migration Template

```python
"""
Database migration: Brief description

Detailed description of what this migration does.
"""

import sqlite3
from pathlib import Path


def upgrade(db_path: Path | str = "RexVoice.db") -> None:
    """Apply migration."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Add your schema changes here
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS new_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                -- columns...
            )
        """)
        
        conn.commit()


def downgrade(db_path: Path | str = "RexVoice.db") -> None:
    """Rollback migration."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Reverse your schema changes
        cursor.execute("DROP TABLE IF EXISTS new_table")
        
        conn.commit()
```

## Migration Best Practices

1. **Always test migrations** on a copy of production data
2. **Make migrations reversible** - implement both upgrade and downgrade
3. **Use transactions** - wrap changes in BEGIN/COMMIT
4. **Document changes** - explain what and why in the migration file
5. **Back up data** - before running migrations on production
6. **Test rollback** - ensure downgrade works correctly

## Schema Documentation

See [STORAGE_ARCHITECTURE.md](../docs/STORAGE_ARCHITECTURE.md) for complete documentation of the database schema and storage architecture.

## Troubleshooting

### Migration Fails with "table already exists"

The migration uses `CREATE TABLE IF NOT EXISTS`, so this shouldn't happen. If it does:

1. Check migration status: `python migrations/001_add_pattern_storage.py status`
2. Verify database file path is correct
3. Check for file permissions issues

### Need to Reset Database

```bash
# Back up existing database
cp RexVoice.db RexVoice.db.backup

# Remove old database
rm RexVoice.db

# Restart app to recreate fresh database
# Or run migration manually
python migrations/001_add_pattern_storage.py upgrade
```

### Migration Partially Applied

If a migration fails partway through:

1. Check the error message to see which table failed
2. Manually verify database state with: `python migrations/001_add_pattern_storage.py status`
3. If needed, manually fix the issue with SQL
4. Or rollback and try again: `python migrations/001_add_pattern_storage.py downgrade && python migrations/001_add_pattern_storage.py upgrade`

## Testing Migrations

Migrations include test coverage in `tests/test_pattern_storage.py`:

```bash
# Run pattern storage tests (includes table creation)
pytest tests/test_pattern_storage.py -v
```

## Future Migrations

As the application evolves, new migrations will be added here for:

- Schema changes (adding columns, tables)
- Data migrations (transforming existing data)
- Index optimizations
- Constraint additions
