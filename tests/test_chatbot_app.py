"""Tests for Streamlit chatbot application."""

import os
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import functions from chatbot_app
from chatbot_app import (
    ThinksCallback,
    clear_user_history,
    get_or_create_user,
    get_xai_client,
    init_database,
    load_messages,
    save_message,
)


@pytest.fixture
def test_db(tmp_path: Path) -> Path:
    """Create a temporary database for testing."""
    db_path = tmp_path / "test_chatbot.db"
    with patch("chatbot_app.DB_PATH", db_path):
        init_database()
    return db_path


def test_init_database(tmp_path: Path) -> None:
    """Test database initialization."""
    db_path = tmp_path / "test.db"

    with patch("chatbot_app.DB_PATH", db_path):
        init_database()

    # Check that database file was created
    assert db_path.exists()

    # Check that tables were created
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}

    assert "users" in tables
    assert "messages" in tables

    conn.close()


def test_default_db_path() -> None:
    """Ensure the default database path uses RexVoice.db."""
    import chatbot_app

    assert chatbot_app.DB_PATH.name == "RexVoice.db"


def test_get_or_create_user_new(test_db: Path) -> None:
    """Test creating a new user."""
    email = "test@example.com"

    with patch("chatbot_app.DB_PATH", test_db):
        user_id = get_or_create_user(email)

    assert user_id > 0

    # Verify user was created in database
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    assert result is not None
    assert result[0] == email


def test_get_or_create_user_existing(test_db: Path) -> None:
    """Test getting an existing user."""
    email = "existing@example.com"

    with patch("chatbot_app.DB_PATH", test_db):
        user_id1 = get_or_create_user(email)
        user_id2 = get_or_create_user(email)

    # Should return the same user ID
    assert user_id1 == user_id2


def test_save_message(test_db: Path) -> None:
    """Test saving a message."""
    email = "user@example.com"

    with patch("chatbot_app.DB_PATH", test_db):
        user_id = get_or_create_user(email)
        save_message(user_id, "user", "Hello, chatbot!")

    # Verify message was saved
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM messages WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    assert result is not None
    assert result[0] == "user"
    assert result[1] == "Hello, chatbot!"


def test_load_messages(test_db: Path) -> None:
    """Test loading messages for a user."""
    email = "user@example.com"

    with patch("chatbot_app.DB_PATH", test_db):
        user_id = get_or_create_user(email)

        # Save multiple messages
        save_message(user_id, "user", "Message 1")
        save_message(user_id, "assistant", "Response 1")
        save_message(user_id, "user", "Message 2")

        # Load messages
        messages = load_messages(user_id)

    assert len(messages) == 3
    # Check that all messages are present
    contents = [m["content"] for m in messages]
    assert "Message 1" in contents
    assert "Response 1" in contents
    assert "Message 2" in contents
    
    # Check roles
    roles = [m["role"] for m in messages]
    assert roles.count("user") == 2
    assert roles.count("assistant") == 1


def test_load_messages_with_limit(test_db: Path) -> None:
    """Test loading messages with a limit."""
    email = "user@example.com"

    with patch("chatbot_app.DB_PATH", test_db):
        user_id = get_or_create_user(email)

        # Save multiple messages
        for i in range(10):
            save_message(user_id, "user", f"Message {i}")

        # Load only 5 messages
        messages = load_messages(user_id, limit=5)

    assert len(messages) == 5
    # Check that we get 5 messages (order may vary due to same timestamps)
    for msg in messages:
        assert msg["role"] == "user"
        assert msg["content"].startswith("Message ")


def test_clear_user_history(test_db: Path) -> None:
    """Test clearing user history."""
    email = "user@example.com"

    with patch("chatbot_app.DB_PATH", test_db):
        user_id = get_or_create_user(email)

        # Save messages
        save_message(user_id, "user", "Message 1")
        save_message(user_id, "assistant", "Response 1")

        # Verify messages exist
        messages_before = load_messages(user_id)
        assert len(messages_before) == 2

        # Clear history
        clear_user_history(user_id)

        # Verify messages were deleted
        messages_after = load_messages(user_id)
        assert len(messages_after) == 0


