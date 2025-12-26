"""Database models for the dossier system."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


def _utcnow() -> datetime:
    """Get current UTC time."""
    return datetime.now(UTC)


@dataclass
class Dossier:
    """Represents a therapy dossier (psychiatrist's information on the subject) tracking emotions, feelings, situations, and personal bio context."""

    id: str
    player_name: str
    data: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert dossier to dictionary representation."""
        return {
            "id": self.id,
            "player_name": self.player_name,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Dossier":
        """Create dossier from dictionary representation."""
        default_time = _utcnow().isoformat()
        return cls(
            id=data["id"],
            player_name=data["player_name"],
            data=data.get("data", {}),
            created_at=datetime.fromisoformat(data.get("created_at", default_time)),
            updated_at=datetime.fromisoformat(data.get("updated_at", default_time)),
        )
