"""Dossier class for patient session data management."""

import json
import logging
import os
import sys
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

# Optional GCS support
try:
    from python_src.services.gcs_storage_service import GCSStorageService
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    GCSStorageService = None

# Set up logger
logger = logging.getLogger(__name__)


class Dossier:
    """
    Manages patient session data with persistent storage.

    This represents the beginning of a patient session with the agent.
    Data is stored in JSON format for easy persistence and retrieval.

    Thread-safe and multi-process safe through file locking and atomic writes.
    """

    def __init__(self, user_id: str, gcs_service: Optional[Any] = None) -> None:
        """
        Initialize dossier for a user.

        Args:
            user_id: Unique identifier for the user
            gcs_service: Optional GCS storage service for large binary data

        """
        self.user_id = user_id
        self.gcs_service = gcs_service
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
        fd, temp_path_str = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
        )
        temp_path = Path(temp_path_str)

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
                temp_path.unlink()
            except FileNotFoundError:
                # File already cleaned up, ignore
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
    
    def store_voice_profile(
        self,
        profile_id: str,
        voice_samples: list[bytes],
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Store voice profile samples.
        
        Uses GCS if available, falls back to local storage.
        
        Args:
            profile_id: Unique profile identifier
            voice_samples: List of audio samples as bytes
            metadata: Optional metadata about the profile
        """
        if self.gcs_service and GCS_AVAILABLE:
            # Store in GCS
            try:
                blob_names = self.gcs_service.upload_voice_profile(
                    profile_id=profile_id,
                    user_id=self.user_id,
                    voice_samples=voice_samples,
                )
                
                # Store GCS references in dossier
                voice_profiles = self.data.get("voice_profiles", {})
                voice_profiles[profile_id] = {
                    "storage": "gcs",
                    "blob_names": blob_names,
                    "metadata": metadata or {},
                    "created_at": datetime.now(UTC).isoformat(),
                }
                self.update("voice_profiles", voice_profiles)
                return
            except Exception as e:
                logger.warning(
                    f"Failed to store voice profile in GCS for user {self.user_id}, "
                    f"profile {profile_id}: {e}. Falling back to local storage."
                )
                # Fall through to local storage on GCS failure
        
        # Fall back to local storage
        profile_dir = Path("voice_profiles") / self.user_id / profile_id
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        sample_paths = []
        for i, sample_data in enumerate(voice_samples):
            sample_path = profile_dir / f"sample_{i}.wav"
            sample_path.write_bytes(sample_data)
            sample_paths.append(str(sample_path))
        
        # Store local references in dossier
        voice_profiles = self.data.get("voice_profiles", {})
        voice_profiles[profile_id] = {
            "storage": "local",
            "sample_paths": sample_paths,
            "metadata": metadata or {},
            "created_at": datetime.now(UTC).isoformat(),
        }
        self.update("voice_profiles", voice_profiles)
    
    def retrieve_voice_profile(self, profile_id: str) -> Optional[dict[str, Any]]:
        """
        Retrieve voice profile samples.
        
        Args:
            profile_id: Profile identifier
            
        Returns:
            Dictionary with voice_samples (list of bytes) and metadata, or None if not found
        """
        voice_profiles = self.data.get("voice_profiles", {})
        profile_info = voice_profiles.get(profile_id)
        
        if not profile_info:
            return None
        
        storage_type = profile_info.get("storage", "local")
        
        if storage_type == "gcs" and self.gcs_service and GCS_AVAILABLE:
            # Retrieve from GCS
            try:
                blob_names = profile_info["blob_names"]
                voice_samples = self.gcs_service.download_voice_profile(blob_names)
                
                return {
                    "voice_samples": voice_samples,
                    "metadata": profile_info.get("metadata", {}),
                    "created_at": profile_info.get("created_at"),
                }
            except Exception as e:
                logger.error(
                    f"Failed to retrieve voice profile from GCS for user {self.user_id}, "
                    f"profile {profile_id}: {e}. Attempting local fallback."
                )
                # Fall through to local if GCS fails
        
        # Retrieve from local storage
        sample_paths = profile_info.get("sample_paths", [])
        voice_samples = []
        
        for path_str in sample_paths:
            path = Path(path_str)
            if path.exists():
                voice_samples.append(path.read_bytes())
        
        if not voice_samples:
            return None
        
        return {
            "voice_samples": voice_samples,
            "metadata": profile_info.get("metadata", {}),
            "created_at": profile_info.get("created_at"),
        }
    
    def delete_voice_profile(self, profile_id: str) -> bool:
        """
        Delete voice profile.
        
        Args:
            profile_id: Profile identifier
            
        Returns:
            True if deleted, False if not found
        """
        voice_profiles = self.data.get("voice_profiles", {})
        profile_info = voice_profiles.get(profile_id)
        
        if not profile_info:
            return False
        
        storage_type = profile_info.get("storage", "local")
        
        if storage_type == "gcs" and self.gcs_service and GCS_AVAILABLE:
            # Delete from GCS
            try:
                blob_names = profile_info["blob_names"]
                self.gcs_service.delete_voice_profile(blob_names)
            except Exception as e:
                logger.warning(
                    f"Failed to delete voice profile from GCS for user {self.user_id}, "
                    f"profile {profile_id}: {e}. Profile metadata will still be removed."
                )
        else:
            # Delete from local storage
            sample_paths = profile_info.get("sample_paths", [])
            for path_str in sample_paths:
                path = Path(path_str)
                path.unlink(missing_ok=True)
            
            # Try to remove profile directory if empty
            profile_dir = Path("voice_profiles") / self.user_id / profile_id
            try:
                profile_dir.rmdir()
            except OSError:
                pass
        
        # Remove from dossier
        del voice_profiles[profile_id]
        self.update("voice_profiles", voice_profiles)
        return True
    
    def list_voice_profiles(self) -> list[dict[str, Any]]:
        """
        List all voice profiles for this user.
        
        Returns:
            List of profile information dictionaries
        """
        voice_profiles = self.data.get("voice_profiles", {})
        
        profiles = []
        for profile_id, info in voice_profiles.items():
            profiles.append({
                "profile_id": profile_id,
                "storage": info.get("storage", "local"),
                "metadata": info.get("metadata", {}),
                "created_at": info.get("created_at"),
                "sample_count": (
                    len(info.get("blob_names", []))
                    if info.get("storage") == "gcs"
                    else len(info.get("sample_paths", []))
                ),
            })
        
        return profiles
