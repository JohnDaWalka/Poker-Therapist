"""Grok AI client for X.AI API."""

import os
from typing import Any, Dict, List, Optional

import httpx


class GrokClient:
    """Client for X.AI Grok API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "grok-2-latest") -> None:
        """Initialize Grok client.
        
        Args:
            api_key: X.AI API key (or use XAI_API_KEY env var)
            model: Model name to use
        """
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        self.model = model
        self.base_url = "https://api.x.ai/v1/chat/completions"
    
    def is_available(self) -> bool:
        """Check if client is available (has API key).
        
        Returns:
            True if API key is configured
        """
        return bool(self.api_key)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """Send chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            API response dict
            
        Raises:
            RuntimeError: If API key is not configured
        """
        if not self.api_key:
            raise RuntimeError("XAI_API_KEY not configured")
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.base_url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def quick_triage(self, context: Dict[str, Any]) -> str:
        """Quick triage response for immediate tilt intervention.
        
        Args:
            context: Dict with situation, emotion, intensity, etc.
            
        Returns:
            Triage guidance text
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Therapy Rex, a poker mental game coach. "
                    "Provide immediate, compassionate triage for tilt situations. "
                    "Be direct, supportive, and action-oriented."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Situation: {context.get('situation', '')}\n"
                    f"Emotion: {context.get('emotion', '')}\n"
                    f"Intensity: {context.get('intensity', 0)}/10\n"
                    f"Body Sensation: {context.get('body_sensation', '')}\n"
                    f"Still Playing: {context.get('still_playing', False)}"
                ),
            },
        ]

        response = await self.chat(messages, temperature=0.5)
        return response["choices"][0]["message"]["content"]
