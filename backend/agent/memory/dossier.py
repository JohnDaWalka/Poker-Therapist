"""Dossier class for patient session data management."""

import json
from pathlib import Path
from typing import Any


class Dossier:
    """
    Manages patient session data with persistent storage.
    
    This represents the beginning of a patient session with the agent.
    Data is stored in JSON format for easy persistence and retrieval.
    """

    def __init__(self, user_id: str) -> None:
        """
        Initialize dossier for a user.
        
        Args:
            user_id: Unique identifier for the user

        """
        self.user_id = user_id
        self.data: dict[str, Any] = self.load()

    def load(self) -> dict[str, Any]:
        """
        Load dossier data from JSON storage.
        
        Returns:
            Dictionary containing user's dossier data, or empty dict if none exists

        """
        storage_path = self._get_storage_path()

        if storage_path.exists():
            try:
                with open(storage_path, encoding="utf-8") as f:
                    data: dict[str, Any] = json.load(f)
                    return data
            except (OSError, json.JSONDecodeError):
                # If file is corrupted or unreadable, return empty dict
                return {}

        return {}

    def save(self) -> None:
        """Write dossier data back to storage."""
        storage_path = self._get_storage_path()

        # Ensure storage directory exists
        storage_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(storage_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
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

    def _get_storage_path(self) -> Path:
        """
        Get the storage path for this user's dossier.
        
        Returns:
            Path to the dossier JSON file

        """
        # Store dossiers in a dedicated directory
        storage_dir = Path("dossiers")
        return storage_dir / f"{self.user_id}.json"
