"""Tests for dossier models."""

from datetime import datetime

from dossier.models import Dossier


def test_dossier_creation() -> None:
    """Test creating a dossier instance."""
    dossier = Dossier(
        id="player123",
        player_name="John Doe",
        data={"skill_level": "advanced"},
    )
    assert dossier.id == "player123"
    assert dossier.player_name == "John Doe"
    assert dossier.data == {"skill_level": "advanced"}
    assert isinstance(dossier.created_at, datetime)
    assert isinstance(dossier.updated_at, datetime)


def test_dossier_to_dict() -> None:
    """Test converting dossier to dictionary."""
    dossier = Dossier(
        id="player123",
        player_name="John Doe",
        data={"skill_level": "advanced"},
    )
    result = dossier.to_dict()

    assert result["id"] == "player123"
    assert result["player_name"] == "John Doe"
    assert result["data"] == {"skill_level": "advanced"}
    assert "created_at" in result
    assert "updated_at" in result


def test_dossier_from_dict() -> None:
    """Test creating dossier from dictionary."""
    data = {
        "id": "player456",
        "player_name": "Jane Smith",
        "data": {"wins": 10, "losses": 5},
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-02T00:00:00",
    }
    dossier = Dossier.from_dict(data)

    assert dossier.id == "player456"
    assert dossier.player_name == "Jane Smith"
    assert dossier.data == {"wins": 10, "losses": 5}
    assert isinstance(dossier.created_at, datetime)
    assert isinstance(dossier.updated_at, datetime)


def test_dossier_default_data() -> None:
    """Test dossier with default empty data."""
    dossier = Dossier(id="player789", player_name="Test Player")
    assert dossier.data == {}


def test_dossier_round_trip() -> None:
    """Test converting to dict and back."""
    original = Dossier(
        id="player999",
        player_name="Round Trip",
        data={"test": "value"},
    )

    as_dict = original.to_dict()
    restored = Dossier.from_dict(as_dict)

    assert restored.id == original.id
    assert restored.player_name == original.player_name
    assert restored.data == original.data
