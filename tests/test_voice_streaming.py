"""Tests for enhanced voice features: streaming, emotion analysis, and conversation mode."""

import os
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# Add python_src to path
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from python_src.services.voice_streaming_service import (
    VoiceStreamingService,
    ConversationSession,
    ConversationMode,
    EmotionType,
)


def test_voice_streaming_service_init() -> None:
    """Test voice streaming service initialization."""
    with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
        service = VoiceStreamingService()
        assert service.api_key == "test-key"
        assert service.is_available()


def test_voice_streaming_service_no_key() -> None:
    """Test streaming service without API key still initializes."""
    with patch.dict(os.environ, {}, clear=True):
        service = VoiceStreamingService()
        # Should still initialize but not be available
        assert not service.is_available()


def test_detect_voice_activity_disabled() -> None:
    """Test voice activity detection when disabled."""
    with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
        service = VoiceStreamingService(enable_vad=False)
        # Should always return True when VAD disabled
        assert service.detect_voice_activity(b"fake_audio") is True


def test_analyze_emotion_disabled() -> None:
    """Test emotion analysis when disabled."""
    with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
        service = VoiceStreamingService(enable_emotion_analysis=False)
        result = service.analyze_emotion(b"fake_audio")
        
        assert result["emotion"] == EmotionType.NEUTRAL.value
        assert result["confidence"] == 0.0


def test_analyze_emotion_returns_valid_data() -> None:
    """Test emotion analysis returns valid data structure."""
    with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
        service = VoiceStreamingService(enable_emotion_analysis=True)
        
        # Mock the analysis - it will fail gracefully
        result = service.analyze_emotion(b"fake_audio")
        
        # Should return valid structure even on error
        assert "emotion" in result
        assert "confidence" in result


def test_conversation_session_init() -> None:
    """Test conversation session initialization."""
    session = ConversationSession(mode=ConversationMode.SINGLE_TURN)
    
    assert session.mode == ConversationMode.SINGLE_TURN
    assert session.is_active is False
    assert len(session.conversation_history) == 0


@pytest.mark.asyncio
async def test_conversation_session_lifecycle() -> None:
    """Test conversation session start and end."""
    session = ConversationSession()
    
    await session.start_session()
    assert session.is_active is True
    
    await session.end_session()
    assert session.is_active is False


def test_conversation_session_add_message() -> None:
    """Test adding messages to conversation history."""
    session = ConversationSession()
    
    session.add_message("user", "Hello")
    session.add_message("assistant", "Hi there")
    
    history = session.get_history()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"


def test_conversation_session_clear_history() -> None:
    """Test clearing conversation history."""
    session = ConversationSession()
    
    session.add_message("user", "Hello")
    session.add_message("assistant", "Hi")
    assert len(session.get_history()) == 2
    
    session.clear_history()
    assert len(session.get_history()) == 0


def test_emotion_types_enum() -> None:
    """Test emotion type enumeration."""
    assert EmotionType.NEUTRAL.value == "neutral"
    assert EmotionType.HAPPY.value == "happy"
    assert EmotionType.FRUSTRATED.value == "frustrated"


def test_conversation_mode_enum() -> None:
    """Test conversation mode enumeration."""
    assert ConversationMode.SINGLE_TURN.value == "single_turn"
    assert ConversationMode.CONTINUOUS.value == "continuous"
    assert ConversationMode.VOICE_ACTIVATED.value == "voice_activated"


@pytest.mark.asyncio
async def test_stream_audio_recognition_empty_stream() -> None:
    """Test streaming recognition with empty stream."""
    with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
        service = VoiceStreamingService()
        
        async def empty_stream():
            return
            yield  # Make it a generator
        
        results = []
        async for text in service.stream_audio_recognition(empty_stream()):
            results.append(text)
        
        # Should handle empty stream gracefully
        assert isinstance(results, list)


def test_vad_initialization_failure() -> None:
    """Test VAD initialization failure is handled gracefully."""
    with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
        # Mock webrtcvad to not be available
        with patch.dict("sys.modules", {"webrtcvad": None}):
            service = VoiceStreamingService(enable_vad=True)
            # Should fallback to disabled VAD
            assert service.enable_vad is False or service.vad is None


def test_emotion_analyzer_initialization_failure() -> None:
    """Test emotion analyzer initialization failure is handled."""
    with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
        # Mock librosa to not be available
        with patch.dict("sys.modules", {"librosa": None}):
            service = VoiceStreamingService(enable_emotion_analysis=True)
            # Should handle missing dependencies gracefully
            result = service.analyze_emotion(b"fake")
            assert "emotion" in result
