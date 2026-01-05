"""Tests for pattern storage service."""

import json
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from python_src.services.pattern_storage import PatternStorage, get_pattern_storage


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    """Create a temporary database."""
    db_path = tmp_path / "test_patterns.db"
    return db_path


@pytest.fixture
def pattern_storage(temp_db: Path) -> PatternStorage:
    """Create a pattern storage instance with temp database."""
    return PatternStorage(db_path=temp_db)


@pytest.fixture
def user_id() -> int:
    """Return a test user ID."""
    return 1


def test_init_creates_tables(temp_db: Path) -> None:
    """Test that initialization creates required tables."""
    storage = PatternStorage(db_path=temp_db)
    
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('user_patterns', 'conversation_context', 'user_insights')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        assert "user_patterns" in tables
        assert "conversation_context" in tables
        assert "user_insights" in tables


def test_save_pattern(pattern_storage: PatternStorage, user_id: int) -> None:
    """Test saving a user pattern."""
    pattern_storage.save_pattern(
        user_id=user_id,
        pattern_type="betting",
        pattern_key="aggression_level",
        pattern_value=7.5,
        confidence=0.9,
    )
    
    # Verify pattern was saved
    result = pattern_storage.get_pattern(user_id, "betting", "aggression_level")
    assert result == 7.5


def test_save_pattern_updates_existing(
    pattern_storage: PatternStorage,
    user_id: int,
) -> None:
    """Test that saving a pattern updates existing entry."""
    # Save initial pattern
    pattern_storage.save_pattern(
        user_id=user_id,
        pattern_type="emotion",
        pattern_key="tilt_trigger",
        pattern_value="bad_beat",
    )
    
    # Update pattern
    pattern_storage.save_pattern(
        user_id=user_id,
        pattern_type="emotion",
        pattern_key="tilt_trigger",
        pattern_value="multiple_losses",
        confidence=0.8,
    )
    
    # Verify update
    result = pattern_storage.get_pattern(user_id, "emotion", "tilt_trigger")
    assert result == "multiple_losses"


def test_save_pattern_complex_value(
    pattern_storage: PatternStorage,
    user_id: int,
) -> None:
    """Test saving complex pattern values."""
    complex_value = {
        "ranges": ["AA", "KK", "QQ"],
        "positions": ["BTN", "CO"],
        "frequency": 0.85,
    }
    
    pattern_storage.save_pattern(
        user_id=user_id,
        pattern_type="betting",
        pattern_key="3bet_range",
        pattern_value=complex_value,
    )
    
    result = pattern_storage.get_pattern(user_id, "betting", "3bet_range")
    assert result == complex_value


def test_get_pattern_default(pattern_storage: PatternStorage, user_id: int) -> None:
    """Test getting pattern with default value."""
    result = pattern_storage.get_pattern(
        user_id,
        "betting",
        "nonexistent",
        default="default_value",
    )
    assert result == "default_value"


def test_get_patterns_by_type(pattern_storage: PatternStorage, user_id: int) -> None:
    """Test getting all patterns of a specific type."""
    # Save multiple patterns
    pattern_storage.save_pattern(user_id, "betting", "aggression", 7.5, 0.9)
    pattern_storage.save_pattern(user_id, "betting", "frequency", 0.35, 0.8)
    pattern_storage.save_pattern(user_id, "emotion", "tilt_level", 3, 0.7)
    
    # Get betting patterns
    betting_patterns = pattern_storage.get_patterns_by_type(user_id, "betting")
    
    assert len(betting_patterns) == 2
    assert "aggression" in betting_patterns
    assert "frequency" in betting_patterns
    assert betting_patterns["aggression"]["value"] == 7.5
    assert betting_patterns["aggression"]["confidence"] == 0.9


