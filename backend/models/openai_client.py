"""OpenAI GPT client for GTO analysis."""

import os
from typing import Any, Dict, List, Optional

import openai


class OpenAIClient:
    """Client for OpenAI GPT API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview") -> None:
        """Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (or use OPENAI_API_KEY env var)
            model: Model name to use
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Set OPENAI_API_KEY in env or pass api_key parameter")
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model

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
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return {
            "content": response.choices[0].message.content,
            "usage": response.usage.model_dump(),
        }

    async def gto_analysis(self, hand_history: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform GTO analysis of poker hand.
        
        Args:
            hand_history: Poker hand history text
            context: Additional context dict
            
        Returns:
            GTO analysis with EV calculations
        """
        system_prompt = (
            "You are an expert poker GTO analyst. Analyze hands using game theory optimal "
            "strategies, calculate expected values, and evaluate decision trees. "
            "Provide precise mathematical analysis."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Analyze this hand from a GTO perspective:\n\n{hand_history}\n\n"
                    f"Additional context: {context}"
                ),
            },
        ]

        response = await self.chat(messages, temperature=0.2)
        
        return {
            "gto_analysis": response["content"],
            "approach": "Game Theory Optimal",
            "usage": response["usage"],
        }

    async def strategic_coaching(self, query: str) -> str:
        """Provide strategic poker coaching.
        
        Args:
            query: Strategic question or scenario
            
        Returns:
            Strategic guidance
        """
        messages = [
            {
                "role": "system",
                "content": "You are an expert poker coach specializing in optimal strategy.",
            },
            {"role": "user", "content": query},
        ]

        response = await self.chat(messages, temperature=0.5)
        return response["content"]
