"""Triage endpoint."""

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from backend.agent.ai_orchestrator import AIOrchestrator
from backend.agent.memory.database import Session as SessionModel
from backend.agent.memory.db_session import get_db
from backend.agent.session_types.tilt_triage import TiltTriageSession
from backend.api.models import TriageRequest, TriageResponse

router = APIRouter()
orchestrator = AIOrchestrator()
triage_handler = TiltTriageSession(orchestrator)


@router.post("/triage", response_model=TriageResponse)
async def triage(request: TriageRequest) -> TriageResponse:
    """Quick tilt intervention endpoint.
    
    Args:
        request: Triage request
        
    Returns:
        Triage response
    """
    try:
        # Conduct triage session
        context = {
            "situation": request.situation,
            "emotion": request.emotion,
            "intensity": request.intensity,
            "body_sensation": request.body_sensation,
            "still_playing": request.still_playing,
            "user_id": request.user_id,
        }
        
        result = await triage_handler.conduct(context)
        
        # Save session to database
        async with get_db() as db:
            session = SessionModel(
                session_id=str(uuid4()),
                user_id=request.user_id,
                session_type="triage",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                emotion=request.emotion,
                intensity=request.intensity,
                body_sensation=request.body_sensation,
                still_playing=request.still_playing,
                severity=result["severity"],
                patterns_detected=result["patterns_detected"],
                ai_guidance=result["ai_guidance"],
                action_plan=result["micro_plan"],
            )
            db.add(session)
            await db.commit()
        
        return TriageResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
