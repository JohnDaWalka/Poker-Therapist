"""Hybrid database layer supporting both SQLite and Firestore."""

import os
from typing import Any, Dict, List, Optional

from backend.agent.memory.firestore_adapter import firestore_adapter


class HybridMemoryStore:
    """Hybrid memory store that uses both SQLite and Firestore.
    
    This allows the application to:
    - Use SQLite for local development
    - Use Firestore for production deployment on GCP/Vercel
    - Maintain compatibility with existing code
    """
    
    def __init__(self):
        """Initialize hybrid memory store."""
        self.use_firestore = bool(os.getenv("GCP_PROJECT_ID"))
        self.use_sqlite = True  # Always keep SQLite as fallback
    
    async def save_session(
        self, 
        session_data: Dict[str, Any],
        db_session=None
    ) -> str:
        """Save session to both SQLite and Firestore.
        
        Args:
            session_data: Session data dictionary
            db_session: SQLite database session (optional)
            
        Returns:
            Session ID
        """
        session_id = session_data.get("session_id", "")
        
        # Save to Firestore if enabled
        if self.use_firestore:
            firestore_id = await firestore_adapter.save_session(session_data)
            if not session_id:
                session_id = firestore_id
        
        # Save to SQLite if db_session provided
        if self.use_sqlite and db_session:
            from backend.agent.memory.database import Session
            
            db_record = Session(
                session_id=session_id,
                user_id=session_data.get("user_id"),
                session_type=session_data.get("session_type"),
                start_time=session_data.get("start_time"),
                end_time=session_data.get("end_time"),
                emotion=session_data.get("emotion"),
                intensity=session_data.get("intensity"),
                body_sensation=session_data.get("body_sensation"),
                still_playing=session_data.get("still_playing"),
                severity=session_data.get("severity"),
                patterns_detected=session_data.get("patterns_detected"),
                ai_guidance=session_data.get("ai_guidance"),
                action_plan=session_data.get("action_plan"),
            )
            db_session.add(db_record)
            await db_session.commit()
        
        return session_id
    
    async def get_user_sessions(
        self, 
        user_id: str, 
        limit: int = 10,
        db_session=None
    ) -> List[Dict[str, Any]]:
        """Get user sessions from Firestore or SQLite.
        
        Args:
            user_id: User identifier
            limit: Maximum number of sessions
            db_session: SQLite database session (optional)
            
        Returns:
            List of session data
        """
        # Try Firestore first if enabled
        if self.use_firestore:
            sessions = await firestore_adapter.get_user_sessions(user_id, limit)
            if sessions:
                return sessions
        
        # Fallback to SQLite
        if self.use_sqlite and db_session:
            from backend.agent.memory.database import Session
            from sqlalchemy import select
            
            stmt = (
                select(Session)
                .where(Session.user_id == user_id)
                .order_by(Session.created_at.desc())
                .limit(limit)
            )
            result = await db_session.execute(stmt)
            sessions = result.scalars().all()
            
            return [
                {
                    "session_id": s.session_id,
                    "user_id": s.user_id,
                    "session_type": s.session_type,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "emotion": s.emotion,
                    "intensity": s.intensity,
                    "severity": s.severity,
                }
                for s in sessions
            ]
        
        return []
    
    async def save_message(
        self,
        user_id: str,
        role: str,
        content: str,
        session_id: Optional[str] = None
    ) -> str:
        """Save message to Firestore.
        
        Args:
            user_id: User identifier
            role: Message role
            content: Message content
            session_id: Optional session ID
            
        Returns:
            Message ID
        """
        if self.use_firestore:
            return await firestore_adapter.save_message(user_id, role, content, session_id)
        return ""
    
    async def get_user_messages(
        self,
        user_id: str,
        limit: int = 50,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get user messages from Firestore.
        
        Args:
            user_id: User identifier
            limit: Maximum number of messages
            session_id: Optional session ID filter
            
        Returns:
            List of message data
        """
        if self.use_firestore:
            return await firestore_adapter.get_user_messages(user_id, limit, session_id)
        return []
    
    async def save_tilt_profile(
        self,
        user_id: str,
        profile_data: Dict[str, Any],
        db_session=None
    ) -> None:
        """Save tilt profile to both stores.
        
        Args:
            user_id: User identifier
            profile_data: Tilt profile data
            db_session: SQLite database session (optional)
        """
        # Save to Firestore
        if self.use_firestore:
            await firestore_adapter.save_tilt_profile(user_id, profile_data)
        
        # Save to SQLite
        if self.use_sqlite and db_session:
            from backend.agent.memory.database import TiltProfile
            from sqlalchemy import select
            
            # Check if profile exists
            stmt = select(TiltProfile).where(TiltProfile.user_id == user_id)
            result = await db_session.execute(stmt)
            profile = result.scalar_one_or_none()
            
            if profile:
                # Update existing
                profile.a_game_characteristics = profile_data.get("a_game_characteristics")
                profile.red_flags = profile_data.get("red_flags")
                profile.recurring_patterns = profile_data.get("recurring_patterns")
            else:
                # Create new
                profile = TiltProfile(
                    user_id=user_id,
                    a_game_characteristics=profile_data.get("a_game_characteristics"),
                    red_flags=profile_data.get("red_flags"),
                    recurring_patterns=profile_data.get("recurring_patterns"),
                )
                db_session.add(profile)
            
            await db_session.commit()
    
    async def get_tilt_profile(
        self,
        user_id: str,
        db_session=None
    ) -> Optional[Dict[str, Any]]:
        """Get tilt profile from Firestore or SQLite.
        
        Args:
            user_id: User identifier
            db_session: SQLite database session (optional)
            
        Returns:
            Tilt profile data or None
        """
        # Try Firestore first
        if self.use_firestore:
            profile = await firestore_adapter.get_tilt_profile(user_id)
            if profile:
                return profile
        
        # Fallback to SQLite
        if self.use_sqlite and db_session:
            from backend.agent.memory.database import TiltProfile
            from sqlalchemy import select
            
            stmt = select(TiltProfile).where(TiltProfile.user_id == user_id)
            result = await db_session.execute(stmt)
            profile = result.scalar_one_or_none()
            
            if profile:
                return {
                    "a_game_characteristics": profile.a_game_characteristics,
                    "red_flags": profile.red_flags,
                    "recurring_patterns": profile.recurring_patterns,
                }
        
        return None


# Global hybrid memory store instance
hybrid_memory = HybridMemoryStore()
