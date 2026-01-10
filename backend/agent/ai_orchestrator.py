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

    async def route_query(self, query_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to appropriate AI model(s).
        
        Args:
            query_type: Type of query (quick_triage, deep_therapy, etc.)
            context: Request context data
            
        Returns:
            Response dict from AI model(s)
        """
        if query_type == "quick_triage":
            # Fast response - Grok
            response = await self.grok.quick_triage(context)
            return {"response": response, "model": "grok"}

        elif query_type == "deep_therapy":
            # Claude primary + optional Perplexity research
            claude_response = await self.claude.deep_therapy(context)
            
            if context.get("needs_research"):
                research = await self.perplexity.research_topic(
                    context.get("research_query", "")
                )
                return self._merge_therapy_research(claude_response, research)
            
            return claude_response

        elif query_type == "hand_analysis":
            # Parallel: Perplexity + OpenAI + optional Gemini (if image)
            tasks: List[Any] = [
                self.perplexity.analyze_hand(
                    context.get("hand_history", ""), context
                ),
                self.openai.gto_analysis(
                    context.get("hand_history", ""), context
                ),
            ]
            
            if context.get("image_data"):
                tasks.append(
                    self.gemini.analyze_image(
                        context["image_data"],
                        "Analyze this poker HUD screenshot. Identify key stats and patterns.",
                    )
                )
            
            responses = await asyncio.gather(*tasks)
            return self._synthesize_hand_analysis(responses, has_image=bool(context.get("image_data")))

        elif query_type == "session_review":
            # Post-session multi-hand review
            session_hands = context.get("session_hands", "")
            tasks = [
                self.perplexity.session_review(session_hands, context),
                self.openai.session_review(session_hands, context),
            ]
            responses = await asyncio.gather(*tasks)
            return {
                "strategy_review": responses[0].get("analysis", ""),
                "therapy_review": responses[1].get("session_review", ""),
                "citations": responses[0].get("citations", []),
                "models": ["perplexity", "openai"],
            }

        elif query_type == "voice_rant":
            # Gemini transcription + Claude therapy
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
        self, responses: List[Dict[str, Any]], has_image: bool = False
    ) -> Dict[str, Any]:
        """Synthesize multi-model hand analysis.
        
        Args:
            responses: List of model responses
            has_image: Whether image analysis was included
            
        Returns:
            Synthesized analysis
        """
        result: Dict[str, Any] = {
            "meta_context": responses[0].get("analysis", ""),
            "gto_analysis": responses[1].get("gto_analysis", ""),
            "models": ["perplexity", "openai"],
        }
        
        if has_image and len(responses) > 2:
            result["hud_insights"] = responses[2].get("analysis", "")
            result["models"].append("gemini")
        
        return result
