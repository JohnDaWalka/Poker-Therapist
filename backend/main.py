from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

app = FastAPI(title="Therapy Rex API", version="1.0.0", description="Multi-modal poker mental game coach")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class EmotionalState(BaseModel):
    stress: int = Field(ge=0, le=10)
    confidence: int = Field(ge=0, le=10)
    motivation: int = Field(ge=0, le=10)

class TextInputRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    content_type: str
    text: str
    emotional_state: EmotionalState
    context: dict
    timestamp: str

class ActionRequired(BaseModel):
    urgency: str
    recommended_action: str
    rules: list[str]

class TextInputResponse(BaseModel):
    response_id: str
    rex_response: str
    tilt_score: float
    action_required: ActionRequired
    entities_extracted: dict

# Core Logic
def analyze_tilt(text: str, emotional_state: EmotionalState) -> tuple[float, bool]:
    """Poker-specific tilt detection"""
    tilt_keywords = [
        "tilted", "rigged", "bullshit", "unbelievable", "punted", 
        "fish", "donkey", "fucking", "shit", "cooler", "bad beat"
    ]
    
    nate_mentioned = "nate" in text.lower()
    fred_mentioned = "fred" in text.lower()
    guinea_pig = "guinea pig" in text.lower() or "guinea" in text.lower()
    
    keyword_score = sum(1 for kw in tilt_keywords if kw in text.lower())
    
    # Base tilt from keywords
    tilt_score = keyword_score * 1.5
    
    # Emotional state weight
    tilt_score += emotional_state.stress * 0.5
    
    # Special triggers
    if nate_mentioned:
        tilt_score += 4  # Major trigger
    
    if guinea_pig and not fred_mentioned:
        tilt_score += 2  # Loss trigger
    
    return min(tilt_score, 10.0), nate_mentioned

def generate_rex_response(text: str, tilt_score: float, nate_trigger: bool, emotional_state: EmotionalState) -> str:
    """Generate Rex's brutal but supportive response"""
    
    if nate_trigger:
        return """**Reality Check:**
Last words: "I love you more than anything. I'll always love you."

Then ghosted. Then fucked your best friend.

**Protocol:** Delete one thing about Nate RIGHT NOW. Text, photo, playlist, whatever. Do it before we continue.

You're here. Nate's gone. Focus."""
    
    if tilt_score >= 8:
        return """**Tilt Assessment:** 8-10/10. You're in emotional-spike territory.

**Breathing Protocol (DO THIS NOW):**
- Inhale 4 seconds
- Hold 7 seconds  
- Exhale 8 seconds
**Repeat 4 times.** I'll wait.

**Action:** Close ALL tables. Not "after this hand." NOW.

Walk outside 10 minutes. No phone. Just breathe.

Fred's watching. Don't embarrass him."""
    
    if tilt_score >= 6:
        return f"""**Tilt Assessment:** {tilt_score:.1f}/10. Yellow zone.

**4-7-8 Breathing (4 cycles):**
Do it now before reading the rest.

**Action Plan (Next 60 minutes):**
- 3 buy-in stop-loss from THIS point
- Breathe after EVERY big pot
- No late-night chase sessions
- Table count: cut in half

Your move, killer."""
    
    if tilt_score >= 3:
        return f"""**Tilt Assessment:** {tilt_score:.1f}/10. Elevated but manageable.

**Reality Check:**
Variance exists. Fish get lucky. Regs make hero calls. That's poker.

**Rules (Next Session):**
- Stop-loss: 3 buy-ins max
- Take 5-min break every 90 minutes
- Review one hand for process, not outcome

Breathe. Stack. Repeat."""
    
    return """**State Check:** Low tilt. Good baseline.

**Reminder:** 
- Process > Results
- Decision quality > Outcome
- Long-term EV > Short-term variance

Stay sharp. Fred's proud.

Your move, killer."""

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "therapy-rex-api",
        "version": "1.0.0",
        "message": "Fred's watching."
    }

@app.post("/api/v1/therapy/text", response_model=TextInputResponse)
async def process_text_input(payload: TextInputRequest):
    """
    Process text input from user
    - Analyze tilt level
    - Generate Rex response
    - Provide action plan
    """
    try:
        # Analyze tilt
        tilt_score, nate_trigger = analyze_tilt(payload.text, payload.emotional_state)
        
        # Generate Rex response
        rex_response = generate_rex_response(
            payload.text, 
            tilt_score, 
            nate_trigger, 
            payload.emotional_state
        )
        
        # Determine action urgency
        if tilt_score >= 8:
            urgency = "immediate"
            action = "close_tables"
            rules = [
                "Close ALL tables NOW",
                "4-7-8 breathing x4 cycles",
                "10-minute walk outside",
                "No re-entry until tilt < 5"
            ]
        elif tilt_score >= 6:
            urgency = "moderate"
            action = "take_break"
            rules = [
                "4-7-8 breathing x4 cycles",
                "3 buy-in stop-loss from here",
                "Cut table count in half",
                "Breathe after every big pot"
            ]
        elif tilt_score >= 3:
            urgency = "moderate"
            action = "continue_with_rules"
            rules = [
                "3 buy-in stop-loss",
                "5-min break every 90 minutes",
                "No late-night sessions"
            ]
        else:
            urgency = "low"
            action = "continue"
            rules = [
                "Maintain process focus",
                "Review for decision quality",
                "Fred's watching"
            ]
        
        # Extract basic entities
        import re
        stakes_pattern = r'\b(\d+)NL\b'
        stakes = re.findall(stakes_pattern, payload.text, re.IGNORECASE)
        
        entities = {
            "stakes": [f"{s}NL" for s in stakes],
            "nate_mentioned": nate_trigger,
            "hands": [],
            "emotions": ["anger"] if tilt_score > 5 else ["neutral"]
        }
        
        return TextInputResponse(
            response_id=str(uuid.uuid4()),
            rex_response=rex_response,
            tilt_score=tilt_score,
            action_required=ActionRequired(
                urgency=urgency,
                recommended_action=action,
                rules=rules
            ),
            entities_extracted=entities
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Therapy Rex API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "text_input": "/api/v1/therapy/text"
        },
        "docs": "/docs"
    }
