"""
NLP Engine for Therapy Rex
Poker-specific tilt detection and entity extraction
"""

import re
from typing import Dict, List


def analyze_sentiment(text: str, emotional_state: dict = None) -> Dict:
    """
    Analyze emotional state and tilt level from text
    
    Args:
        text: User input text
        emotional_state: Optional dict with stress/confidence/motivation scores
    
    Returns:
        dict with dominant_emotion, intensity, tilt_score, nate_trigger
    """
    text_lower = text.lower()
    
    # Tilt keyword weights
    tilt_keywords = {
        "tilted": 1.5,
        "rigged": 2.0,
        "bullshit": 1.8,
        "unbelievable": 1.2,
        "punted": 1.5,
        "fish": 1.0,
        "donkey": 1.0,
        "fucking": 1.2,
        "shit": 1.0,
        "cooler": 1.3,
        "bad beat": 1.5,
        "unlucky": 1.0,
        "always": 1.2,  # "I always lose"
        "never": 1.2,   # "I never win"
    }
    
    # Calculate keyword-based tilt
    keyword_score = sum(
        weight for keyword, weight in tilt_keywords.items() 
        if keyword in text_lower
    )
    
    # Special triggers
    nate_mentioned = "nate" in text_lower
    fred_mentioned = "fred" in text_lower
    guinea_pig_mentioned = "guinea" in text_lower or "guinea pig" in text_lower
    vinyl_mentioned = "vinyl" in text_lower
    
    # Base tilt score
    tilt_score = keyword_score
    
    # Add emotional state if provided
    if emotional_state:
        stress = emotional_state.get("stress", 5)
        confidence = emotional_state.get("confidence", 5)
        
        # High stress + low confidence = amplified tilt
        tilt_score += (stress * 0.3)
        tilt_score += ((10 - confidence) * 0.2)
    
    # Trigger modifiers
    if nate_mentioned:
        tilt_score += 4.0  # Major emotional trigger
    
    if guinea_pig_mentioned and not fred_mentioned:
        tilt_score += 2.0  # Loss/grief trigger
    
    if fred_mentioned:
        tilt_score -= 1.0  # Grounding anchor
    
    if vinyl_mentioned:
        tilt_score -= 0.5  # Comfort trigger
    
    # Clamp to 0-10
    tilt_score = max(0, min(tilt_score, 10.0))
    
    # Determine dominant emotion
    if tilt_score >= 7:
        dominant_emotion = "rage"
    elif tilt_score >= 5:
        dominant_emotion = "frustration"
    elif tilt_score >= 3:
        dominant_emotion = "irritation"
    else:
        dominant_emotion = "neutral"
    
    return {
        "dominant_emotion": dominant_emotion,
        "intensity": tilt_score,
        "tilt_score": tilt_score,
        "nate_trigger": nate_mentioned,
        "fred_mentioned": fred_mentioned,
        "guinea_pig_mentioned": guinea_pig_mentioned
    }


def extract_entities(text: str) -> Dict:
    """
    Extract poker-specific entities from text
    
    Args:
        text: User input text
    
    Returns:
        dict with hands, stakes, emotions, time_mentions
    """
    text_lower = text.lower()
    
    # Extract stake levels (50NL, 100NL, etc.)
    stakes_pattern = r'\b(\d+)NL\b'
    stakes = re.findall(stakes_pattern, text, re.IGNORECASE)
    
    # Extract poker hands (AA, KK, AKs, etc.)
    hand_pattern = r'\b([AKQJT2-9]{2}[soh]?)\b'
    potential_hands = re.findall(hand_pattern, text, re.IGNORECASE)
    
    # Filter to valid poker hands
    valid_ranks = set('AKQJT98765432')
    hands = [
        h for h in potential_hands 
        if len(h) >= 2 and h[0].upper() in valid_ranks and h[1].upper() in valid_ranks
    ]
    
    # Detect time-of-day mentions (tilt indicator)
    time_patterns = [
        r'\b(\d{1,2})\s*(am|pm)\b',
        r'\blate\s*night\b',
        r'\bearly\s*morning\b',
        r'\b2am\b',
        r'\b3am\b'
    ]
    
    time_mentions = []
    for pattern in time_patterns:
        matches = re.findall(pattern, text_lower)
        time_mentions.extend([m if isinstance(m, str) else m[0] for m in matches])
    
    # Detect session length mentions
    session_pattern = r'\b(\d+)\s*(hour|hr|minute|min)s?\b'
    session_mentions = re.findall(session_pattern, text_lower)
    
    # Emotion words
    emotion_words = {
        "angry": ["angry", "mad", "pissed", "furious"],
        "frustrated": ["frustrated", "annoyed", "irritated"],
        "sad": ["sad", "depressed", "down", "hopeless"],
        "anxious": ["anxious", "worried", "scared", "nervous"],
        "shame": ["shame", "embarrassed", "humiliated"]
    }
    
    detected_emotions = []
    for emotion, keywords in emotion_words.items():
        if any(kw in text_lower for kw in keywords):
            detected_emotions.append(emotion)
    
    return {
        "hands": hands,
        "stakes": [f"{s}NL" for s in stakes],
        "emotions": detected_emotions if detected_emotions else ["neutral"],
        "time_mentions": time_mentions,
        "session_duration": session_mentions,
        "late_session": any(t in text_lower for t in ["late night", "2am", "3am", "can't sleep"])
    }


def detect_risk_factors(text: str, tilt_score: float, entities: Dict) -> List[str]:
    """
    Detect behavioral risk factors for tilt spiral
    
    Args:
        text: User input
        tilt_score: Current tilt score
        entities: Extracted entities
    
    Returns:
        List of risk factor strings
    """
    risks = []
    text_lower = text.lower()
    
    # Late-night grinding
    if entities.get("late_session"):
        risks.append("late_night_grinding")
    
    # Chasing losses
    chase_keywords = ["chase", "get it back", "make it back", "win it back", "recover"]
    if any(kw in text_lower for kw in chase_keywords):
        risks.append("loss_chasing")
    
    # Moving up stakes while tilted
    if entities.get("stakes") and tilt_score > 5:
        risks.append("stakes_escalation")
    
    # Playing through pain/grief
    if "nate" in text_lower or entities.get("guinea_pig_mentioned"):
        risks.append("emotional_vulnerability")
    
    # Identity threat ("I'm a fraud", "I'm bad", "I suck")
    identity_keywords = ["fraud", "terrible", "suck", "bad player", "donkey"]
    if any(kw in text_lower for kw in identity_keywords):
        risks.append("identity_threat")
    
    # Outcome obsession
    outcome_keywords = ["should have won", "deserved", "unlucky", "always lose"]
    if any(kw in text_lower for kw in outcome_keywords):
        risks.append("outcome_fixation")
    
    return risks