def test_get_xai_client_with_env_var() -> None:
    """Test getting xAI client with environment variable."""
    with patch.dict(os.environ, {"XAI_API_KEY": "test-api-key"}):
        with patch("chatbot_app.st") as mock_st:
            mock_st.secrets = {}
            client = get_xai_client()

    assert client is not None
    assert client.api_key == "test-api-key"
    # base_url might have trailing slash
    assert str(client.base_url).rstrip("/") == "https://api.x.ai/v1"


def test_get_xai_client_with_secrets() -> None:
    """Test getting xAI client with Streamlit secrets."""
    with patch("chatbot_app.st") as mock_st:
        mock_st.secrets = {"XAI_API_KEY": "secret-api-key"}
        client = get_xai_client()

    assert client is not None
    assert client.api_key == "secret-api-key"


def test_get_xai_client_missing_key() -> None:
    """Test error when API key is missing."""
    with patch.dict(os.environ, {}, clear=True):
        with patch("chatbot_app.st") as mock_st:
            mock_st.secrets = {}
            mock_st.error = Mock()
            mock_st.stop = Mock(side_effect=SystemExit)

            with pytest.raises(SystemExit):
                get_xai_client()

            mock_st.error.assert_called_once()


def test_thinks_callback_no_thinking() -> None:
    """Test ThinksCallback with regular text."""
    container = MagicMock()
    callback = ThinksCallback(container)

    # Process regular text
    callback.process_chunk("Hello, ")
    callback.process_chunk("this is a test.")

    assert callback.response_text == "Hello, this is a test."
    assert callback.thinking_text == ""
    assert not callback.in_thinking


def test_thinks_callback_with_thinking() -> None:
    """Test ThinksCallback with thinking tags."""
    container = MagicMock()
    callback = ThinksCallback(container)

    # Process text with thinking
    callback.process_chunk("Before <thinking>")
    callback.process_chunk("Let me think about this...")
    callback.process_chunk("</thinking> After")

    # Thinking should not include text before the tag
    assert callback.thinking_text == "Let me think about this..."
    # Response includes text before thinking and after thinking
    assert callback.response_text == "Before  After"
    assert not callback.in_thinking


def test_thinks_callback_thinking_in_multiple_chunks() -> None:
    """Test ThinksCallback with thinking split across chunks."""
    container = MagicMock()
    callback = ThinksCallback(container)

    # Process thinking split across chunks
    callback.process_chunk("<thinking>Part 1 ")
    assert callback.in_thinking
    assert callback.thinking_text == "Part 1 "

    callback.process_chunk("Part 2 ")
    assert callback.in_thinking
    assert callback.thinking_text == "Part 1 Part 2 "

    callback.process_chunk("</thinking>")
    assert not callback.in_thinking


def test_user_isolation(test_db: Path) -> None:
    """Test that users have isolated message histories."""
    with patch("chatbot_app.DB_PATH", test_db):
        # Create two users
        user1_id = get_or_create_user("user1@example.com")
        user2_id = get_or_create_user("user2@example.com")

        # Save messages for each user
        save_message(user1_id, "user", "User 1 message")
        save_message(user2_id, "user", "User 2 message")

        # Load messages for each user
        user1_messages = load_messages(user1_id)
        user2_messages = load_messages(user2_id)

    # Verify isolation
    assert len(user1_messages) == 1
    assert len(user2_messages) == 1
    assert user1_messages[0]["content"] == "User 1 message"
    assert user2_messages[0]["content"] == "User 2 message"


def test_database_constraints(test_db: Path) -> None:
    """Test database constraints."""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()

    # Test unique email constraint
    cursor.execute("INSERT INTO users (email) VALUES (?)", ("test@example.com",))
    conn.commit()

    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("INSERT INTO users (email) VALUES (?)", ("test@example.com",))
        conn.commit()

    conn.close()
