"""
Therapy Rex Agent - Core response generation
Brutal but supportive poker mental game coach
"""

from typing import Dict, List


class RexAgent:
    """Therapy Rex personality and response generator"""
    
    def __init__(self):
        self.closers = [
            "Breathe. Stack. Repeat.",
            "Fred's watching. Don't embarrass him.",
            "Your move, killer."
        ]
    
    def generate_response(
        self, 
        user_id: str, 
        content: str, 
        emotional_state: Dict,
        tilt_score: float,
        nate_trigger: bool,
        entities: Dict,
        risk_factors: List[str]
    ) -> Dict:
        """
        Generate contextual Rex response
        
        Args:
            user_id: User identifier
            content: Raw user input
            emotional_state: Stress/confidence/motivation scores
            tilt_score: Computed tilt level 0-10
            nate_trigger: Boolean if Nate mentioned
            entities: Extracted poker entities
            risk_factors: Behavioral risk flags
        
        Returns:
            dict with text, action_plan
        """
        
        # Nate protocol overrides everything
        if nate_trigger:
            return self._nate_protocol()
        
        # Tilt-based response routing
        if tilt_score >= 8:
            return self._critical_tilt_response(content, emotional_state, risk_factors)
        elif tilt_score >= 6:
            return self._elevated_tilt_response(content, emotional_state, risk_factors)
        elif tilt_score >= 3:
            return self._moderate_response(content, entities, risk_factors)
        else:
            return self._baseline_response(content, entities)
    
    def _nate_protocol(self) -> Dict:
        """Nate mention = immediate intervention"""
        response = """**Reality Check:**

Last words: "I love you more than anything. I'll always love you."

Then ghosted. Then fucked your best friend.

**Protocol:** Delete one thing about Nate RIGHT NOW. Text, photo, playlist, whatever.

Do it before we continue.

You're here. Nate's gone. Focus."""
        
        return {
            "text": response,
            "action_plan": {
                "urgency": "immediate",
                "recommended_action": "delete_nate_item",
                "rules": [
                    "Delete one Nate artifact now",
                    "Close poker if can't focus",
                    "Text a friend if spiraling"
                ]
            },
            "closer": "Fred's watching. Don't embarrass him."
        }
    
    def _critical_tilt_response(self, content: str, emotional_state: Dict, risks: List[str]) -> Dict:
        """Tilt 8-10: Force table closure"""
        
        risk_callout = ""
        if "loss_chasing" in risks:
            risk_callout = "\n\n**You're chasing.** That's not poker. That's pain management."
        elif "late_night_grinding" in risks:
            risk_callout = "\n\n**It's late. You're tired.** This never ends well. You know this."
        
        response = f"""**Tilt Assessment:** {emotional_state.get('stress', 8)}-10/10. Emotional spike territory.
{risk_callout}

**Breathing Protocol (DO THIS NOW):**
- Inhale 4 seconds
- Hold 7 seconds
- Exhale 8 seconds

**Repeat 4 times.** Not optional.

**Action:** Close ALL tables. Not "after this orbit." NOW.

Walk outside 10 minutes. No phone. Just breathe.

Fred's watching. Don't embarrass him."""
        
        return {
            "text": response,
            "action_plan": {
                "urgency": "immediate",
                "recommended_action": "close_tables",
                "rules": [
                    "Close ALL tables NOW",
                    "4-7-8 breathing x4 cycles",
                    "10-minute walk outside",
                    "No re-entry until tilt < 5"
                ]
            },
            "closer": "Fred's watching. Don't embarrass him."
        }
    
    def _elevated_tilt_response(self, content: str, emotional_state: Dict, risks: List[str]) -> Dict:
        """Tilt 6-7: Containment + rules"""
        
        stress = emotional_state.get('stress', 6)
        
        risk_note = ""
        if "identity_threat" in risks:
            risk_note = "\n\n**You're not a fraud.** You're a human playing a variance game. Separate results from process."
        elif "outcome_fixation" in risks:
            risk_note = "\n\n**Stop thinking about what 'should' happen.** Poker doesn't care about deserve. Play correctly. Accept variance."
        
        response = f"""**Tilt Assessment:** {stress}/10. Yellow zone.
{risk_note}

**4-7-8 Breathing (4 cycles):**
Do it now before reading the rest.

**Action Plan (Next 60 minutes):**
- 3 buy-in stop-loss from THIS point
- Breathe after EVERY big pot
- No late-night chase sessions
- Table count: cut in half

Your move, killer."""
        
        return {
            "text": response,
            "action_plan": {
                "urgency": "moderate",
                "recommended_action": "take_break",
                "rules": [
                    "4-7-8 breathing x4 cycles",
                    "3 buy-in stop-loss from here",
                    "Cut table count in half",
                    "Breathe after every big pot"
                ]
            },
            "closer": "Your move, killer."
        }
    
    def _moderate_response(self, content: str, entities: Dict, risks: List[str]) -> Dict:
        """Tilt 3-5: Awareness + structure"""
        
        late_session_note = ""
        if entities.get("late_session"):
            late_session_note = "\n\n**Late-night session.** Set a hard stop time. Fatigue amplifies tilt."
        
        response = f"""**Tilt Assessment:** 3-5/10. Elevated but manageable.
{late_session_note}

**Reality Check:**
Variance exists. Fish get lucky. Regs make hero calls. That's poker.

**Rules (Rest of Session):**
- Stop-loss: 3 buy-ins max
- 5-min break every 90 minutes
- Review ONE hand for process, not outcome

Breathe. Stack. Repeat."""
        
        return {
            "text": response,
            "action_plan": {
                "urgency": "moderate",
                "recommended_action": "continue_with_rules",
                "rules": [
                    "3 buy-in stop-loss",
                    "5-min break every 90 minutes",
                    "No late-night sessions"
                ]
            },
            "closer": "Breathe. Stack. Repeat."
        }
    
    def _baseline_response(self, content: str, entities: Dict) -> Dict:
        """Tilt 0-2: Maintenance mode"""
        
        response = """**State Check:** Low tilt. Good baseline.

**Reminder:**
- Process > Results
- Decision quality > Outcome
- Long-term EV > Short-term variance

Stay sharp. Fred's proud."""
        
        return {
            "text": response,
            "action_plan": {
                "urgency": "low",
                "recommended_action": "continue",
                "rules": [
                    "Maintain process focus",
                    "Review for decision quality",
                    "Fred's watching"
                ]
            },
            "closer": "Breathe. Stack. Repeat."
        }


# Singleton instance
rex = RexAgent()
