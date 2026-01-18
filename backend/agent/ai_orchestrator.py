"""AI Orchestrator for routing requests to appropriate models."""

import asyncio
from typing import Any, Dict, List, Optional

from backend.models import (
    ClaudeClient,
    GeminiClient,
    GrokClient,
    OpenAIClient,
    PerplexityClient,
)


class AIOrchestrator:
    """Orchestrates AI model selection and request routing."""

    def __init__(self) -> None:
        """Initialize AI clients."""
        self.grok = GrokClient()
        self.perplexity = PerplexityClient()
        self.claude = ClaudeClient()
        self.openai = OpenAIClient()
        self.gemini = GeminiClient()
    
    def _get_available_triage_client(self) -> tuple[Any, str]:
        """Get available client for triage (Grok first, OpenAI fallback).
        
        Returns:
            Tuple of (client, model_name)
            
        Raises:
            RuntimeError: If no triage client is available
        """
        if self.grok.is_available():
            return (self.grok, "grok")
        elif self.openai.is_available():
            return (self.openai, "openai")
        else:
            raise RuntimeError(
                "No triage client available. Configure XAI_API_KEY or OPENAI_API_KEY."
            )

    async def route_query(self, query_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to appropriate AI model(s).
        
        Args:
            query_type: Type of query (quick_triage, deep_therapy, etc.)
            context: Request context data
            
        Returns:
            Response dict from AI model(s)
        """
        if query_type == "quick_triage":
            # Fast response - Grok preferred, OpenAI fallback
            client, model = self._get_available_triage_client()
            response = await client.quick_triage(context)
            return {"response": response, "model": model}

        elif query_type == "deep_therapy":
            # Claude primary + optional Perplexity research
            if not self.claude.is_available():
                raise RuntimeError(
                    "Deep therapy requires Claude. Configure ANTHROPIC_API_KEY."
                )
            
            claude_response = await self.claude.deep_therapy(context)
            
            if context.get("needs_research") and self.perplexity.is_available():
                research = await self.perplexity.research_topic(
                    context.get("research_query", "")
                )
                return self._merge_therapy_research(claude_response, research)
            
            return claude_response

        elif query_type == "hand_analysis":
            # Parallel: Perplexity + OpenAI + optional Gemini (if image)
            tasks: List[Any] = []
            available_models = []
            
            if self.perplexity.is_available():
                tasks.append(
                    self.perplexity.analyze_hand(
                        context.get("hand_history", ""), context
                    )
                )
                available_models.append("perplexity")
            
            if self.openai.is_available():
                tasks.append(
                    self.openai.gto_analysis(
                        context.get("hand_history", ""), context
                    )
                )
                available_models.append("openai")
            
            if not tasks:
                raise RuntimeError(
                    "Hand analysis requires Perplexity or OpenAI. Configure PERPLEXITY_API_KEY or OPENAI_API_KEY."
                )
            
            if context.get("image_data") and self.gemini.is_available():
                tasks.append(
                    self.gemini.analyze_image(
                        context["image_data"],
                        "Analyze this poker HUD screenshot. Identify key stats and patterns.",
                    )
                )
                available_models.append("gemini")
            
            responses = await asyncio.gather(*tasks)
            return self._synthesize_hand_analysis(
                responses, 
                has_image=bool(context.get("image_data") and self.gemini.is_available()),
                models=available_models
            )

        elif query_type == "session_review":
            # Post-session multi-hand review
            session_hands = context.get("session_hands", "")
            tasks = []
            available_models = []
            
            if self.perplexity.is_available():
                tasks.append(self.perplexity.session_review(session_hands, context))
                available_models.append("perplexity")
            
            if self.openai.is_available():
                tasks.append(self.openai.session_review(session_hands, context))
                available_models.append("openai")
            
            if not tasks:
                raise RuntimeError(
                    "Session review requires Perplexity or OpenAI. Configure PERPLEXITY_API_KEY or OPENAI_API_KEY."
                )
            
            responses = await asyncio.gather(*tasks)
            
            # Build response based on available models
            result = {"models": available_models}
            if self.perplexity.is_available():
                perplexity_idx = available_models.index("perplexity")
                result["strategy_review"] = responses[perplexity_idx].get("analysis", "")
                result["citations"] = responses[perplexity_idx].get("citations", [])
            if self.openai.is_available():
                openai_idx = available_models.index("openai")
                result["therapy_review"] = responses[openai_idx].get("session_review", "")
            
            return result

        elif query_type == "voice_rant":
            # Gemini transcription + Claude therapy
            if not self.gemini.is_available():
                raise RuntimeError(
                    "Voice rant requires Gemini for transcription. Configure GOOGLE_AI_API_KEY."
                )
            if not self.claude.is_available():
                raise RuntimeError(
                    "Voice rant requires Claude for therapy. Configure ANTHROPIC_API_KEY."
                )
            
            transcript = await self.gemini.transcribe_audio(
                context["audio_data"],
                context.get("mime_type", "audio/wav"),
            )
            
            therapy_context = {
                **context,
                "transcript": transcript,
                "emotional_state": {"from_voice": True},
            }
            
            therapy_response = await self.claude.deep_therapy(therapy_context)
            
            return {
                "transcript": transcript,
                "therapeutic_response": therapy_response["session_summary"],
                "models": ["gemini", "claude"],
            }

        elif query_type == "session_video":
            # Gemini video analysis + Claude interpretation
            if not self.gemini.is_available():
                raise RuntimeError(
                    "Session video requires Gemini for video analysis. Configure GOOGLE_AI_API_KEY."
                )
            if not self.claude.is_available():
                raise RuntimeError(
                    "Session video requires Claude for interpretation. Configure ANTHROPIC_API_KEY."
                )
            
            video_insights = await self.gemini.analyze_video(
                context["video_data"],
                context.get("mime_type", "video/mp4"),
            )
            
            interpretation = await self.claude.interpret_multimodal(
                video_insights, context
            )
            
            return {
                "video_analysis": video_insights["timeline"],
                "psychological_interpretation": interpretation,
                "models": ["gemini", "claude"],
            }

        else:
            raise ValueError(f"Unknown query type: {query_type}")

    def _merge_therapy_research(
        self, therapy: Dict[str, Any], research: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge therapy session with research insights.
        
        Args:
            therapy: Claude therapy response
            research: Perplexity research response
            
        Returns:
            Merged response
        """
        return {
            "session_summary": therapy["session_summary"],
            "research_insights": research["answer"],
            "citations": research.get("citations", []),
            "therapeutic_approach": therapy["therapeutic_approach"],
            "models": ["claude", "perplexity"],
        }

    def _synthesize_hand_analysis(
        self, responses: List[Dict[str, Any]], has_image: bool = False, models: List[str] = None
    ) -> Dict[str, Any]:
        """Synthesize multi-model hand analysis.
        
        Args:
            responses: List of model responses
            has_image: Whether image analysis was included
            models: List of available model names
            
        Returns:
            Synthesized analysis
        """
        if models is None:
            models = []
        
        result: Dict[str, Any] = {"models": models}
        
        # Add responses based on which models are available
        for idx, model in enumerate(models):
            if model == "perplexity" and idx < len(responses):
                result["meta_context"] = responses[idx].get("analysis", "")
            elif model == "openai" and idx < len(responses):
                result["gto_analysis"] = responses[idx].get("gto_analysis", "")
            elif model == "gemini" and idx < len(responses) and has_image:
                result["hud_insights"] = responses[idx].get("analysis", "")
        
        return result
