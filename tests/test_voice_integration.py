"""Tests for voice service integration."""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add python_src to path
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from python_src.services.voice_service import VoiceService, REX_SYSTEM_PROMPT, get_voice_service


def test_rex_system_prompt_exists() -> None:
    """Test that Rex system prompt is defined."""
    assert REX_SYSTEM_PROMPT
    assert "Rex" in REX_SYSTEM_PROMPT
    assert "poker" in REX_SYSTEM_PROMPT.lower()
    assert "CFR" in REX_SYSTEM_PROMPT


def test_voice_service_init_with_xai_key() -> None:
    """Test voice service initialization with x.ai key."""
    with patch.dict(os.environ, {"XAI_API_KEY": "test-xai-key"}):
        service = VoiceService()
        assert service.xai_api_key == "test-xai-key"
        assert service.use_xai is True


def test_voice_service_init_with_openai_key() -> None:
    """Test voice service initialization with OpenAI key."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-openai-key"}, clear=True):
        # Remove XAI_API_KEY if it exists
        if "XAI_API_KEY" in os.environ:
            del os.environ["XAI_API_KEY"]
        service = VoiceService()
        assert service.openai_api_key == "test-openai-key"


def test_voice_service_init_no_keys() -> None:
    """Test voice service initialization fails without API keys."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="API key required"):
            VoiceService()


def test_voice_service_is_available() -> None:
    """Test voice service availability check."""
    with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
        service = VoiceService()
        assert service.is_available() is True


def test_voice_service_get_provider() -> None:
    """Test get_voice_provider method."""
    with patch.dict(os.environ, {"XAI_API_KEY": "xai-key", "OPENAI_API_KEY": "openai-key"}):
        service = VoiceService()
        provider = service.get_voice_provider()
        assert "x.ai" in provider


def test_get_voice_service_factory() -> None:
    """Test voice service factory function."""
    with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
        service = get_voice_service()
        assert isinstance(service, VoiceService)


def test_voice_service_tts_empty_text() -> None:
    """Test TTS with empty text raises error."""
    with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
        service = VoiceService()
        with pytest.raises(ValueError, match="Text cannot be empty"):
            service.text_to_speech("")


def test_voice_service_stt_empty_audio() -> None:
    """Test STT with empty audio raises error."""
    with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
        service = VoiceService()
        with pytest.raises(ValueError, match="Audio data cannot be empty"):
            service.speech_to_text(b"")


@patch("python_src.services.voice_service.OpenAI")
def test_voice_service_tts_success(mock_openai: Mock) -> None:
    """Test successful TTS conversion."""
    # Mock OpenAI client
    mock_response = Mock()
    mock_response.content = b"fake_audio_data"
    mock_client = Mock()
    mock_client.audio.speech.create.return_value = mock_response
    mock_openai.return_value = mock_client

    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
        service = VoiceService(use_xai=False)
        audio = service.text_to_speech("Hello from Rex!")
        assert audio == b"fake_audio_data"
        mock_client.audio.speech.create.assert_called_once()


@patch("python_src.services.voice_service.OpenAI")
def test_voice_service_stt_success(mock_openai: Mock) -> None:
    """Test successful STT conversion."""
    # Mock OpenAI client
    mock_response = Mock()
    mock_response.text = "Hello from user"
    mock_client = Mock()
    mock_client.audio.transcriptions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
        service = VoiceService(use_xai=False)
        text = service.speech_to_text(b"fake_audio_data")
        assert text == "Hello from user"
        mock_client.audio.transcriptions.create.assert_called_once()


def test_authorized_emails_in_chatbot_app() -> None:
    """Test that authorized emails are properly configured."""
    # Import chatbot_app to check AUTHORIZED_EMAILS
    import chatbot_app
    
    assert hasattr(chatbot_app, "AUTHORIZED_EMAILS")
    authorized = chatbot_app.AUTHORIZED_EMAILS
    
    # Check all required emails are present
    required_emails = [
        "m.fanelli1@icloud.com",
        "johndawalka@icloud.com",
        "mauro.fanelli@ctstate.edu",
        "maurofanellijr@gmail.com",
        "cooljack87@icloud.com",
        "jdwalka@pm.me",
    ]
    
    for email in required_emails:
        assert email in authorized, f"Email {email} not in AUTHORIZED_EMAILS"
