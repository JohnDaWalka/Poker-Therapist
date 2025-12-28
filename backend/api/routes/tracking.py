"""Profile and playbook endpoints."""

from datetime import datetime

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from backend.agent.memory.database import Playbook as PlaybookModel
from backend.agent.memory.database import TiltProfile as TiltProfileModel
from backend.agent.memory.db_session import get_db
from backend.api.models import Playbook, TiltProfile

router = APIRouter()


@router.get("/profile/{user_id}", response_model=TiltProfile)
async def get_profile(user_id: str) -> TiltProfile:
    """Get user tilt profile.
    
    Args:
        user_id: User ID
        
    Returns:
        Tilt profile
    """
    try:
        async with get_db() as db:
            result = await db.execute(
                select(TiltProfileModel).where(TiltProfileModel.user_id == user_id)
            )
            profile = result.scalar_one_or_none()
            
            if not profile:
                # Create default profile
                profile = TiltProfileModel(
                    user_id=user_id,
                    a_game_characteristics={
                        "patient": True,
                        "focused": True,
                        "confident": True,
                    },
                    red_flags=["Anger", "Revenge thoughts", "Chasing losses"],
                    recurring_patterns=["Variance tilt", "Mistake tilt"],
                )
                db.add(profile)
                await db.commit()
                await db.refresh(profile)
            
            return TiltProfile(
                user_id=profile.user_id,
                a_game_characteristics=profile.a_game_characteristics or {},
                red_flags=profile.red_flags or [],
                recurring_patterns=profile.recurring_patterns or [],
                created_at=profile.created_at,
                updated_at=profile.updated_at,
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/playbook/{user_id}", response_model=Playbook)
async def get_playbook(user_id: str) -> Playbook:
    """Get user mental game playbook.
    
    Args:
        user_id: User ID
        
    Returns:
        Playbook
    """
    try:
        async with get_db() as db:
            result = await db.execute(
                select(PlaybookModel).where(PlaybookModel.user_id == user_id)
            )
            playbook = result.scalar_one_or_none()
            
            if not playbook:
                # Create default playbook
                playbook = PlaybookModel(
                    user_id=user_id,
                    pre_session_script="I am calm, focused, and ready to play my A-game.",
                    warmup_routine=["5 min meditation", "Review A-game checklist"],
                    in_session_protocol=["Take break every 90 min", "Stop at stop-loss"],
                    post_session_template="What went well? What to improve?",
                    personal_rules=["Never play tilted", "Always stick to bankroll"],
                )
                db.add(playbook)
                await db.commit()
                await db.refresh(playbook)
            
            return Playbook(
                user_id=playbook.user_id,
                pre_session_script=playbook.pre_session_script or "",
                warmup_routine=playbook.warmup_routine or [],
                in_session_protocol=playbook.in_session_protocol or [],
                post_session_template=playbook.post_session_template or "",
                personal_rules=playbook.personal_rules or [],
                created_at=playbook.created_at,
                updated_at=playbook.updated_at,
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