def test_save_context(pattern_storage: PatternStorage, user_id: int) -> None:
    """Test saving conversation context."""
    pattern_storage.save_context(
        user_id=user_id,
        context_key="last_topic",
        context_value="bad beat discussion",
        session_id="session123",
    )
    
    # Verify context was saved
    result = pattern_storage.get_context(user_id, "last_topic", "session123")
    assert len(result) == 1
    assert result[0] == "bad beat discussion"


def test_save_context_complex_value(
    pattern_storage: PatternStorage,
    user_id: int,
) -> None:
    """Test saving complex context values."""
    context_data = {
        "hand": "AKs",
        "position": "BTN",
        "action": "raise",
        "result": "fold",
    }
    
    pattern_storage.save_context(
        user_id=user_id,
        context_key="last_hand",
        context_value=context_data,
    )
    
    result = pattern_storage.get_context(user_id, "last_hand")
    assert len(result) == 1
    assert result[0] == context_data


def test_get_context_multiple_entries(
    pattern_storage: PatternStorage,
    user_id: int,
) -> None:
    """Test getting multiple context entries."""
    # Save multiple context entries
    pattern_storage.save_context(user_id, "topic", "preflop strategy")
    pattern_storage.save_context(user_id, "topic", "3betting")
    pattern_storage.save_context(user_id, "topic", "position play")
    
    results = pattern_storage.get_context(user_id, "topic")
    
    # Should return in reverse chronological order
    assert len(results) == 3
    assert results[0] == "position play"  # Most recent
    assert results[2] == "preflop strategy"  # Oldest


def test_context_expiration(pattern_storage: PatternStorage, user_id: int) -> None:
    """Test that expired context is not returned."""
    # Save context that expires immediately
    pattern_storage.save_context(
        user_id=user_id,
        context_key="temporary",
        context_value="expires soon",
        expires_minutes=-1,  # Already expired
    )
    
    # Save non-expiring context
    pattern_storage.save_context(
        user_id=user_id,
        context_key="temporary",
        context_value="persists",
    )
    
    results = pattern_storage.get_context(user_id, "temporary")
    
    # Should only return non-expired context
    assert len(results) == 1
    assert results[0] == "persists"


def test_context_session_filtering(
    pattern_storage: PatternStorage,
    user_id: int,
) -> None:
    """Test filtering context by session ID."""
    # Save context for different sessions
    pattern_storage.save_context(user_id, "topic", "session1 topic", "session1")
    pattern_storage.save_context(user_id, "topic", "session2 topic", "session2")
    pattern_storage.save_context(user_id, "topic", "no session topic")
    
    # Get context for specific session
    session1_results = pattern_storage.get_context(user_id, "topic", "session1")
    assert len(session1_results) == 1
    assert session1_results[0] == "session1 topic"
    
    # Get all context without session filter
    all_results = pattern_storage.get_context(user_id, "topic")
    assert len(all_results) == 3


def test_save_insight(pattern_storage: PatternStorage, user_id: int) -> None:
    """Test saving user insight."""
    insight_data = {
        "trigger": "consecutive losses",
        "pattern": "increased aggression",
        "correlation": 0.85,
    }
    
    pattern_storage.save_insight(
        user_id=user_id,
        insight_type="tilt_pattern",
        insight_data=insight_data,
        importance=0.9,
    )
    
    # Verify insight was saved
    insights = pattern_storage.get_insights(user_id, "tilt_pattern")
    assert len(insights) == 1
    assert insights[0]["type"] == "tilt_pattern"
    assert insights[0]["data"] == insight_data
    assert insights[0]["importance"] == 0.9


