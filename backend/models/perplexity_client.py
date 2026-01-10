"""Perplexity AI client for research and analysis."""

import os
from typing import Any, Dict, List, Optional

import httpx


class PerplexityClient:
    """Client for Perplexity AI API."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "llama-3.1-sonar-large-128k-online"
    ) -> None:
        """Initialize Perplexity client.
        
        Args:
            api_key: Perplexity API key (or use PERPLEXITY_API_KEY env var)
            model: Model name to use
        """
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise RuntimeError("Set PERPLEXITY_API_KEY in env or pass api_key parameter")
        self.model = model
        self.base_url = "https://api.perplexity.ai/chat/completions"

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """Send chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            API response dict
        """
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

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(self.base_url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def analyze_hand(self, hand_history: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze poker hand with meta context and research.
        
        Args:
            hand_history: Poker hand history text
            context: Additional context dict
            
        Returns:
            Analysis dict with meta insights
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a poker strategy analyst with access to current "
                    "meta analysis and tournament trends. Provide detailed hand "
                    "analysis with contextual research."
                ),
            },
            {
                "role": "user",
                "content": f"Analyze this hand:\n\n{hand_history}\n\nContext: {context}",
            },
        ]

        response = await self.chat(messages, temperature=0.3)
        return {
            "analysis": response["choices"][0]["message"]["content"],
            "citations": response.get("citations", []),
        }

    async def research_topic(self, query: str) -> Dict[str, Any]:
        """Research a poker-related topic.
        
        Args:
            query: Research query
            
        Returns:
            Research results with citations
        """
        messages = [
            {
                "role": "system",
                "content": "You are a poker research assistant. Provide accurate, cited information.",
            },
            {"role": "user", "content": query},
        ]

        response = await self.chat(messages)
        return {
            "answer": response["choices"][0]["message"]["content"],
            "citations": response.get("citations", []),
        }

    async def session_review(self, session_hands: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Research-backed review of a full session's hands."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a poker strategy analyst with access to current meta analysis. "
                    "Given a batch of hands from one session, identify recurring strategic issues "
                    "and provide evidence-based improvements."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Review the following session hands. Provide: Session Summary, 3-7 Key Leaks, "
                    "and concrete drills to fix them.\n\n"
                    f"Hands:\n{session_hands}\n\nContext: {context}"
                ),
            },
        ]

        response = await self.chat(messages, temperature=0.3)
        return {
            "analysis": response["choices"][0]["message"]["content"],
            "citations": response.get("citations", []),
        }
