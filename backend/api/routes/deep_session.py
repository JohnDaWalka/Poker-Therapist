"""Deep session endpoint."""

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from backend.agent.ai_orchestrator import AIOrchestrator
from backend.agent.memory.database import Session as SessionModel
from backend.agent.memory.db_session import get_db
from backend.agent.session_types.deep_session import DeepTherapySession
from backend.api.models import DeepSessionRequest, DeepSessionResponse

router = APIRouter()
orchestrator = AIOrchestrator()
deep_handler = DeepTherapySession(orchestrator)


@router.post("/deep-session", response_model=DeepSessionResponse)
async def deep_session(request: DeepSessionRequest) -> DeepSessionResponse:
    """Deep therapy session endpoint.
    
    Args:
        request: Deep session request
        
    Returns:
        Deep session response
    """
    try:
        # Conduct deep therapy session
        context = {
            "emotional_state": request.emotional_state,
            "recent_results": request.recent_results,
            "life_context": request.life_context,
            "recurring_themes": request.recurring_themes,
            "user_id": request.user_id,
        }
        
        result = await deep_handler.conduct(context)
        
        # Save session to database
        async with get_db() as db:
            session = SessionModel(
                session_id=str(uuid4()),
                user_id=request.user_id,
                session_type="deep",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                ai_guidance=result["session_summary"],
                action_plan=result["action_plan"],
            )
            db.add(session)
            await db.commit()
        
        return DeepSessionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
