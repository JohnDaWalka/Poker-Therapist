"""Safety protocols for emergency situations."""

from typing import Any, Dict


def assess_severity(intensity: int, emotion: str, still_playing: bool) -> int:
    """Assess severity level of tilt situation.
    
    Args:
        intensity: Intensity rating 1-10
        emotion: Type of emotion
        still_playing: Whether user is still playing
        
    Returns:
        Severity level 1-10
    """
    severity = intensity
    
    # Increase severity for high-risk emotions
    high_risk_emotions = ["anger", "rage", "despair", "shame"]
    if emotion.lower() in high_risk_emotions:
        severity = min(10, severity + 1)
    
    # Increase severity if still playing at high intensity
    if still_playing and intensity >= 7:
        severity = min(10, severity + 1)
    
    return severity


def check_safety_escalation(context: Dict[str, Any]) -> Dict[str, Any]:
    """Check if safety escalation is needed.
    
    Args:
        context: Session context with intensity, emotion, etc.
        
    Returns:
        Safety assessment dict
    """
    severity = assess_severity(
        context.get("intensity", 0),
        context.get("emotion", ""),
        context.get("still_playing", False),
    )
    
    # Check for self-harm indicators
    situation = context.get("situation", "").lower()
    self_harm_keywords = [
        "hurt myself",
        "end it",
        "suicide",
        "kill myself",
        "not worth living",
    ]
    has_self_harm_indicator = any(keyword in situation for keyword in self_harm_keywords)
    
    result: Dict[str, Any] = {
        "severity": severity,
        "needs_escalation": severity >= 10 or has_self_harm_indicator,
        "should_stop_playing": severity >= 8 or has_self_harm_indicator,
        "emergency_contacts": [],
    }
    
    if has_self_harm_indicator:
        result["emergency_contacts"] = [
            {
                "name": "National Suicide Prevention Lifeline",
                "phone": "988",
                "available": "24/7",
            },
            {
                "name": "Crisis Text Line",
                "text": "Text HOME to 741741",
                "available": "24/7",
            },
        ]
        result["emergency_message"] = (
            "⚠️ EMERGENCY: Your message indicates you may be in crisis. "
            "Please reach out to a mental health professional immediately. "
            "Therapy Rex is not a substitute for professional mental health care."
        )
    
    elif severity >= 8:
        result["warning_message"] = (
            "🛑 HIGH SEVERITY: We strongly recommend stopping play immediately. "
            "Your current emotional state is significantly impacting your decision-making."
        )
    
    return result


def get_safety_guidance(severity: int) -> Dict[str, Any]:
    """Get safety-appropriate guidance based on severity.
    
    Args:
        severity: Severity level 1-10
        
    Returns:
        Guidance dict with recommendations
    """
    if severity >= 9:
        return {
            "action": "STOP_IMMEDIATELY",
            "guidance": (
                "Stop playing NOW. Take a minimum 24-hour break. "
                "Consider talking to a mental health professional."
            ),
            "breathing_exercise": "4-7-8 breathing (4 in, 7 hold, 8 out)",
            "immediate_steps": [
                "Close poker client immediately",
                "Step away from computer",
                "Practice breathing exercise",
                "Call a trusted friend or therapist",
            ],
        }
    elif severity >= 7:
        return {
            "action": "TAKE_BREAK",
            "guidance": (
                "Take an immediate break. Minimum 2-hour cooling period. "
                "Review your pre-session checklist before returning."
            ),
            "breathing_exercise": "Box breathing (4-4-4-4)",
            "immediate_steps": [
                "Sit out current session",
                "Leave computer area",
                "Practice breathing exercise",
                "Journal about what triggered this",
            ],
        }
    elif severity >= 5:
        return {
            "action": "SLOW_DOWN",
            "guidance": (
                "Reduce your table count and stakes. "
                "Implement your in-session tilt protocol."
            ),
            "breathing_exercise": "5-5 breathing (5 in, 5 out)",
            "immediate_steps": [
                "Close half your tables",
                "Take 5-minute break",
                "Review A-game reminders",
                "Refocus on process goals",
            ],
        }
    else:
        return {
            "action": "CONTINUE_WITH_AWARENESS",
            "guidance": (
                "You're managing well. Stay aware of your emotional state. "
                "Stick to your game plan."
            ),
            "breathing_exercise": "Normal mindful breathing",
            "immediate_steps": [
                "Note what you're feeling",
                "Recommit to your strategy",
                "Take break every hour",
                "Stay hydrated",
            ],
        }
