"""Deep therapy session handler."""

from typing import Any, Dict

from backend.agent.ai_orchestrator import AIOrchestrator


class DeepTherapySession:
    """Handler for 45-90 minute deep therapy sessions."""

    def __init__(self, orchestrator: AIOrchestrator) -> None:
        """Initialize deep therapy session handler.
        
        Args:
            orchestrator: AI orchestrator instance
        """
        self.orchestrator = orchestrator

    async def conduct(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct deep therapy session.
        
        Args:
            context: Session context with emotional state, themes, etc.
            
        Returns:
            Therapy session results
        """
        # Check if research is needed
        needs_research = self._assess_research_needs(context)
        if needs_research:
            context["needs_research"] = True
            context["research_query"] = self._generate_research_query(context)
        
        # Conduct therapy session
        therapy_result = await self.orchestrator.route_query("deep_therapy", context)
        
        # Extract cognitive reframes
        reframes = self._extract_reframes(therapy_result.get("session_summary", ""))
        
        # Build action plan
        action_plan = self._build_action_plan(context, reframes)
        
        # Identify follow-up themes
        follow_up = self._identify_follow_up_themes(context, therapy_result)
        
        return {
            "session_summary": therapy_result.get("session_summary", ""),
            "cognitive_reframes": reframes,
            "action_plan": action_plan,
            "follow_up_themes": follow_up,
            "therapeutic_approach": therapy_result.get("therapeutic_approach", "CBT/DBT/ACT"),
            "research_insights": therapy_result.get("research_insights"),
            "citations": therapy_result.get("citations", []),
        }

    def _assess_research_needs(self, context: Dict[str, Any]) -> bool:
        """Assess if research is needed for this session.
        
        Args:
            context: Session context
            
        Returns:
            True if research needed
        """
        # Research needed if specific hands or tournament situations mentioned
        recent_results = context.get("recent_results", "").lower()
        return any(
            keyword in recent_results
            for keyword in ["tournament", "specific hand", "opponent", "meta"]
        )

    def _generate_research_query(self, context: Dict[str, Any]) -> str:
        """Generate research query based on context.
        
        Args:
            context: Session context
            
        Returns:
            Research query string
        """
        return f"Poker strategy analysis: {context.get('recent_results', '')}"

    def _extract_reframes(self, session_summary: str) -> list[str]:
        """Extract cognitive reframes from therapy session.
        
        Args:
            session_summary: AI-generated session summary
            
        Returns:
            List of cognitive reframes
        """
        # Simple extraction - look for reframe indicators
        reframes = []
        lines = session_summary.split("\n")
        
        for line in lines:
            if any(
                indicator in line.lower()
                for indicator in ["instead", "reframe", "alternative", "consider"]
            ):
                reframes.append(line.strip())
        
        # If no reframes found, provide defaults
        if not reframes:
            reframes = [
                "Focus on process over results",
                "Variance is expected and normal",
                "Emotional awareness is progress",
            ]
        
        return reframes[:5]  # Limit to top 5

    def _build_action_plan(
        self, context: Dict[str, Any], reframes: list[str]
    ) -> list[Dict[str, str]]:
        """Build structured action plan.
        
        Args:
            context: Session context
            reframes: Cognitive reframes
            
        Returns:
            List of action items
        """
        plan = [
            {
                "category": "Immediate",
                "action": "Practice 4-7-8 breathing daily before sessions",
                "timeline": "Start today",
            },
            {
                "category": "Study",
                "action": "Review 3 hands where emotional state affected decisions",
                "timeline": "Within 48 hours",
            },
            {
                "category": "Mental Game",
                "action": f"Journal on: {reframes[0] if reframes else 'emotional patterns'}",
                "timeline": "Daily for 1 week",
            },
        ]
        
        # Add context-specific actions
        if context.get("recurring_themes"):
            plan.append(
                {
                    "category": "Deep Work",
                    "action": f"Address pattern: {context['recurring_themes']}",
                    "timeline": "Schedule therapy appointment",
                }
            )
        
        return plan

    def _identify_follow_up_themes(
        self, context: Dict[str, Any], therapy_result: Dict[str, Any]
    ) -> list[str]:
        """Identify themes for follow-up sessions.
        
        Args:
            context: Session context
            therapy_result: Therapy result dict
            
        Returns:
            List of follow-up themes
        """
        themes = []
        
        # Check for recurring patterns
        if context.get("recurring_themes"):
            themes.append(f"Recurring: {context['recurring_themes']}")
        
        # Check emotional state
        emotional_state = context.get("emotional_state", {})
        if emotional_state.get("stress", 0) >= 7:
            themes.append("Stress management techniques")
        
        if emotional_state.get("confidence", 10) <= 3:
            themes.append("Confidence building")
        
        # Default themes if none identified
        if not themes:
            themes = [
                "Emotional regulation strategies",
                "Building resilience",
            ]
        
        return themes
