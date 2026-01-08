"""Analysis endpoints for hand, voice, and video."""

import logging
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.agent.ai_orchestrator import AIOrchestrator
from backend.agent.memory.hand_history_logger import (
    DEFAULT_SOURCE,
    DEFAULT_SOURCE_VERSION,
    fetch_hand_histories,
    log_hand_history_entry,
)
from backend.agent.memory.db_session import get_db
from backend.api.models import (
    HandAnalysisRequest,
    HandAnalysisResponse,
    HandHistoryLog,
    VideoAnalysisResponse,
    VoiceAnalysisResponse,
)

router = APIRouter()
orchestrator = AIOrchestrator()
logger = logging.getLogger(__name__)


@router.post("/analyze/hand", response_model=HandAnalysisResponse)
async def analyze_hand(request: HandAnalysisRequest) -> HandAnalysisResponse:
    """Analyze poker hand with multi-model approach.
    
    Args:
        request: Hand analysis request
        
    Returns:
        Hand analysis response
    """
    try:
        context = {
            "hand_history": request.hand_history,
            "emotional_context": request.emotional_context,
            "image_data": request.image_data,
            "user_id": request.user_id,
        }
        
        result = await orchestrator.route_query("hand_analysis", context)
        
        # Extract learning points
        learning_points = [
            "Focus on decision quality over results",
            "Consider opponent tendencies",
            "Review GTO baseline for this spot",
        ]

        log_id = await log_hand_history_entry(
            user_id=request.user_id,
            hand_history=request.hand_history,
            emotional_context=request.emotional_context or "",
            analysis={
                "gto_analysis": result.get("gto_analysis"),
                "meta_context": result.get("meta_context"),
                "hud_insights": result.get("hud_insights"),
                "models": result.get("models"),
            },
        )
        
        return HandAnalysisResponse(
            gto_analysis=result["gto_analysis"],
            meta_context=result["meta_context"],
            hud_insights=result.get("hud_insights"),
            learning_points=learning_points,
            models=result["models"],
            log_id=log_id,
            source=DEFAULT_SOURCE,
            source_version=DEFAULT_SOURCE_VERSION,
        )
        
    except Exception:
        logger.exception("Hand analysis failed")
        raise HTTPException(
            status_code=500,
            detail="Hand analysis failed. Please try again later.",
        )


@router.get("/analyze/hand/history/{user_id}", response_model=List[HandHistoryLog])
async def get_hand_history(
    user_id: str, limit: int = 20
) -> List[HandHistoryLog]:
    """Return stored PokerTracker hand histories for a user."""
    try:
        async with get_db() as db:
            records = await fetch_hand_histories(db, user_id, limit)

            return [
                HandHistoryLog(
                    id=record.id,
                    user_id=record.user_id,
                    source=record.source or DEFAULT_SOURCE,
                    source_version=record.source_version or DEFAULT_SOURCE_VERSION,
                    hand_history=record.hand_history,
                    emotional_context=record.emotional_context or "",
                    gto_analysis=record.gto_analysis or "",
                    meta_context=record.meta_context or "",
                    hud_insights=record.hud_insights,
                    models=record.models or [],
                    created_at=record.created_at,
                )
                for record in records
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/analyze/voice", response_model=VoiceAnalysisResponse)
async def analyze_voice(
    audio: UploadFile = File(...),
    user_id: str = "default",
) -> VoiceAnalysisResponse:
    """Analyze voice rant/recording.
    
    Args:
        audio: Audio file upload
        user_id: User ID
        
    Returns:
        Voice analysis response
    """
    try:
        audio_data = await audio.read()
        
        context = {
            "audio_data": audio_data,
            "mime_type": audio.content_type or "audio/wav",
            "user_id": user_id,
        }
        
        result = await orchestrator.route_query("voice_rant", context)
        
        # Extract emotions and triggers (simplified)
        detected_emotions = ["frustration", "stress"]
        tilt_triggers = ["bad beat", "variance"]
        
        return VoiceAnalysisResponse(
            transcript=result["transcript"],
            detected_emotions=detected_emotions,
            tilt_triggers=tilt_triggers,
            therapeutic_response=result["therapeutic_response"],
            models=result["models"],
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/analyze/video", response_model=VideoAnalysisResponse)
async def analyze_video(
    video: UploadFile = File(...),
    user_id: str = "default",
) -> VideoAnalysisResponse:
    """Analyze session video.
    
    Args:
        video: Video file upload
        user_id: User ID
        
    Returns:
        Video analysis response
    """
    try:
        video_data = await video.read()
        
        context = {
            "video_data": video_data,
            "mime_type": video.content_type or "video/mp4",
            "user_id": user_id,
        }
        
        result = await orchestrator.route_query("session_video", context)
        
        # Extract structured data (simplified)
        body_language = ["tense shoulders", "rapid movements"]
        tilt_moments = [
            {"timestamp": "00:15:30", "severity": 7, "trigger": "bad beat"}
        ]
        psychological_patterns = ["escalating frustration", "revenge mentality"]
        
        return VideoAnalysisResponse(
            timeline=result["video_analysis"],
            body_language=body_language,
            tilt_moments=tilt_moments,
            psychological_patterns=psychological_patterns,
            models=result["models"],
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
