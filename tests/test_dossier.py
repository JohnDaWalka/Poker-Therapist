"""Tests for Dossier class."""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from backend.agent.memory.dossier import Dossier


@pytest.fixture
def test_dossier_dir(tmp_path: Path) -> str:
    """Create a temporary directory for dossier storage."""
    dossier_dir = tmp_path / "dossiers"
    dossier_dir.mkdir()
    return str(dossier_dir)


@pytest.fixture
def user_id() -> str:
    """Return a test user ID."""
    return "test_user_123"


def test_init_new_user(user_id: str, test_dossier_dir: str) -> None:
    """Test initializing a dossier for a new user."""
    dossier = Dossier(user_id, storage_path=test_dossier_dir)

    assert dossier.user_id == user_id
    assert dossier.storage_path == test_dossier_dir
    assert dossier.file_path == os.path.join(test_dossier_dir, f"{user_id}.json")
    assert dossier.data == {
        "profile": {},
        "goals": [],
        "strengths": [],
        "patterns": [],
        "sessions": []
    }


def test_init_existing_user(user_id: str, test_dossier_dir: str) -> None:
    """Test initializing a dossier for an existing user."""
    # Create existing dossier file
    dossier_path = os.path.join(test_dossier_dir, f"{user_id}.json")
    existing_data = {"profile": {"name": "John"}, "goals": ["improve"], "strengths": [], "patterns": [], "sessions": []}
    with open(dossier_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f)

    dossier = Dossier(user_id, storage_path=test_dossier_dir)

    assert dossier.user_id == user_id
    assert dossier.data == existing_data


def test_load_nonexistent_file(user_id: str, test_dossier_dir: str) -> None:
    """Test loading when file doesn't exist."""
    dossier = Dossier(user_id, storage_path=test_dossier_dir)

    assert dossier.data == {
        "profile": {},
        "goals": [],
        "strengths": [],
        "patterns": [],
        "sessions": []
    }


def test_load_corrupted_file(user_id: str, test_dossier_dir: str) -> None:
    """Test loading a corrupted JSON file."""
    dossier_path = os.path.join(test_dossier_dir, f"{user_id}.json")

    # Create corrupted JSON file
    with open(dossier_path, "w", encoding="utf-8") as f:
        f.write("{ invalid json }")

    dossier = Dossier(user_id, storage_path=test_dossier_dir)

    # Should return default structure on corrupted file
    assert dossier.data == {
        "profile": {},
        "goals": [],
        "strengths": [],
        "patterns": [],
        "sessions": []
    }


def test_save(user_id: str, test_dossier_dir: str) -> None:
    """Test saving dossier data."""
    dossier_path = os.path.join(test_dossier_dir, f"{user_id}.json")

    dossier = Dossier(user_id, storage_path=test_dossier_dir)
    dossier.data = {"test_key": "test_value", "count": 42}
    dossier.save()

    # Verify file was created with correct data
    assert os.path.exists(dossier_path)
    with open(dossier_path, encoding="utf-8") as f:
        saved_data = json.load(f)

    assert saved_data == {"test_key": "test_value", "count": 42}


def test_update_field(user_id: str, test_dossier_dir: str) -> None:
    """Test updating a field in a section."""
    dossier_path = os.path.join(test_dossier_dir, f"{user_id}.json")

    dossier = Dossier(user_id, storage_path=test_dossier_dir)

    # Update some values in profile section
    dossier.update_field("profile", "name", "John")
    dossier.update_field("profile", "age", 30)

    # Verify data is in memory
    assert dossier.data["profile"]["name"] == "John"
    assert dossier.data["profile"]["age"] == 30

    # Verify data was saved to file
    with open(dossier_path, encoding="utf-8") as f:
        saved_data = json.load(f)

    assert saved_data["profile"]["name"] == "John"
    assert saved_data["profile"]["age"] == 30


def test_update_field_overwrites_existing_key(user_id: str, test_dossier_dir: str) -> None:
    """Test that update_field overwrites existing keys."""
    dossier = Dossier(user_id, storage_path=test_dossier_dir)

    dossier.update_field("profile", "status", "active")
    assert dossier.data["profile"]["status"] == "active"

    dossier.update_field("profile", "status", "inactive")
    assert dossier.data["profile"]["status"] == "inactive"


def test_update_field_creates_new_section(user_id: str, test_dossier_dir: str) -> None:
    """Test that update_field creates a new section if it doesn't exist."""
    dossier = Dossier(user_id, storage_path=test_dossier_dir)

    dossier.update_field("custom_section", "key1", "value1")
    assert dossier.data["custom_section"]["key1"] == "value1"


def test_append_to_list(user_id: str, test_dossier_dir: str) -> None:
    """Test appending values to list sections."""
    dossier_path = os.path.join(test_dossier_dir, f"{user_id}.json")

    dossier = Dossier(user_id, storage_path=test_dossier_dir)

    # Append to existing lists
    dossier.append_to_list("goals", "Improve bluffing")
    dossier.append_to_list("goals", "Better position play")
    dossier.append_to_list("strengths", "Patient player")

    # Verify data is in memory
    assert len(dossier.data["goals"]) == 2
    assert "Improve bluffing" in dossier.data["goals"]
    assert "Better position play" in dossier.data["goals"]
    assert len(dossier.data["strengths"]) == 1
    assert "Patient player" in dossier.data["strengths"]

    # Verify data was saved to file
    with open(dossier_path, encoding="utf-8") as f:
        saved_data = json.load(f)

    assert saved_data["goals"] == ["Improve bluffing", "Better position play"]
    assert saved_data["strengths"] == ["Patient player"]


