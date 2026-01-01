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


# Concurrency and atomicity tests


def test_log_session_with_timestamp(user_id: str, test_dossier_dir: Path) -> None:
    """Test logging a session with timezone-aware timestamp."""
    from datetime import datetime, timezone
    
    dossier_path = test_dossier_dir / f"{user_id}.json"

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)
        
        # Log a session
        session_data = {
            "session_type": "triage",
            "emotion": "anxious",
            "severity": 7
        }
        dossier.log_session(session_data)
        
        # Verify session was logged
        sessions = dossier.get("sessions", [])
        assert len(sessions) == 1
        assert sessions[0]["session_type"] == "triage"
        assert sessions[0]["emotion"] == "anxious"
        assert sessions[0]["severity"] == 7
        
        # Verify timestamp is present and properly formatted (ISO 8601 with timezone)
        timestamp_str = sessions[0]["timestamp"]
        assert timestamp_str.endswith("+00:00") or timestamp_str.endswith("Z")
        
        # Verify it's a valid ISO 8601 timestamp
        parsed_dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        assert parsed_dt.tzinfo is not None  # Must be timezone-aware


def test_log_multiple_sessions(user_id: str, test_dossier_dir: Path) -> None:
    """Test logging multiple sessions."""
    dossier_path = test_dossier_dir / f"{user_id}.json"

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)
        
        # Log multiple sessions
        dossier.log_session({"session_type": "triage", "emotion": "anxious"})
        dossier.log_session({"session_type": "deep", "emotion": "calm"})
        dossier.log_session({"session_type": "debrief", "emotion": "relieved"})
        
        # Verify all sessions were logged
        sessions = dossier.get("sessions", [])
        assert len(sessions) == 3
        assert sessions[0]["session_type"] == "triage"
        assert sessions[1]["session_type"] == "deep"
        assert sessions[2]["session_type"] == "debrief"


def test_append_to_list_thread_safe(user_id: str, test_dossier_dir: Path) -> None:
    """Test append_to_list method reloads data before appending."""
    dossier_path = test_dossier_dir / f"{user_id}.json"

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        
        # Create first instance and add item
        dossier1 = Dossier(user_id)
        dossier1.append_to_list("goals", "goal1")
        
        # Create second instance and add item
        # This simulates concurrent access
        dossier2 = Dossier(user_id)
        dossier2.append_to_list("goals", "goal2")
        
        # Verify both items are present
        dossier3 = Dossier(user_id)
        goals = dossier3.get("goals", [])
        assert "goal1" in goals
        assert "goal2" in goals
        assert len(goals) == 2


def test_append_to_list_creates_list_if_missing(user_id: str, test_dossier_dir: Path) -> None:
    """Test append_to_list creates list if key doesn't exist."""
    dossier_path = test_dossier_dir / f"{user_id}.json"

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)
        
        # Append to non-existent list
        dossier.append_to_list("new_list", "item1")
        
        # Verify list was created with item
        items = dossier.get("new_list", [])
        assert items == ["item1"]


def test_append_to_list_handles_non_list(user_id: str, test_dossier_dir: Path) -> None:
    """Test append_to_list handles when key exists but isn't a list."""
    dossier_path = test_dossier_dir / f"{user_id}.json"

    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)
        
        # Set key to non-list value
        dossier.update("key", "not_a_list")
        
        # Append should create new list
        dossier.append_to_list("key", "item1")
        
        # Verify key is now a list with the item
        items = dossier.get("key", [])
        assert items == ["item1"]


def test_concurrent_writes_multiprocess(user_id: str, test_dossier_dir: Path) -> None:
    """Test concurrent writes from multiple processes don't corrupt JSON."""
    import multiprocessing
    import time
    
    dossier_path = test_dossier_dir / f"{user_id}.json"
    
    def write_worker(worker_id: int, path: Path) -> None:
        """Worker function that writes to dossier."""
        with patch.object(Dossier, "_get_storage_path") as mock_path:
            mock_path.return_value = path
            dossier = Dossier(user_id)
            
            # Each worker writes 5 times
            for i in range(5):
                dossier.append_to_list("items", f"worker_{worker_id}_item_{i}")
                time.sleep(0.01)  # Small delay to increase contention
    
    # Start multiple processes writing concurrently
    processes = []
    num_workers = 4
    
    for worker_id in range(num_workers):
        p = multiprocessing.Process(target=write_worker, args=(worker_id, dossier_path))
        p.start()
        processes.append(p)
    
    # Wait for all processes to complete
    for p in processes:
        p.join()
    
    # Verify the JSON file is valid and not corrupted
    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)
        items = dossier.get("items", [])
        
        # Should have all items from all workers (4 workers * 5 items each = 20)
        assert len(items) == num_workers * 5
        
        # Verify each worker's items are present
        for worker_id in range(num_workers):
            for i in range(5):
                expected_item = f"worker_{worker_id}_item_{i}"
                assert expected_item in items


def test_atomic_write_prevents_corruption(user_id: str, test_dossier_dir: Path) -> None:
    """Test that atomic write prevents partial writes."""
    import json
    
    dossier_path = test_dossier_dir / f"{user_id}.json"
    
    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)
        
        # Write large data
        large_data = {"items": [f"item_{i}" for i in range(1000)]}
        dossier.data = large_data
        dossier.save()
        
        # Verify file is valid JSON
        with open(dossier_path, encoding="utf-8") as f:
            loaded_data = json.load(f)
        
        assert loaded_data == large_data
        assert len(loaded_data["items"]) == 1000


def test_concurrent_read_write(user_id: str, test_dossier_dir: Path) -> None:
    """Test concurrent reads and writes work correctly."""
    import multiprocessing
    
    dossier_path = test_dossier_dir / f"{user_id}.json"
    
    def reader_worker(path: Path, results: list) -> None:
        """Worker that reads from dossier."""
        with patch.object(Dossier, "_get_storage_path") as mock_path:
            mock_path.return_value = path
            for _ in range(10):
                dossier = Dossier(user_id)
                value = dossier.get("counter", 0)
                results.append(value)
    
    def writer_worker(path: Path) -> None:
        """Worker that writes to dossier."""
        with patch.object(Dossier, "_get_storage_path") as mock_path:
            mock_path.return_value = path
            for i in range(10):
                dossier = Dossier(user_id)
                dossier.update("counter", i)
    
    # Initialize with a value
    with patch.object(Dossier, "_get_storage_path") as mock_path:
        mock_path.return_value = dossier_path
        dossier = Dossier(user_id)
        dossier.update("counter", 0)
    
    # Start reader and writer processes
    manager = multiprocessing.Manager()
    read_results = manager.list()
    
    writer = multiprocessing.Process(target=writer_worker, args=(dossier_path,))
    reader = multiprocessing.Process(target=reader_worker, args=(dossier_path, read_results))
    
    writer.start()
    reader.start()
    
    writer.join()
    reader.join()
    
    # All reads should succeed (file should never be corrupted)
    assert len(read_results) == 10
    
    # All values should be valid integers
    for value in read_results:
        assert isinstance(value, int)
        assert 0 <= value <= 9
