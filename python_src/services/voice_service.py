"""Voice service abstraction for TTS and STT with Rex personality using x.ai API."""

import os
from typing import Any, Optional

from openai import OpenAI

# Rex Personality System Prompt
REX_SYSTEM_PROMPT = """You are Rex, an elite poker coach with decades of experience. You combine:
- Advanced CFR (Counterfactual Regret Minimization) analysis
- Psychological wellness coaching
- Strategic gameplay optimization
- Direct, no-nonsense communication style
- Sharp wit with professional empathy

Speak authoritatively but supportively. Use poker terminology naturally. 
Provide actionable insights backed by mathematical analysis.
Be conversational and engaging, like you're coaching someone at the table."""


class VoiceService:
    """Service for handling text-to-speech and speech-to-text operations using x.ai API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        use_xai: bool = True,
        fallback_to_openai: bool = True,
    ) -> None:
        """
        Initialize voice service with API credentials.

        Args:
            api_key: Optional API key override
            use_xai: Use x.ai API endpoint (default: True)
            fallback_to_openai: Fallback to OpenAI if x.ai doesn't support voice (default: True)

        """
        # Try x.ai API first
        self.xai_api_key = api_key or os.getenv("XAI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_xai = use_xai and bool(self.xai_api_key)
        self.fallback_to_openai = fallback_to_openai

        if not self.xai_api_key and not self.openai_api_key:
            raise RuntimeError(
                "API key required. Set XAI_API_KEY or OPENAI_API_KEY in environment."
            )

        # Initialize x.ai client (OpenAI-compatible API)
        if self.use_xai and self.xai_api_key:
            self.xai_client = OpenAI(
                api_key=self.xai_api_key,
                base_url="https://api.x.ai/v1",
            )

        # Initialize OpenAI client for voice features (fallback)
        if self.openai_api_key and fallback_to_openai:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
        else:
            self.openai_client = None

        self.tts_voice = "onyx"  # Deep, authoritative voice for Rex
        self.tts_model = "tts-1"  # Standard quality, faster response
        self.stt_model = "whisper-1"  # Speech recognition model

    def text_to_speech(self, text: str, voice: Optional[str] = None) -> bytes:
        """
        Convert text to speech audio using x.ai or OpenAI API.

        Note: x.ai may not support TTS yet. Will attempt x.ai first, then fallback to OpenAI.

        Args:
            text: Text to convert to speech
            voice: Voice to use (onyx, alloy, echo, fable, nova, shimmer)

        Returns:
            Audio data as bytes

        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Try x.ai first if available
        if self.use_xai and self.xai_client:
            try:
                response = self.xai_client.audio.speech.create(
                    model=self.tts_model,
                    voice=voice or self.tts_voice,
                    input=text,
                )
                return response.content
            except Exception as xai_error:
                # x.ai might not support TTS yet, fallback to OpenAI
                if self.openai_client and self.fallback_to_openai:
                    pass  # Continue to OpenAI fallback below
                else:
                    raise RuntimeError(
                        f"x.ai TTS conversion failed and no fallback available: {xai_error!s}"
                    ) from xai_error

        # Fallback to OpenAI for TTS
        if self.openai_client:
            try:
                response = self.openai_client.audio.speech.create(
                    model=self.tts_model,
                    voice=voice or self.tts_voice,
                    input=text,
                )
                return response.content
            except Exception as openai_error:
                raise RuntimeError(
                    f"OpenAI TTS conversion failed: {openai_error!s}"
                ) from openai_error

        raise RuntimeError("No TTS service available. Configure XAI_API_KEY or OPENAI_API_KEY.")

    def speech_to_text(self, audio_data: bytes, language: str = "en") -> str:
        """
        Convert speech audio to text using x.ai or OpenAI API.

        Note: x.ai may not support STT yet. Will attempt x.ai first, then fallback to OpenAI.

        Args:
            audio_data: Audio data as bytes
            language: Language code (default: en)

        Returns:
            Transcribed text

        """
        if not audio_data:
            raise ValueError("Audio data cannot be empty")

        try:
            # Create a temporary file-like object for the audio data
            from io import BytesIO

            audio_file = BytesIO(audio_data)
            audio_file.name = "audio.wav"  # Whisper needs a filename

            # Try x.ai first if available
            if self.use_xai and self.xai_client:
                try:
                    response = self.xai_client.audio.transcriptions.create(
                        model=self.stt_model,
                        file=audio_file,
                        language=language,
                    )
                    return response.text
                except Exception:
                    # x.ai might not support STT yet, fallback to OpenAI
                    if self.openai_client and self.fallback_to_openai:
                        # Reset the BytesIO position for retry
                        audio_file.seek(0)
                    else:
                        raise

            # Fallback to OpenAI for STT
            if self.openai_client:
                response = self.openai_client.audio.transcriptions.create(
                    model=self.stt_model,
                    file=audio_file,
                    language=language,
                )
                return response.text

            raise RuntimeError("No STT service available")
        except Exception as e:
            raise RuntimeError(f"STT conversion failed: {e!s}") from e

    @staticmethod
    def get_rex_system_prompt() -> str:
        """Get the Rex personality system prompt."""
        return REX_SYSTEM_PROMPT

    def is_available(self) -> bool:
        """Check if voice service is available and configured."""
        return bool(self.xai_api_key or self.openai_api_key)

    def get_voice_provider(self) -> str:
        """Get the current voice provider being used."""
        if self.use_xai and self.xai_api_key:
            return "x.ai (with OpenAI fallback)" if self.openai_client else "x.ai"
        elif self.openai_client:
            return "OpenAI"
        return "None"


def get_voice_service(
    api_key: Optional[str] = None,
    use_xai: bool = True,
    fallback_to_openai: bool = True,
) -> VoiceService:
    """
    Get or create voice service instance.

    Args:
        api_key: Optional API key override
        use_xai: Use x.ai API endpoint (default: True)
        fallback_to_openai: Fallback to OpenAI if x.ai doesn't support voice (default: True)

    Returns:
        VoiceService instance

    """
    return VoiceService(
        api_key=api_key,
        use_xai=use_xai,
        fallback_to_openai=fallback_to_openai,
    )