def test_append_to_list_creates_new_section(user_id: str, test_dossier_dir: str) -> None:
    """Test that append_to_list creates a new section if it doesn't exist."""
    dossier = Dossier(user_id, storage_path=test_dossier_dir)

    dossier.append_to_list("custom_list", "item1")
    assert dossier.data["custom_list"] == ["item1"]


def test_log_session(user_id: str, test_dossier_dir: str) -> None:
    """Test logging a session."""
    from datetime import datetime
    from unittest.mock import patch as mock_patch

    dossier_path = os.path.join(test_dossier_dir, f"{user_id}.json")

    dossier = Dossier(user_id, storage_path=test_dossier_dir)

    # Mock datetime to get consistent timestamp
    mock_datetime = datetime(2024, 1, 15, 10, 30, 45)
    with mock_patch("backend.agent.memory.dossier.datetime") as mock_dt:
        mock_dt.utcnow.return_value = mock_datetime
        dossier.log_session("Discussed tilt management")

    # Verify data is in memory
    assert len(dossier.data["sessions"]) == 1
    assert dossier.data["sessions"][0]["summary"] == "Discussed tilt management"
    assert dossier.data["sessions"][0]["timestamp"] == "2024-01-15T10:30:45"

    # Log another session
    mock_datetime2 = datetime(2024, 1, 16, 11, 0, 0)
    with mock_patch("backend.agent.memory.dossier.datetime") as mock_dt:
        mock_dt.utcnow.return_value = mock_datetime2
        dossier.log_session("Reviewed hand history")

    assert len(dossier.data["sessions"]) == 2
    assert dossier.data["sessions"][1]["summary"] == "Reviewed hand history"

    # Verify data was saved to file
    with open(dossier_path, encoding="utf-8") as f:
        saved_data = json.load(f)

    assert len(saved_data["sessions"]) == 2


def test_get_existing_section(user_id: str, test_dossier_dir: str) -> None:
    """Test getting an existing section."""
    dossier = Dossier(user_id, storage_path=test_dossier_dir)
    dossier.data["profile"] = {"name": "John", "age": 30}
    dossier.data["goals"] = ["goal1", "goal2"]

    assert dossier.get("profile") == {"name": "John", "age": 30}
    assert dossier.get("goals") == ["goal1", "goal2"]


def test_get_nonexistent_section(user_id: str, test_dossier_dir: str) -> None:
    """Test getting a nonexistent section."""
    dossier = Dossier(user_id, storage_path=test_dossier_dir)

    assert dossier.get("nonexistent") is None


def test_get_with_default(user_id: str, test_dossier_dir: str) -> None:
    """Test getting a section with a default value."""
    dossier = Dossier(user_id, storage_path=test_dossier_dir)

    assert dossier.get("nonexistent", []) == []
    assert dossier.get("missing", {"default": "value"}) == {"default": "value"}


def test_persistence_across_instances(user_id: str, test_dossier_dir: str) -> None:
    """Test that data persists across different Dossier instances."""
    # First instance - save data
    dossier1 = Dossier(user_id, storage_path=test_dossier_dir)
    dossier1.update_field("profile", "persistent_value", "test")
    dossier1.append_to_list("goals", "test goal")

    # Second instance - load data
    dossier2 = Dossier(user_id, storage_path=test_dossier_dir)

    assert dossier2.data["profile"]["persistent_value"] == "test"
    assert "test goal" in dossier2.data["goals"]


def test_complex_data_types(user_id: str, test_dossier_dir: str) -> None:
    """Test storing complex data types."""
    dossier = Dossier(user_id, storage_path=test_dossier_dir)

    # Store various data types
    dossier.update_field("profile", "list_data", [1, 2, 3, 4, 5])
    dossier.update_field("profile", "dict_data", {"nested": {"key": "value"}})
    dossier.update_field("profile", "bool_data", True)
    dossier.update_field("profile", "null_data", None)

    # Reload and verify
    dossier2 = Dossier(user_id, storage_path=test_dossier_dir)

    assert dossier2.data["profile"]["list_data"] == [1, 2, 3, 4, 5]
    assert dossier2.data["profile"]["dict_data"] == {"nested": {"key": "value"}}
    assert dossier2.data["profile"]["bool_data"] is True
    assert dossier2.data["profile"]["null_data"] is None


def test_unicode_support(user_id: str, test_dossier_dir: str) -> None:
    """Test Unicode character support."""
    dossier = Dossier(user_id, storage_path=test_dossier_dir)

    # Store Unicode data
    dossier.update_field("profile", "unicode_text", "Hello 世界 🎰 ♠️ ♥️")

    # Reload and verify
    dossier2 = Dossier(user_id, storage_path=test_dossier_dir)
    assert dossier2.data["profile"]["unicode_text"] == "Hello 世界 🎰 ♠️ ♥️"


def test_directory_creation(user_id: str, tmp_path: Path) -> None:
    """Test that storage directory is created if it doesn't exist."""
    # Use a non-existent subdirectory
    new_storage_path = str(tmp_path / "new_dossiers")
    dossier = Dossier(user_id, storage_path=new_storage_path)
    dossier.update_field("profile", "test", "value")

    # Verify directory was created
    assert os.path.exists(new_storage_path)
    assert os.path.exists(os.path.join(new_storage_path, f"{user_id}.json"))
