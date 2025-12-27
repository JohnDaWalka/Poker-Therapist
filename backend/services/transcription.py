"""
Transcription Service using OpenAI Whisper API

This module provides voice transcription functionality using OpenAI's Whisper API.
It accepts audio file paths and returns transcribed text with comprehensive error handling.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import openai
from openai import OpenAI

# Configure logging
logger = logging.getLogger(__name__)


class TranscriptionError(Exception):
    """Custom exception for transcription-related errors."""
    pass


class TranscriptionService:
    """Service for transcribing audio files using OpenAI Whisper API."""
    
    # Supported audio formats by Whisper API
    SUPPORTED_FORMATS = {
        '.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', 
        '.wav', '.webm', '.ogg', '.flac'
    }
    
    # Maximum file size in bytes (25 MB for Whisper API)
    MAX_FILE_SIZE = 25 * 1024 * 1024
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the transcription service.
        
        Args:
            api_key: OpenAI API key. If not provided, will use OPENAI_API_KEY environment variable.
            
        Raises:
            TranscriptionError: If API key is not provided or found in environment.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise TranscriptionError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        logger.info("TranscriptionService initialized successfully")
    
    def _validate_audio_file(self, file_path: str) -> Path:
        """
        Validate the audio file path and format.
        
        Args:
            file_path: Path to the audio file.
            
        Returns:
            Path object of the validated file.
            
        Raises:
            TranscriptionError: If file validation fails.
        """
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            raise TranscriptionError(f"Audio file not found: {file_path}")
        
        # Check if it's a file (not a directory)
        if not path.is_file():
            raise TranscriptionError(f"Path is not a file: {file_path}")
        
        # Check file extension
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise TranscriptionError(
                f"Unsupported audio format: {path.suffix}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        # Check file size
        file_size = path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise TranscriptionError(
                f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds "
                f"maximum allowed size ({self.MAX_FILE_SIZE / 1024 / 1024} MB)"
            )
        
        if file_size == 0:
            raise TranscriptionError("Audio file is empty")
        
        return path
    
    def transcribe(
        self, 
        file_path: str, 
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0,
        response_format: str = "text"
    ) -> str:
        """
        Transcribe an audio file using OpenAI Whisper API.
        
        Args:
            file_path: Path to the audio file to transcribe.
            language: Optional ISO-639-1 language code (e.g., 'en', 'es').
            prompt: Optional text to guide the model's style or continue a previous segment.
            temperature: Sampling temperature between 0 and 1. Lower is more deterministic.
            response_format: Format of the response ('text', 'json', 'srt', 'vtt', 'verbose_json').
            
        Returns:
            Transcribed text from the audio file.
            
        Raises:
            TranscriptionError: If transcription fails for any reason.
        """
        try:
            # Validate the audio file
            audio_path = self._validate_audio_file(file_path)
            
            logger.info(f"Starting transcription for file: {audio_path}")
            
            # Open and transcribe the audio file
            with open(audio_path, 'rb') as audio_file:
                # Prepare API parameters
                transcription_params = {
                    "model": "whisper-1",
                    "file": audio_file,
                    "response_format": response_format,
                    "temperature": temperature
                }
                
                # Add optional parameters if provided
                if language:
                    transcription_params["language"] = language
                
                if prompt:
                    transcription_params["prompt"] = prompt
                
                # Call Whisper API
                transcript = self.client.audio.transcriptions.create(**transcription_params)
            
            # Extract text based on response format
            if response_format == "text":
                result = transcript
            elif response_format in ["json", "verbose_json"]:
                result = transcript.text
            else:
                result = transcript
            
            logger.info(f"Transcription completed successfully for: {audio_path}")
            return result
            
        except TranscriptionError:
            # Re-raise custom exceptions
            raise
        except openai.APIError as e:
            logger.error(f"OpenAI API error during transcription: {e}")
            raise TranscriptionError(f"API error: {str(e)}")
        except openai.AuthenticationError as e:
            logger.error(f"Authentication error with OpenAI API: {e}")
            raise TranscriptionError("Authentication failed. Check your API key.")
        except openai.RateLimitError as e:
            logger.error(f"Rate limit exceeded: {e}")
            raise TranscriptionError("Rate limit exceeded. Please try again later.")
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {e}", exc_info=True)
            raise TranscriptionError(f"Transcription failed: {str(e)}")
    
    def transcribe_with_metadata(
        self, 
        file_path: str, 
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe an audio file and return detailed metadata.
        
        Args:
            file_path: Path to the audio file to transcribe.
            language: Optional ISO-639-1 language code.
            prompt: Optional text to guide the model's style.
            
        Returns:
            Dictionary containing transcribed text and metadata.
            
        Raises:
            TranscriptionError: If transcription fails for any reason.
        """
        try:
            # Validate the audio file
            audio_path = self._validate_audio_file(file_path)
            
            logger.info(f"Starting transcription with metadata for: {audio_path}")
            
            # Open and transcribe the audio file with verbose JSON format
            with open(audio_path, 'rb') as audio_file:
                transcription_params = {
                    "model": "whisper-1",
                    "file": audio_file,
                    "response_format": "verbose_json",
                    "temperature": 0.0
                }
                
                if language:
                    transcription_params["language"] = language
                
                if prompt:
                    transcription_params["prompt"] = prompt
                
                transcript = self.client.audio.transcriptions.create(**transcription_params)
            
            # Build result with metadata
            result = {
                "text": transcript.text,
                "language": transcript.language,
                "duration": transcript.duration,
                "segments": transcript.segments if hasattr(transcript, 'segments') else []
            }
            
            logger.info(f"Transcription with metadata completed for: {audio_path}")
            return result
            
        except TranscriptionError:
            raise
        except Exception as e:
            logger.error(f"Error during transcription with metadata: {e}", exc_info=True)
            raise TranscriptionError(f"Transcription failed: {str(e)}")


# Convenience function for simple transcription
def transcribe_audio(file_path: str, api_key: Optional[str] = None) -> str:
    """
    Convenience function to transcribe an audio file.
    
    Args:
        file_path: Path to the audio file to transcribe.
        api_key: Optional OpenAI API key.
        
    Returns:
        Transcribed text from the audio file.
        
    Raises:
        TranscriptionError: If transcription fails.
    """
    service = TranscriptionService(api_key=api_key)
    return service.transcribe(file_path)
