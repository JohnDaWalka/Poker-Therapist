"""Voice cloning service for custom Rex voice profiles."""

import os
from pathlib import Path
from typing import Optional

import numpy as np


class VoiceProfile:
    """Voice profile for custom voice synthesis."""
    
    def __init__(
        self,
        profile_id: str,
        name: str,
        voice_samples: list[bytes],
        description: Optional[str] = None,
    ) -> None:
        """
        Initialize voice profile.
        
        Args:
            profile_id: Unique profile identifier
            name: Profile name
            voice_samples: List of audio samples for voice cloning
            description: Optional profile description
        """
        self.profile_id = profile_id
        self.name = name
        self.voice_samples = voice_samples
        self.description = description
        self.created_at = None  # Would be set in production
    
    def to_dict(self) -> dict:
        """Convert profile to dictionary."""
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "sample_count": len(self.voice_samples),
            "description": self.description,
        }


class VoiceCloningService:
    """Service for voice cloning and custom voice synthesis."""
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        use_coqui_tts: bool = True,
    ) -> None:
        """
        Initialize voice cloning service.
        
        Args:
            model_path: Path to voice cloning model
            use_coqui_tts: Use Coqui TTS for voice cloning
        """
        self.model_path = model_path
        self.use_coqui_tts = use_coqui_tts
        self.profiles: dict[str, VoiceProfile] = {}
        self.tts_model = None
        
        # Initialize TTS model if available
        if use_coqui_tts:
            try:
                self._init_tts_model()
            except ImportError:
                self.use_coqui_tts = False
    
    def _init_tts_model(self) -> None:
        """Initialize Coqui TTS model (lazy loading)."""
        try:
            from TTS.api import TTS
            
            # Initialize with default voice cloning model
            # In production, would select appropriate model based on requirements
            # Example: "tts_models/multilingual/multi-dataset/xtts_v2"
            self.tts_model = None  # Lazy load on first use
        except ImportError:
            pass
    
    def create_profile(
        self,
        name: str,
        voice_samples: list[bytes],
        description: Optional[str] = None,
    ) -> VoiceProfile:
        """
        Create new voice profile from audio samples.
        
        Args:
            name: Profile name
            voice_samples: List of audio samples (minimum 3 recommended)
            description: Optional description
            
        Returns:
            Created voice profile
            
        Raises:
            ValueError: If insufficient voice samples provided
        """
        if len(voice_samples) < 1:
            raise ValueError("At least 1 voice sample required for cloning")
        
        # Generate unique profile ID
        import hashlib
        profile_id = hashlib.md5(f"{name}{len(voice_samples)}".encode()).hexdigest()[:12]
        
        # Create profile
        profile = VoiceProfile(
            profile_id=profile_id,
            name=name,
            voice_samples=voice_samples,
            description=description,
        )
        
        # Store profile
        self.profiles[profile_id] = profile
        
        return profile
    
    def synthesize_with_profile(
        self,
        text: str,
        profile: VoiceProfile,
        language: str = "en",
    ) -> bytes:
        """
        Synthesize speech using custom voice profile.
        
        Args:
            text: Text to synthesize
            profile: Voice profile to use
            language: Language code
            
        Returns:
            Audio data as bytes
            
        Raises:
            RuntimeError: If synthesis fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            if self.use_coqui_tts and self.tts_model:
                # Use Coqui TTS for voice cloning
                return self._synthesize_coqui(text, profile, language)
            else:
                # Fallback to OpenAI with voice profile metadata
                # In production, would use actual voice cloning
                from openai import OpenAI
                
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise RuntimeError("OpenAI API key required for voice synthesis")
                
                client = OpenAI(api_key=api_key)
                
                # Use standard voice as fallback
                # Note: OpenAI doesn't support custom voice cloning yet
                # This would be replaced with actual cloning API when available
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="onyx",  # Default voice
                    input=text,
                )
                
                return response.content
        except Exception as e:
            raise RuntimeError(f"Voice synthesis failed: {e}") from e
    
    def _synthesize_coqui(
        self,
        text: str,
        profile: VoiceProfile,
        language: str,
    ) -> bytes:
        """
        Synthesize using Coqui TTS.
        
        Args:
            text: Text to synthesize
            profile: Voice profile
            language: Language code
            
        Returns:
            Audio data as bytes
        """
        try:
            # Lazy load TTS model
            if self.tts_model is None:
                from TTS.api import TTS
                
                # Use XTTS v2 for voice cloning
                self.tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            
            # Use first voice sample as speaker reference
            # In production, would use all samples or create speaker embedding
            import tempfile
            import wave
            
            # Save reference audio to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as ref_file:
                ref_path = ref_file.name
                
                # Write audio data (simplified - assumes WAV format)
                ref_file.write(profile.voice_samples[0])
            
            # Synthesize with voice cloning
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out_file:
                out_path = out_file.name
            
            try:
                self.tts_model.tts_to_file(
                    text=text,
                    file_path=out_path,
                    speaker_wav=ref_path,
                    language=language,
                )
                
                # Read synthesized audio
                with open(out_path, "rb") as f:
                    audio_data = f.read()
                
                return audio_data
            finally:
                # Cleanup temp files
                Path(ref_path).unlink(missing_ok=True)
                Path(out_path).unlink(missing_ok=True)
        except Exception as e:
            raise RuntimeError(f"Coqui TTS synthesis failed: {e}") from e
    
    def get_profile(self, profile_id: str) -> Optional[VoiceProfile]:
        """
        Get voice profile by ID.
        
        Args:
            profile_id: Profile identifier
            
        Returns:
            Voice profile or None if not found
        """
        return self.profiles.get(profile_id)
    
    def list_profiles(self) -> list[VoiceProfile]:
        """
        List all voice profiles.
        
        Returns:
            List of voice profiles
        """
        return list(self.profiles.values())
    
    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete voice profile.
        
        Args:
            profile_id: Profile identifier
            
        Returns:
            True if deleted, False if not found
        """
        if profile_id in self.profiles:
            del self.profiles[profile_id]
            return True
        return False
    
    def validate_audio_sample(self, audio_data: bytes) -> dict:
        """
        Validate audio sample for voice cloning.
        
        Args:
            audio_data: Audio data to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            import librosa
            from io import BytesIO
            
            # Load audio
            audio_io = BytesIO(audio_data)
            y, sr = librosa.load(audio_io, sr=None)
            
            # Check duration
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Check quality metrics
            is_valid = True
            issues = []
            
            if duration < 3.0:
                is_valid = False
                issues.append("Audio too short (minimum 3 seconds recommended)")
            
            if duration > 30.0:
                issues.append("Audio is long (10-15 seconds recommended for best results)")
            
            # Check if audio has sufficient energy
            rms = np.sqrt(np.mean(y**2))
            if rms < 0.01:
                is_valid = False
                issues.append("Audio too quiet - ensure clear speech")
            
            return {
                "valid": is_valid,
                "duration": duration,
                "sample_rate": sr,
                "issues": issues,
                "recommendations": [
                    "Use clear, noise-free audio",
                    "Record in a quiet environment",
                    "Speak naturally and clearly",
                    "Use 10-15 seconds of audio per sample",
                ],
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "issues": ["Failed to analyze audio sample"],
            }
    
    def is_available(self) -> bool:
        """Check if voice cloning is available."""
        return self.use_coqui_tts or bool(os.getenv("OPENAI_API_KEY"))


def get_cloning_service(
    model_path: Optional[str] = None,
    use_coqui_tts: bool = True,
) -> VoiceCloningService:
    """
    Get voice cloning service instance.
    
    Args:
        model_path: Path to voice cloning model
        use_coqui_tts: Use Coqui TTS for voice cloning
        
    Returns:
        VoiceCloningService instance
    """
    return VoiceCloningService(
        model_path=model_path,
        use_coqui_tts=use_coqui_tts,
    )
