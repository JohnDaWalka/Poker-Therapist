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
        self.api_key = api_key
        if api_key:
            self.client = openai.AsyncOpenAI(api_key=api_key)
        else:
            self.client = None
        self.model = model
    
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
        max_tokens: int = 2048,
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
        if not self.client:
            raise RuntimeError("OPENAI_API_KEY not configured")
        
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

    async def session_review(self, session_hands: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Review a post-session batch of hands.

        This is used when the user wants "Therapist" to review an entire session
        rather than a single hand.
        """
        system_prompt = (
            "You are Therapy Rex: a high-performance poker sports therapist + mental-game coach. "
            "Given a batch of hands from one session, identify strategic leaks, recurring decision patterns, "
            "and mental-game triggers. You are direct, grounded, process-focused, and action-oriented. "
            "You must also report Provably Fair / RNG Proof status when provided in context."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    "Review my session hands below.\n\n"
                    "Return sections (use these exact headings):\n"
                    "1) Provably Fair / RNG Proof\n"
                    "2) Session Summary\n"
                    "3) Strategic Leaks\n"
                    "4) Mental Game Notes\n"
                    "5) Action Items\n\n"
                    "In 'Provably Fair / RNG Proof':\n"
                    "- Use context fields rng_verified_count, num_hands, rng_verified_lines_total, rng_verifiable_lines_total, rng_mismatch_total.\n"
                    "- If rng_mismatch_total > 0, mention that verification did not fully match and cite 1-2 mismatch samples (rng_mismatch_samples).\n"
                    "- If rng_verifiable_lines_total == 0, say RNG proof was not verifiable from the export.\n\n"
                    f"Hands:\n{session_hands}\n\nContext (JSON): {context}"
                ),
            },
        ]

        response = await self.chat(messages, temperature=0.3, max_tokens=2048)
        return {
            "session_review": response["content"],
            "usage": response["usage"],
        }
    
    async def quick_triage(self, context: Dict[str, Any]) -> str:
        """Quick triage response for immediate tilt intervention.
        
        Used as fallback when Grok is not available.
        
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
        return response["content"]
