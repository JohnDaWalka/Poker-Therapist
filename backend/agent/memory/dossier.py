"""Dossier class for patient session data management."""

import json
import os
import sys
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class Dossier:
    """
    Manages patient session data with persistent storage.

    This represents the beginning of a patient session with the agent.
    Data is stored in JSON format for easy persistence and retrieval.

    Thread-safe and multi-process safe through file locking and atomic writes.
    """

    def __init__(self, user_id: str) -> None:
        """
        Initialize dossier for a user.

        Args:
            user_id: Unique identifier for the user

        """
        self.user_id = user_id
        self.data: dict[str, Any] = self.load()

    @contextmanager
    def _file_lock(self, file_handle: Any) -> Iterator[None]:
        """
        Acquire an exclusive lock on a file (cross-platform).

        Args:
            file_handle: Open file handle to lock

        Yields:
            None - lock is held during context

        """
        if sys.platform == "win32":
            import msvcrt

            # Windows file locking
            msvcrt.locking(file_handle.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            # Unix file locking
            fcntl.flock(file_handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)

    def load(self) -> dict[str, Any]:
        """
        Load dossier data from JSON storage with file locking.

        Returns:
            Dictionary containing user's dossier data, or empty dict if none exists

        """
        storage_path = self._get_storage_path()

        if storage_path.exists():
            try:
                with open(storage_path, encoding="utf-8") as f, self._file_lock(f):
                    data: dict[str, Any] = json.load(f)
                    return data
            except (OSError, json.JSONDecodeError):
                # If file is corrupted or unreadable, return empty dict
                return {}

        return {}

    def _atomic_write(self, path: Path, data: dict[str, Any]) -> None:
        """
        Atomically write data to a file using temp file + fsync + replace.

        This prevents partial writes and corruption even if the process
        crashes or is killed during the write operation.

        Args:
            path: Target file path
            data: Data to write as JSON

        """
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Create temp file in same directory (for atomic rename)
        fd, temp_path = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
        )

        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())

            # Atomic replace (works on both Unix and Windows)
            os.replace(temp_path, path)
        except Exception:
            # Clean up temp file on error
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise

    def save(self) -> None:
        """Write dossier data back to storage atomically with file locking."""
        storage_path = self._get_storage_path()

        try:
            # Use lock file to coordinate multi-process access
            lock_path = storage_path.parent / f".{storage_path.name}.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)

            with open(lock_path, "w", encoding="utf-8") as lock_file:
                with self._file_lock(lock_file):
                    # Reload data to merge any concurrent changes
                    if storage_path.exists():
                        with open(storage_path, encoding="utf-8") as f:
                            current_data = json.load(f)
                            # Merge current data with our changes (our changes win)
                            merged_data = {**current_data, **self.data}
                            self.data = merged_data

                    # Perform atomic write
                    self._atomic_write(storage_path, self.data)
        except OSError as e:
            raise OSError(f"Failed to save dossier for user {self.user_id}: {e}") from e

    def update(self, key: str, value: Any) -> None:
        """
        Update a key in the dossier and save.

        Args:
            key: The key to update
            value: The value to set

        """
        self.data[key] = value
        self.save()

    def get(self, key: str, default: Any | None = None) -> Any:
        """
        Get a value from the dossier.

        Args:
            key: The key to retrieve
            default: Default value if key doesn't exist

        Returns:
            The value associated with the key, or default if not found

        """
        return self.data.get(key, default)

    def log_session(self, session_data: dict[str, Any]) -> None:
        """
        Log a therapy session with timezone-aware UTC timestamp.

        Args:
            session_data: Dictionary containing session information

        """
        # Get or initialize sessions list
        sessions = self.data.get("sessions", [])

        # Add timezone-aware UTC timestamp
        session_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            **session_data,
        }

        sessions.append(session_entry)
        self.update("sessions", sessions)

    def append_to_list(self, key: str, item: Any) -> None:
        """
        Append an item to a list in the dossier.

        Thread-safe and multi-process safe operation that won't lose
        updates under concurrent access.

        Args:
            key: The list key to append to
            item: The item to append

        """
        storage_path = self._get_storage_path()

        try:
            # Use lock file to coordinate multi-process access
            lock_path = storage_path.parent / f".{storage_path.name}.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)

            with open(lock_path, "w", encoding="utf-8") as lock_file:
                with self._file_lock(lock_file):
                    # Reload fresh data under lock
                    if storage_path.exists():
                        with open(storage_path, encoding="utf-8") as f:
                            current_data = json.load(f)
                            self.data = current_data

                    # Get or create list
                    items = self.data.get(key, [])
                    if not isinstance(items, list):
                        items = []

                    # Append item
                    items.append(item)
                    self.data[key] = items

                    # Perform atomic write
                    self._atomic_write(storage_path, self.data)
        except OSError as e:
            raise OSError(f"Failed to append to list for user {self.user_id}: {e}") from e

    def _get_storage_path(self) -> Path:
        """
        Get the storage path for this user's dossier.

        Returns:
            Path to the dossier JSON file

        """
        # Store dossiers in a dedicated directory
        storage_dir = Path("dossiers")
        return storage_dir / f"{self.user_id}.json"
