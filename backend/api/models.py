"""Pydantic models for API requests and responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TriageRequest(BaseModel):
    """Triage request model."""

    situation: str = Field(..., description="Current situation description")
    emotion: str = Field(..., description="Primary emotion")
    intensity: int = Field(..., ge=1, le=10, description="Intensity level 1-10")
    body_sensation: str = Field(default="", description="Physical sensations")
    still_playing: bool = Field(default=False, description="Still playing poker")
    user_id: str = Field(..., description="User ID")


class TriageResponse(BaseModel):
    """Triage response model."""

    severity: int
    should_stop: bool
    patterns_detected: List[str]
    primary_trigger: str
    ai_guidance: str
    safety_guidance: str
    breathing_exercise: str
    micro_plan: List[str]
    emergency_contacts: List[Dict[str, str]]
    warning_message: str


class DeepSessionRequest(BaseModel):
    """Deep therapy session request."""

    emotional_state: Dict[str, int] = Field(
        ..., description="Emotional state dict (stress, confidence, motivation)"
    )
    recent_results: str = Field(..., description="Recent poker results and situations")
    life_context: str = Field(default="", description="Life context affecting game")
    recurring_themes: str = Field(default="", description="Recurring issues")
    user_id: str = Field(..., description="User ID")


class DeepSessionResponse(BaseModel):
    """Deep therapy session response."""

    session_summary: str
    cognitive_reframes: List[str]
    action_plan: List[Dict[str, str]]
    follow_up_themes: List[str]
    therapeutic_approach: str
    research_insights: Optional[str] = None
    citations: List[str] = []


class HandAnalysisRequest(BaseModel):
    """Hand analysis request."""

    hand_history: str = Field(..., description="Poker hand history text")
    emotional_context: str = Field(default="", description="Emotional context")
    image_data: Optional[bytes] = None
    user_id: str = Field(..., description="User ID")


class HandAnalysisResponse(BaseModel):
    """Hand analysis response."""

    gto_analysis: str
    meta_context: str
    hud_insights: Optional[str] = None
    learning_points: List[str]
    models: List[str]
    log_id: Optional[int] = None
    source: str = "PokerTracker"
    source_version: str = "4.18.16"


class HandHistoryLog(BaseModel):
    """Logged hand history entry."""

    id: int
    user_id: str
    source: str
    source_version: str
    hand_history: str
    emotional_context: str
    gto_analysis: str
    meta_context: str
    hud_insights: Optional[str] = None
    models: List[str] = Field(default_factory=list)
    created_at: datetime


class VoiceAnalysisRequest(BaseModel):
    """Voice analysis request."""

    audio_data: bytes = Field(..., description="Audio file data")
    mime_type: str = Field(default="audio/wav", description="Audio MIME type")
    user_id: str = Field(..., description="User ID")


class VoiceAnalysisResponse(BaseModel):
    """Voice analysis response."""

    transcript: str
    detected_emotions: List[str]
    tilt_triggers: List[str]
    therapeutic_response: str
    models: List[str]


class VideoAnalysisRequest(BaseModel):
    """Video analysis request."""

    video_data: bytes = Field(..., description="Video file data")
    mime_type: str = Field(default="video/mp4", description="Video MIME type")
    user_id: str = Field(..., description="User ID")


class VideoAnalysisResponse(BaseModel):
    """Video analysis response."""

    timeline: str
    body_language: List[str]
    tilt_moments: List[Dict[str, Any]]
    psychological_patterns: List[str]
    models: List[str]


class TiltProfile(BaseModel):
    """Tilt profile model."""

    user_id: str
    a_game_characteristics: Dict[str, Any]
    red_flags: List[str]
    recurring_patterns: List[str]
    created_at: datetime
    updated_at: datetime


class Playbook(BaseModel):
    """Playbook model."""

    user_id: str
    pre_session_script: str
    warmup_routine: List[str]
    in_session_protocol: List[str]
    post_session_template: str
    personal_rules: List[str]
    created_at: datetime
    updated_at: datetime
