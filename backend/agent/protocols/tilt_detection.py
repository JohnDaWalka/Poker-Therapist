"""Tilt detection and pattern recognition."""

from typing import Any, Dict, List


def detect_tilt_patterns(context: Dict[str, Any]) -> Dict[str, Any]:
    """Detect tilt patterns from user input.
    
    Args:
        context: Session context with situation, emotion, etc.
        
    Returns:
        Detected patterns dict
    """
    situation = context.get("situation", "").lower()
    emotion = context.get("emotion", "").lower()
    intensity = context.get("intensity", 0)
    
    patterns: List[str] = []
    
    # Check for specific tilt types
    if "bad beat" in situation or "cooler" in situation:
        patterns.append("variance_tilt")
    
    if "mistake" in situation or "misplayed" in situation or "should have" in situation:
        patterns.append("mistake_tilt")
    
    if "donkey" in situation or "idiot" in situation or "fish" in situation:
        patterns.append("justice_tilt")
    
    if "revenge" in situation or "get them back" in situation:
        patterns.append("revenge_tilt")
    
    if "bored" in situation or emotion == "boredom":
        patterns.append("boredom_tilt")
    
    if "entitled" in situation or emotion == "entitlement":
        patterns.append("entitlement_tilt")
    
    if "losing streak" in situation or "downswing" in situation:
        patterns.append("downswing_tilt")
    
    # Determine primary trigger
    primary_trigger = patterns[0] if patterns else "general_frustration"
    
    return {
        "patterns": patterns,
        "primary_trigger": primary_trigger,
        "intensity_level": _categorize_intensity(intensity),
        "recommendations": _get_pattern_recommendations(primary_trigger),
    }


def _categorize_intensity(intensity: int) -> str:
    """Categorize intensity level.
    
    Args:
        intensity: Intensity rating 1-10
        
    Returns:
        Category string
    """
    if intensity >= 8:
        return "severe"
    elif intensity >= 6:
        return "high"
    elif intensity >= 4:
        return "moderate"
    else:
        return "mild"


def _get_pattern_recommendations(pattern: str) -> List[str]:
    """Get recommendations for specific tilt pattern.
    
    Args:
        pattern: Tilt pattern type
        
    Returns:
        List of recommendations
    """
    recommendations_map = {
        "variance_tilt": [
            "Remember: variance is expected and normal",
            "Focus on decision quality, not results",
            "Review your equity calculations",
            "Take pride in getting your money in good",
        ],
        "mistake_tilt": [
            "Mistakes are learning opportunities",
            "Note the mistake for future study",
            "Self-compassion: everyone makes mistakes",
            "Refocus on next decision, not last one",
        ],
        "justice_tilt": [
            "Bad players = profit in long run",
            "Thank them for their mistakes",
            "Your job is to exploit, not judge",
            "Their play style creates your edge",
        ],
        "revenge_tilt": [
            "Revenge is -EV thinking",
            "Play optimal, not emotional",
            "Their chips are worth same as anyone's",
            "Focus on exploitable patterns, not payback",
        ],
        "boredom_tilt": [
            "Boredom ≠ need to force action",
            "Tight play is winning play",
            "Quality over quantity of hands",
            "Consider taking break if truly bored",
        ],
        "entitlement_tilt": [
            "You're not owed winning sessions",
            "Expectations create suffering",
            "Process goals > outcome goals",
            "Focus on what you can control",
        ],
        "downswing_tilt": [
            "Downswings are statistically normal",
            "Review your game honestly",
            "Consider moving down in stakes",
            "Volume will reveal true results",
        ],
        "general_frustration": [
            "Acknowledge your feelings",
            "Return to fundamentals",
            "Take strategic break if needed",
            "Review your mental game plan",
        ],
    }
    
    return recommendations_map.get(pattern, recommendations_map["general_frustration"])


def assess_recurring_themes(
    user_history: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Assess recurring themes across sessions.
    
    Args:
        user_history: List of previous session dicts
        
    Returns:
        Recurring themes analysis
    """
    if not user_history:
        return {"themes": [], "frequency": {}}
    
    # Count pattern occurrences
    pattern_counts: Dict[str, int] = {}
    emotion_counts: Dict[str, int] = {}
    
    for session in user_history:
        patterns = session.get("patterns", [])
        for pattern in patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        emotion = session.get("emotion", "")
        if emotion:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    # Identify recurring themes (appears in >30% of sessions)
    threshold = len(user_history) * 0.3
    recurring_patterns = [
        pattern for pattern, count in pattern_counts.items() if count >= threshold
    ]
    
    return {
        "recurring_patterns": recurring_patterns,
        "dominant_emotions": sorted(
            emotion_counts.items(), key=lambda x: x[1], reverse=True
        )[:3],
        "total_sessions": len(user_history),
        "needs_deeper_work": len(recurring_patterns) > 2,
    }
