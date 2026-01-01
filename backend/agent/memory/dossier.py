"""Dossier class for patient session data management."""

import json
import os
from datetime import datetime
from typing import Any


class Dossier:
    """
    Manages patient session data with persistent storage.

    This represents the beginning of a patient session with the agent.
    Data is stored in JSON format for easy persistence and retrieval.
    """

    def __init__(self, user_id: str, storage_path: str = "dossiers") -> None:
        """
        Initialize dossier for a user.

        Args:
            user_id: Unique identifier for the user
            storage_path: Directory path for storing dossier files

        """
        self.user_id = user_id
        self.storage_path = storage_path
        self.file_path = os.path.join(storage_path, f"{user_id}.json")  # noqa: PTH118

        if not os.path.exists(storage_path):  # noqa: PTH110
            os.makedirs(storage_path)  # noqa: PTH103

        self.data: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        """
        Load dossier data from JSON storage.

        Returns:
            Dictionary containing user's dossier data with default structure

        """
        if os.path.exists(self.file_path):  # noqa: PTH110
            try:
                with open(self.file_path, encoding="utf-8") as f:  # noqa: PTH123
                    data: dict[str, Any] = json.load(f)
                    return data
            except (OSError, json.JSONDecodeError):
                # If file is corrupted or unreadable, return default structure
                pass

        return {
            "profile": {},
            "goals": [],
            "strengths": [],
            "patterns": [],
            "sessions": [],
        }

    def save(self) -> None:
        """Write dossier data back to storage."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:  # noqa: PTH123
                json.dump(self.data, f, indent=4)
        except OSError as e:
            msg = f"Failed to save dossier for user {self.user_id}: {e}"
            raise OSError(msg) from e

    def update_field(self, section: str, key: str, value: Any) -> None:  # noqa: ANN401
        """
        Update a field in a specific section of the dossier.

        Args:
            section: The section to update (e.g., "profile")
            key: The key within the section to update
            value: The value to set

        """
        if section not in self.data:
            self.data[section] = {}
        self.data[section][key] = value
        self.save()

    def append_to_list(self, section: str, value: Any) -> None:  # noqa: ANN401
        """
        Append a value to a list section in the dossier.

        Args:
            section: The section to append to (e.g., "goals", "strengths")
            value: The value to append

        """
        if section not in self.data:
            self.data[section] = []
        self.data[section].append(value)
        self.save()

    def log_session(self, summary: str) -> None:
        """
        Log a session with timestamp and summary.

        Args:
            summary: Summary of the session

        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),  # noqa: DTZ003
            "summary": summary,
        }
        self.data["sessions"].append(entry)
        self.save()

    def get(self, section: str, default: Any | None = None) -> Any:  # noqa: ANN401
        """
        Get a section from the dossier.

        Args:
            section: The section to retrieve
            default: Default value if section doesn't exist

        Returns:
            The section data, or default if not found

        """
        return self.data.get(section, default)