def test_get_insights_filtering(pattern_storage: PatternStorage, user_id: int) -> None:
    """Test filtering insights by type and importance."""
    # Save insights with different types and importance
    pattern_storage.save_insight(user_id, "tilt_pattern", {"data": "tilt1"}, 0.9)
    pattern_storage.save_insight(user_id, "tilt_pattern", {"data": "tilt2"}, 0.7)
    pattern_storage.save_insight(user_id, "win_correlation", {"data": "win1"}, 0.8)
    pattern_storage.save_insight(user_id, "win_correlation", {"data": "win2"}, 0.4)
    
    # Get all tilt patterns
    tilt_insights = pattern_storage.get_insights(user_id, "tilt_pattern")
    assert len(tilt_insights) == 2
    
    # Get all insights with minimum importance
    important_insights = pattern_storage.get_insights(user_id, min_importance=0.75)
    assert len(important_insights) == 3  # 0.9, 0.8, 0.7
    
    # Get all insights
    all_insights = pattern_storage.get_insights(user_id)
    assert len(all_insights) == 4


def test_get_insights_limit(pattern_storage: PatternStorage, user_id: int) -> None:
    """Test limiting number of insights returned."""
    # Save multiple insights
    for i in range(10):
        pattern_storage.save_insight(
            user_id,
            "test_insight",
            {"index": i},
            0.5,
        )
    
    # Get limited results
    insights = pattern_storage.get_insights(user_id, limit=5)
    assert len(insights) == 5
    
    # Should be most recent first
    assert insights[0]["data"]["index"] == 9


def test_clear_user_patterns(pattern_storage: PatternStorage, user_id: int) -> None:
    """Test clearing user patterns."""
    # Save patterns
    pattern_storage.save_pattern(user_id, "betting", "aggression", 7.5)
    pattern_storage.save_pattern(user_id, "betting", "frequency", 0.35)
    
    # Clear patterns
    pattern_storage.clear_user_patterns(user_id)
    
    # Verify patterns are cleared
    patterns = pattern_storage.get_patterns_by_type(user_id, "betting")
    assert len(patterns) == 0


def test_clear_user_context(pattern_storage: PatternStorage, user_id: int) -> None:
    """Test clearing user context."""
    # Save context
    pattern_storage.save_context(user_id, "topic", "test1", "session1")
    pattern_storage.save_context(user_id, "topic", "test2", "session2")
    
    # Clear specific session
    pattern_storage.clear_user_context(user_id, "session1")
    
    # Verify only session1 is cleared
    results = pattern_storage.get_context(user_id, "topic")
    assert len(results) == 1
    assert results[0] == "test2"
    
    # Clear all context
    pattern_storage.clear_user_context(user_id)
    results = pattern_storage.get_context(user_id, "topic")
    assert len(results) == 0


def test_multiple_users_isolation(
    pattern_storage: PatternStorage,
    temp_db: Path,
) -> None:
    """Test that data is isolated between users."""
    # Create users table (normally done by init_database in chatbot_app)
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL
            )
        """)
        cursor.execute("INSERT INTO users (id, email) VALUES (1, 'user1@test.com')")
        cursor.execute("INSERT INTO users (id, email) VALUES (2, 'user2@test.com')")
        conn.commit()
    
    user1_id = 1
    user2_id = 2
    
    # Save patterns for both users
    pattern_storage.save_pattern(user1_id, "betting", "aggression", 8.0)
    pattern_storage.save_pattern(user2_id, "betting", "aggression", 3.0)
    
    # Verify isolation
    user1_pattern = pattern_storage.get_pattern(user1_id, "betting", "aggression")
    user2_pattern = pattern_storage.get_pattern(user2_id, "betting", "aggression")
    
    assert user1_pattern == 8.0
    assert user2_pattern == 3.0


def test_get_pattern_storage() -> None:
    """Test factory function."""
    storage = get_pattern_storage("test.db")
    assert isinstance(storage, PatternStorage)
    assert storage.db_path == Path("test.db")


def test_pattern_storage_indexes(temp_db: Path) -> None:
    """Test that performance indexes are created."""
    storage = PatternStorage(db_path=temp_db)
    
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        
        # Check indexes exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name LIKE 'idx_%'
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        
        assert "idx_user_patterns_user_type" in indexes
        assert "idx_conversation_context_user" in indexes
        assert "idx_user_insights_user" in indexes
