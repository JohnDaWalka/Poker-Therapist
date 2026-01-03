"""Tests for voice cloning service."""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from python_src.services.voice_cloning_service import (
    VoiceCloningService,
    VoiceProfile,
    get_cloning_service,
)


def test_voice_profile_creation() -> None:
    """Test voice profile creation."""
    samples = [b"sample1", b"sample2", b"sample3"]
    profile = VoiceProfile(
        profile_id="test123",
        name="Test Profile",
        voice_samples=samples,
        description="Test description",
    )
    
    assert profile.profile_id == "test123"
    assert profile.name == "Test Profile"
    assert len(profile.voice_samples) == 3
    assert profile.description == "Test description"


def test_voice_profile_to_dict() -> None:
    """Test voice profile serialization."""
    samples = [b"sample1"]
    profile = VoiceProfile(
        profile_id="test123",
        name="Test Profile",
        voice_samples=samples,
    )
    
    data = profile.to_dict()
    assert data["profile_id"] == "test123"
    assert data["name"] == "Test Profile"
    assert data["sample_count"] == 1


def test_voice_cloning_service_init() -> None:
    """Test voice cloning service initialization."""
    service = VoiceCloningService(use_coqui_tts=False)
    
    assert service.use_coqui_tts is False
    assert len(service.profiles) == 0


def test_create_profile_success() -> None:
    """Test creating a voice profile."""
    service = VoiceCloningService(use_coqui_tts=False)
    
    samples = [b"sample1", b"sample2", b"sample3"]
    profile = service.create_profile(
        name="My Voice",
        voice_samples=samples,
        description="Custom Rex voice",
    )
    
    assert profile.name == "My Voice"
    assert len(profile.voice_samples) == 3
    assert profile.description == "Custom Rex voice"
    assert profile.profile_id in service.profiles


def test_create_profile_insufficient_samples() -> None:
    """Test creating profile with insufficient samples raises error."""
    service = VoiceCloningService(use_coqui_tts=False)
    
    with pytest.raises(ValueError, match="At least 1 voice sample required"):
        service.create_profile(
            name="My Voice",
            voice_samples=[],
        )


def test_get_profile() -> None:
    """Test retrieving a voice profile."""
    service = VoiceCloningService(use_coqui_tts=False)
    
    samples = [b"sample1"]
    created_profile = service.create_profile("Test", samples)
    
    retrieved_profile = service.get_profile(created_profile.profile_id)
    assert retrieved_profile is not None
    assert retrieved_profile.name == "Test"


def test_get_nonexistent_profile() -> None:
    """Test retrieving non-existent profile returns None."""
    service = VoiceCloningService(use_coqui_tts=False)
    
    profile = service.get_profile("nonexistent")
    assert profile is None


def test_list_profiles() -> None:
    """Test listing all profiles."""
    service = VoiceCloningService(use_coqui_tts=False)
    
    service.create_profile("Profile 1", [b"sample1"])
    service.create_profile("Profile 2", [b"sample2"])
    
    profiles = service.list_profiles()
    assert len(profiles) == 2
    assert all(isinstance(p, VoiceProfile) for p in profiles)


def test_delete_profile() -> None:
    """Test deleting a profile."""
    service = VoiceCloningService(use_coqui_tts=False)
    
    profile = service.create_profile("To Delete", [b"sample"])
    assert len(service.list_profiles()) == 1
    
    result = service.delete_profile(profile.profile_id)
    assert result is True
    assert len(service.list_profiles()) == 0


def test_delete_nonexistent_profile() -> None:
    """Test deleting non-existent profile returns False."""
    service = VoiceCloningService(use_coqui_tts=False)
    
    result = service.delete_profile("nonexistent")
    assert result is False


def test_synthesize_with_profile_empty_text() -> None:
    """Test synthesis with empty text raises error."""
    service = VoiceCloningService(use_coqui_tts=False)
    profile = service.create_profile("Test", [b"sample"])
    
    with pytest.raises(ValueError, match="Text cannot be empty"):
        service.synthesize_with_profile("", profile)


def test_synthesize_with_profile_openai_fallback() -> None:
    """Test synthesis falls back to OpenAI when Coqui not available."""
    # Skip test if openai not available
    try:
        from openai import OpenAI
    except ImportError:
        pytest.skip("OpenAI library not available")
    
    # Mock OpenAI client
    mock_response = Mock()
    mock_response.content = b"fake_audio_data"
    mock_client = Mock()
    mock_client.audio.speech.create.return_value = mock_response
    
    with patch("openai.OpenAI", return_value=mock_client):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            service = VoiceCloningService(use_coqui_tts=False)
            profile = service.create_profile("Test", [b"sample"])
            
            audio = service.synthesize_with_profile("Hello", profile)
            assert audio == b"fake_audio_data"
            mock_client.audio.speech.create.assert_called_once()


def test_synthesize_without_api_key() -> None:
    """Test synthesis without API key raises error."""
    with patch.dict(os.environ, {}, clear=True):
        service = VoiceCloningService(use_coqui_tts=False)
        profile = service.create_profile("Test", [b"sample"])
        
        with pytest.raises(RuntimeError, match="(OpenAI API key required|No module named 'openai'|Voice synthesis failed)"):
            service.synthesize_with_profile("Hello", profile)


def test_validate_audio_sample_structure() -> None:
    """Test audio validation returns proper structure."""
    service = VoiceCloningService(use_coqui_tts=False)
    
    # Will fail to analyze but should return proper structure
    result = service.validate_audio_sample(b"fake_audio")
    
    assert "valid" in result
    assert isinstance(result["valid"], bool)


def test_is_available_with_openai_key() -> None:
    """Test service is available with OpenAI key."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        service = VoiceCloningService(use_coqui_tts=False)
        assert service.is_available() is True


def test_is_available_without_keys() -> None:
    """Test service availability without keys."""
    with patch.dict(os.environ, {}, clear=True):
        service = VoiceCloningService(use_coqui_tts=False)
        assert service.is_available() is False


def test_get_cloning_service_factory() -> None:
    """Test cloning service factory function."""
    service = get_cloning_service(use_coqui_tts=False)
    assert isinstance(service, VoiceCloningService)


def test_coqui_tts_not_available() -> None:
    """Test Coqui TTS initialization failure is handled."""
    # Mock TTS import to fail
    with patch.dict("sys.modules", {"TTS": None, "TTS.api": None}):
        service = VoiceCloningService(use_coqui_tts=True)
        # Should fallback to disabled
        assert service.use_coqui_tts is False or service.tts_model is None


def test_multiple_profiles_unique_ids() -> None:
    """Test that multiple profiles get unique IDs."""
    service = VoiceCloningService(use_coqui_tts=False)
    
    profile1 = service.create_profile("Profile 1", [b"sample1"])
    profile2 = service.create_profile("Profile 2", [b"sample2"])
    
    assert profile1.profile_id != profile2.profile_id


def test_profile_with_single_sample() -> None:
    """Test profile can be created with single sample."""
    service = VoiceCloningService(use_coqui_tts=False)
    
    profile = service.create_profile("Single Sample", [b"sample1"])
    assert profile is not None
    assert len(profile.voice_samples) == 1


def test_profile_with_many_samples() -> None:
    """Test profile can be created with many samples."""
    service = VoiceCloningService(use_coqui_tts=False)
    
    samples = [f"sample{i}".encode() for i in range(10)]
    profile = service.create_profile("Many Samples", samples)
    assert len(profile.voice_samples) == 10
