"""Tests for Dossier class."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from backend.agent.memory.dossier import Dossier


@pytest.fixture
def test_dossier_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for dossier storage."""
    dossier_dir = tmp_path / "dossiers"
    dossier_dir.mkdir()
    return dossier_dir


@pytest.fixture
def user_id() -> str:
    """Return a test user ID."""
    return "test_user_123"


def test_init_new_user(user_id: str, test_dossier_dir: Path) -> None:
    """Test initializing a dossier for a new user."""
    with patch("backend.agent.memory.dossier.Path", return_value=test_dossier_dir):
        with patch.object(Dossier, "_get_storage_path") as mock_path:
            mock_path.return_value = test_dossier_dir / f"{user_id}.json"
            dossier = Dossier(user_id)

    assert dossier.user_id == user_id
    assert dossier.data == {}


def test_init_existing_user(user_id: str, test_dossier_dir: Path) -> None:
    """Test initializing a dossier for an existing user."""
    # Create existing dossier file
    dossier_path = test_dossier_dir / f"{user_id}.json"
    existing_data = {"session_count": 5, "last_emotion": "frustrated"}
    with open(dossier_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f)

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)

    assert dossier.user_id == user_id
    assert dossier.data == existing_data


def test_load_nonexistent_file(user_id: str, test_dossier_dir: Path) -> None:
    """Test loading when file doesn't exist."""
    dossier_path = test_dossier_dir / f"{user_id}.json"

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)

    assert dossier.data == {}


def test_load_corrupted_file(user_id: str, test_dossier_dir: Path) -> None:
    """Test loading a corrupted JSON file."""
    dossier_path = test_dossier_dir / f"{user_id}.json"

    # Create corrupted JSON file
    with open(dossier_path, "w", encoding="utf-8") as f:
        f.write("{ invalid json }")

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)

    # Should return empty dict on corrupted file
    assert dossier.data == {}


def test_save(user_id: str, test_dossier_dir: Path) -> None:
    """Test saving dossier data."""
    dossier_path = test_dossier_dir / f"{user_id}.json"

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)
        dossier.data = {"test_key": "test_value", "count": 42}
        dossier.save()

    # Verify file was created with correct data
    assert dossier_path.exists()
    with open(dossier_path, encoding="utf-8") as f:
        saved_data = json.load(f)

    assert saved_data == {"test_key": "test_value", "count": 42}


def test_update(user_id: str, test_dossier_dir: Path) -> None:
    """Test updating a key in the dossier."""
    dossier_path = test_dossier_dir / f"{user_id}.json"

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)

        # Update some values
        dossier.update("emotion", "calm")
        dossier.update("session_count", 1)

    # Verify data is in memory
    assert dossier.data["emotion"] == "calm"
    assert dossier.data["session_count"] == 1

    # Verify data was saved to file
    with open(dossier_path, encoding="utf-8") as f:
        saved_data = json.load(f)

    assert saved_data["emotion"] == "calm"
    assert saved_data["session_count"] == 1


def test_update_overwrites_existing_key(user_id: str, test_dossier_dir: Path) -> None:
    """Test that update overwrites existing keys."""
    dossier_path = test_dossier_dir / f"{user_id}.json"

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)

        dossier.update("status", "active")
        assert dossier.data["status"] == "active"

        dossier.update("status", "inactive")
        assert dossier.data["status"] == "inactive"


def test_get_existing_key(user_id: str, test_dossier_dir: Path) -> None:
    """Test getting an existing key."""
    dossier_path = test_dossier_dir / f"{user_id}.json"

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)
        dossier.data = {"name": "John", "age": 30}

        assert dossier.get("name") == "John"
        assert dossier.get("age") == 30


def test_get_nonexistent_key(user_id: str, test_dossier_dir: Path) -> None:
    """Test getting a nonexistent key."""
    dossier_path = test_dossier_dir / f"{user_id}.json"

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)

        assert dossier.get("nonexistent") is None


def test_get_with_default(user_id: str, test_dossier_dir: Path) -> None:
    """Test getting a key with a default value."""
    dossier_path = test_dossier_dir / f"{user_id}.json"

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)

        assert dossier.get("count", 0) == 0
        assert dossier.get("message", "default_msg") == "default_msg"


def test_get_storage_path(user_id: str) -> None:
    """Test storage path generation."""
    dossier = Dossier(user_id)
    path = dossier._get_storage_path()

    assert path == Path("dossiers") / f"{user_id}.json"


def test_persistence_across_instances(user_id: str, test_dossier_dir: Path) -> None:
    """Test that data persists across different Dossier instances."""
    dossier_path = test_dossier_dir / f"{user_id}.json"

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path

        # First instance - save data
        dossier1 = Dossier(user_id)
        dossier1.update("persistent_value", "test")

        # Second instance - load data
        dossier2 = Dossier(user_id)

        assert dossier2.get("persistent_value") == "test"


def test_complex_data_types(user_id: str, test_dossier_dir: Path) -> None:
    """Test storing complex data types."""
    dossier_path = test_dossier_dir / f"{user_id}.json"

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)

        # Store various data types
        dossier.update("list_data", [1, 2, 3, 4, 5])
        dossier.update("dict_data", {"nested": {"key": "value"}})
        dossier.update("bool_data", True)
        dossier.update("null_data", None)

        # Reload and verify
        dossier2 = Dossier(user_id)

        assert dossier2.get("list_data") == [1, 2, 3, 4, 5]
        assert dossier2.get("dict_data") == {"nested": {"key": "value"}}
        assert dossier2.get("bool_data") is True
        assert dossier2.get("null_data") is None


def test_unicode_support(user_id: str, test_dossier_dir: Path) -> None:
    """Test Unicode character support."""
    dossier_path = test_dossier_dir / f"{user_id}.json"

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)

        # Store Unicode data
        dossier.update("unicode_text", "Hello 世界 🎰 ♠️ ♥️")

        # Reload and verify
        dossier2 = Dossier(user_id)
        assert dossier2.get("unicode_text") == "Hello 世界 🎰 ♠️ ♥️"


def test_directory_creation(user_id: str, tmp_path: Path) -> None:
    """Test that storage directory is created if it doesn't exist."""
    # Use a non-existent subdirectory
    dossier_path = tmp_path / "new_dossiers" / f"{user_id}.json"

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)
        dossier.update("test", "value")

    # Verify directory was created
    assert dossier_path.parent.exists()
    assert dossier_path.exists()
