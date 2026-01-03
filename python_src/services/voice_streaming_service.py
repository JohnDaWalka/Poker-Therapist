"""Enhanced voice service with real-time streaming, emotion analysis, and conversation mode."""

import asyncio
import os
from enum import Enum
from typing import Any, AsyncIterator, Callable, Optional

import numpy as np


class EmotionType(Enum):
    """Detected emotion types."""
    
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FRUSTRATED = "frustrated"
    EXCITED = "excited"
    CONFIDENT = "confident"
    ANXIOUS = "anxious"


class ConversationMode(Enum):
    """Conversation mode types."""
    
    SINGLE_TURN = "single_turn"
    CONTINUOUS = "continuous"
    VOICE_ACTIVATED = "voice_activated"


class VoiceStreamingService:
    """Service for real-time voice streaming with WebRTC support."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        enable_emotion_analysis: bool = True,
        enable_vad: bool = True,
    ) -> None:
        """
        Initialize voice streaming service.
        
        Args:
            api_key: Optional API key override
            enable_emotion_analysis: Enable emotion detection
            enable_vad: Enable voice activity detection
        """
        self.api_key = api_key or os.getenv("XAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.enable_emotion_analysis = enable_emotion_analysis
        self.enable_vad = enable_vad
        
        # Initialize VAD if enabled
        self.vad = None
        if enable_vad:
            try:
                import webrtcvad
                self.vad = webrtcvad.Vad(2)  # Aggressiveness level 2 (0-3)
            except ImportError:
                self.enable_vad = False
        
        # Initialize emotion analyzer if enabled
        self.emotion_analyzer = None
        if enable_emotion_analysis:
            try:
                # Lazy load to avoid startup overhead
                self._init_emotion_analyzer()
            except ImportError:
                self.enable_emotion_analysis = False
    
    def _init_emotion_analyzer(self) -> None:
        """Initialize emotion analysis model (lazy loading)."""
        # Will be loaded on first use to reduce startup time
        pass
    
    def detect_voice_activity(self, audio_chunk: bytes, sample_rate: int = 16000) -> bool:
        """
        Detect if audio chunk contains voice activity.
        
        Args:
            audio_chunk: Audio data chunk
            sample_rate: Sample rate (must be 8000, 16000, 32000, or 48000)
            
        Returns:
            True if voice activity detected
        """
        if not self.enable_vad or not self.vad:
            return True  # Assume voice present if VAD disabled
        
        try:
            # Ensure sample rate is valid
            if sample_rate not in [8000, 16000, 32000, 48000]:
                sample_rate = 16000
            
            # Frame duration must be 10, 20, or 30 ms
            frame_duration = 30  # ms
            
            # Check if audio chunk has voice
            return self.vad.is_speech(audio_chunk, sample_rate)
        except Exception:
            return True  # Assume voice on error
    
    def analyze_emotion(self, audio_data: bytes) -> dict[str, Any]:
        """
        Analyze emotion from audio data.
        
        Args:
            audio_data: Audio data as bytes
            
        Returns:
            Dictionary with emotion type and confidence
        """
        if not self.enable_emotion_analysis:
            return {"emotion": EmotionType.NEUTRAL.value, "confidence": 0.0}
        
        try:
            # Lazy load emotion analyzer
            if self.emotion_analyzer is None:
                import librosa
                # Placeholder for actual emotion model
                # In production, would use pre-trained emotion recognition model
            
            # Extract audio features
            # This is a simplified placeholder - actual implementation would use
            # a trained model like wav2vec2 for emotion recognition
            import librosa
            import numpy as np
            from io import BytesIO
            
            # Load audio
            audio_io = BytesIO(audio_data)
            y, sr = librosa.load(audio_io, sr=16000)
            
            # Extract features (simplified example)
            # In production, would use actual emotion detection model
            energy = np.mean(librosa.feature.rms(y=y))
            zcr = np.mean(librosa.feature.zero_crossing_rate(y))
            
            # Simple heuristic-based emotion detection (placeholder)
            # In production, use trained model like SpeechBrain emotion recognition
            if energy > 0.02 and zcr > 0.1:
                emotion = EmotionType.EXCITED
                confidence = 0.7
            elif energy < 0.01:
                emotion = EmotionType.SAD
                confidence = 0.6
            elif zcr > 0.15:
                emotion = EmotionType.FRUSTRATED
                confidence = 0.65
            else:
                emotion = EmotionType.NEUTRAL
                confidence = 0.5
            
            return {
                "emotion": emotion.value,
                "confidence": confidence,
                "energy": float(energy),
                "zcr": float(zcr),
            }
        except Exception as e:
            # Return neutral on error
            return {
                "emotion": EmotionType.NEUTRAL.value,
                "confidence": 0.0,
                "error": str(e),
            }
    
    async def stream_audio_recognition(
        self,
        audio_stream: AsyncIterator[bytes],
        callback: Optional[Callable[[str], None]] = None,
    ) -> AsyncIterator[str]:
        """
        Stream real-time audio recognition.
        
        Args:
            audio_stream: Async iterator of audio chunks
            callback: Optional callback for each transcription
            
        Yields:
            Transcribed text chunks
        """
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            
            # Buffer for accumulating audio chunks
            audio_buffer = bytearray()
            buffer_threshold = 1024 * 100  # 100KB chunks
            
            async for audio_chunk in audio_stream:
                # Check for voice activity
                if self.enable_vad and not self.detect_voice_activity(audio_chunk):
                    continue
                
                audio_buffer.extend(audio_chunk)
                
                # Process when buffer reaches threshold
                if len(audio_buffer) >= buffer_threshold:
                    # Convert to file-like object
                    from io import BytesIO
                    audio_file = BytesIO(bytes(audio_buffer))
                    audio_file.name = "stream.wav"
                    
                    try:
                        # Transcribe chunk
                        response = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file,
                        )
                        
                        text = response.text
                        
                        if callback:
                            callback(text)
                        
                        yield text
                    except Exception:
                        # Skip failed chunks
                        pass
                    
                    # Clear buffer
                    audio_buffer.clear()
        except Exception as e:
            # Handle streaming errors gracefully
            yield f"[Streaming error: {e}]"
    
    def is_available(self) -> bool:
        """Check if streaming service is available."""
        return bool(self.api_key)


class ConversationSession:
    """Manages continuous conversation sessions."""
    
    def __init__(
        self,
        mode: ConversationMode = ConversationMode.SINGLE_TURN,
        voice_service: Optional[VoiceStreamingService] = None,
    ) -> None:
        """
        Initialize conversation session.
        
        Args:
            mode: Conversation mode
            voice_service: Optional voice streaming service
        """
        self.mode = mode
        self.voice_service = voice_service or VoiceStreamingService()
        self.is_active = False
        self.conversation_history: list[dict[str, str]] = []
    
    async def start_session(self) -> None:
        """Start conversation session."""
        self.is_active = True
        self.conversation_history = []
    
    async def end_session(self) -> None:
        """End conversation session."""
        self.is_active = False
    
    def add_message(self, role: str, content: str) -> None:
        """Add message to conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content,
        })
    
    def get_history(self) -> list[dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history.copy()
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()


def get_streaming_service(
    api_key: Optional[str] = None,
    enable_emotion_analysis: bool = True,
    enable_vad: bool = True,
) -> VoiceStreamingService:
    """
    Get voice streaming service instance.
    
    Args:
        api_key: Optional API key override
        enable_emotion_analysis: Enable emotion detection
        enable_vad: Enable voice activity detection
        
    Returns:
        VoiceStreamingService instance
    """
    return VoiceStreamingService(
        api_key=api_key,
        enable_emotion_analysis=enable_emotion_analysis,
        enable_vad=enable_vad,
    )
