"""Google Gemini client for multimodal processing."""

import os
from typing import Any, Dict, List, Optional

import google.generativeai as genai


class GeminiClient:
    """Client for Google Gemini API."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "gemini-1.5-pro-latest"
    ) -> None:
        """Initialize Gemini client.
        
        Args:
            api_key: Google AI API key (or use GOOGLE_AI_API_KEY env var)
            model: Model name to use
        """
        api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model)
        else:
            self.model = None
        self.model_name = model
    
    def is_available(self) -> bool:
        """Check if client is available (has API key).
        
        Returns:
            True if API key is configured
        """
        return self.model is not None

    async def generate(
        self, prompt: str, temperature: float = 0.7, max_output_tokens: int = 2048
    ) -> str:
        """Generate text response.
        
        Args:
            prompt: Text prompt
            temperature: Sampling temperature
            max_output_tokens: Maximum output tokens
            
        Returns:
            Generated text
            
        Raises:
            RuntimeError: If API key is not configured
        """
        if not self.model:
            raise RuntimeError("GOOGLE_AI_API_KEY not configured")
        
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        response = await self.model.generate_content_async(
            prompt, generation_config=generation_config
        )
        return response.text

    async def analyze_image(self, image_data: bytes, prompt: str) -> Dict[str, Any]:
        """Analyze image (e.g., HUD screenshot).
        
        Args:
            image_data: Image bytes
            prompt: Analysis prompt
            
        Returns:
            Analysis results
        """
        # Create image part
        image_part = {"mime_type": "image/jpeg", "data": image_data}

        response = await self.model.generate_content_async([prompt, image_part])

        return {
            "analysis": response.text,
            "type": "image",
        }

    async def transcribe_audio(self, audio_data: bytes, mime_type: str = "audio/wav") -> str:
        """Transcribe audio file.
        
        Args:
            audio_data: Audio bytes
            mime_type: Audio MIME type
            
        Returns:
            Transcript text
        """
        audio_part = {"mime_type": mime_type, "data": audio_data}

        prompt = "Transcribe this audio accurately. Include emotional tone observations."
        response = await self.model.generate_content_async([prompt, audio_part])

        return response.text

    async def analyze_video(self, video_data: bytes, mime_type: str = "video/mp4") -> Dict[str, Any]:
        """Analyze video session for body language and tilt cues.
        
        Args:
            video_data: Video bytes
            mime_type: Video MIME type
            
        Returns:
            Video analysis with timestamped insights
        """
        video_part = {"mime_type": mime_type, "data": video_data}

        prompt = (
            "Analyze this poker session video. Identify:\n"
            "1. Body language patterns\n"
            "2. Emotional state changes\n"
            "3. Tilt indicators (frustration, anger, resignation)\n"
            "4. Timeline of key moments\n"
            "Provide timestamped observations."
        )

        response = await self.model.generate_content_async([prompt, video_part])

        return {
            "timeline": response.text,
            "type": "video",
        }

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Response text
        """
        # Convert messages to Gemini format
        chat = self.model.start_chat(history=[])
        
        for msg in messages[:-1]:
            if msg["role"] == "user":
                chat.send_message_async(msg["content"])
        
        # Send final message
        response = await chat.send_message_async(messages[-1]["content"])
        return response.text
