"""Claude AI client for deep therapy sessions."""

import os
from typing import Any, Dict, List, Optional

import anthropic


class ClaudeClient:
    """Client for Anthropic Claude API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022") -> None:
        """Initialize Claude client.
        
        Args:
            api_key: Anthropic API key (or use ANTHROPIC_API_KEY env var)
            model: Model name to use
        """
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("Set ANTHROPIC_API_KEY in env or pass api_key parameter")
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """Send chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            API response dict
        """
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system or "",
            messages=messages,
        )

        return {
            "content": response.content[0].text,
            "usage": response.usage.model_dump(),
        }

    async def deep_therapy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct deep therapy session.
        
        Args:
            context: Session context with emotional state, themes, etc.
            
        Returns:
            Therapy response with reframes and action plan
        """
        system_prompt = (
            "You are Therapy Rex, a specialized poker mental game therapist. "
            "You use evidence-based techniques including CBT, DBT, and ACT. "
            "Provide deep, compassionate therapeutic guidance with cognitive reframes "
            "and actionable plans. Focus on hierarchy of needs mapping and "
            "psychological patterns specific to poker."
        )

        messages = [
            {
                "role": "user",
                "content": (
                    f"Emotional State: {context.get('emotional_state', {})}\n"
                    f"Recent Results: {context.get('recent_results', '')}\n"
                    f"Life Context: {context.get('life_context', '')}\n"
                    f"Recurring Themes: {context.get('recurring_themes', '')}\n\n"
                    "Please conduct a deep therapy session."
                ),
            }
        ]

        response = await self.chat(messages, system=system_prompt, temperature=0.6)
        
        return {
            "session_summary": response["content"],
            "therapeutic_approach": "CBT/DBT/ACT",
            "usage": response["usage"],
        }

    async def interpret_multimodal(
        self, visual_cues: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        """Interpret multimodal analysis from Gemini with therapeutic lens.
        
        Args:
            visual_cues: Visual analysis from Gemini
            context: Additional context
            
        Returns:
            Therapeutic interpretation
        """
        messages = [
            {
                "role": "user",
                "content": (
                    f"Visual Analysis:\n{visual_cues}\n\n"
                    f"Context:\n{context}\n\n"
                    "Provide therapeutic interpretation of these visual cues "
                    "and behavioral patterns."
                ),
            }
        ]

        system_prompt = (
            "You are a poker psychology expert analyzing body language and "
            "behavioral cues. Provide therapeutic insights and recommendations."
        )

        response = await self.chat(messages, system=system_prompt)
        return response["content"]
