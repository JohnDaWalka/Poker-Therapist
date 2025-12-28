"""Tilt triage session handler."""

from typing import Any, Dict

from backend.agent.ai_orchestrator import AIOrchestrator
from backend.agent.protocols.safety import check_safety_escalation, get_safety_guidance
from backend.agent.protocols.tilt_detection import detect_tilt_patterns


class TiltTriageSession:
    """Handler for 5-10 minute tilt triage sessions."""

    def __init__(self, orchestrator: AIOrchestrator) -> None:
        """Initialize triage session handler.
        
        Args:
            orchestrator: AI orchestrator instance
        """
        self.orchestrator = orchestrator

    async def conduct(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct triage session.
        
        Args:
            context: Session context with situation, emotion, intensity, etc.
            
        Returns:
            Triage results dict
        """
        # Safety check
        safety = check_safety_escalation(context)
        
        # Detect tilt patterns
        patterns = detect_tilt_patterns(context)
        
        # Get safety-appropriate guidance
        guidance = get_safety_guidance(safety["severity"])
        
        # Get AI response (only if not emergency)
        ai_response = ""
        if not safety.get("needs_escalation"):
            ai_response = await self.orchestrator.route_query("quick_triage", context)
        
        # Build micro action plan
        micro_plan = self._build_micro_plan(
            patterns["primary_trigger"],
            guidance["immediate_steps"],
        )
        
        return {
            "severity": safety["severity"],
            "should_stop": safety["should_stop_playing"],
            "patterns_detected": patterns["patterns"],
            "primary_trigger": patterns["primary_trigger"],
            "ai_guidance": ai_response.get("response", "") if ai_response else "",
            "safety_guidance": guidance["guidance"],
            "breathing_exercise": guidance["breathing_exercise"],
            "micro_plan": micro_plan,
            "emergency_contacts": safety.get("emergency_contacts", []),
            "warning_message": safety.get("warning_message") or safety.get("emergency_message", ""),
        }

    def _build_micro_plan(
        self, trigger: str, immediate_steps: list[str]
    ) -> list[str]:
        """Build micro action plan.
        
        Args:
            trigger: Primary tilt trigger
            immediate_steps: Immediate safety steps
            
        Returns:
            Micro plan list
        """
        plan = immediate_steps.copy()
        
        # Add trigger-specific actions
        trigger_actions = {
            "variance_tilt": "Review equity calculator for this spot",
            "mistake_tilt": "Add this hand to study queue",
            "justice_tilt": "List 3 exploitable patterns from this player",
            "revenge_tilt": "Calculate EV of revenge play vs optimal play",
            "boredom_tilt": "Set timer for 30-min focused session",
        }
        
        if trigger in trigger_actions:
            plan.append(trigger_actions[trigger])
        
        return plan
