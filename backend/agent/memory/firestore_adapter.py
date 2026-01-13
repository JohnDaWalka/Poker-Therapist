"""Firestore database adapter for persistent memory."""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from google.cloud import firestore

from backend.agent.memory.gcp_config import gcp_config


class FirestoreAdapter:
    """Adapter for Firestore database operations."""
    
    def __init__(self):
        """Initialize Firestore adapter."""
        self.enabled = bool(os.getenv("GCP_PROJECT_ID"))
        self._client: Optional[firestore.AsyncClient] = None
    
    @property
    def client(self) -> firestore.AsyncClient:
        """Get Firestore client.
        
        Returns:
            Firestore async client
        """
        if self._client is None:
            self._client = gcp_config.get_firestore_client()
        return self._client
    
    async def create_user(self, user_id: str, email: str) -> Dict[str, Any]:
        """Create a user in Firestore.
        
        Args:
            user_id: Unique user identifier
            email: User email address
            
        Returns:
            User document data
        """
        if not self.enabled:
            return {}
        
        user_ref = self.client.collection("users").document(user_id)
        user_data = {
            "email": email,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
        await user_ref.set(user_data)
        return user_data
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user from Firestore.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            User document data or None
        """
        if not self.enabled:
            return None
        
        user_ref = self.client.collection("users").document(user_id)
        doc = await user_ref.get()
        return doc.to_dict() if doc.exists else None
    
    async def save_session(self, session_data: Dict[str, Any]) -> str:
        """Save therapy session to Firestore.
        
        Args:
            session_data: Session data dictionary
            
        Returns:
            Session document ID
        """
        if not self.enabled:
            return ""
        
        session_data["created_at"] = firestore.SERVER_TIMESTAMP
        doc_ref = await self.client.collection("sessions").add(session_data)
        # doc_ref is a tuple: (WriteResult, DocumentReference)
        return doc_ref[1].id
    
    async def get_user_sessions(
        self, 
        user_id: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get user's therapy sessions from Firestore.
        
        Args:
            user_id: Unique user identifier
            limit: Maximum number of sessions to retrieve
            
        Returns:
            List of session documents
        """
        if not self.enabled:
            return []
        
        sessions_ref = (
            self.client.collection("sessions")
            .where("user_id", "==", user_id)
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        
        docs = await sessions_ref.get()
        return [doc.to_dict() for doc in docs]
    
    async def save_tilt_profile(
        self, 
        user_id: str, 
        profile_data: Dict[str, Any]
    ) -> None:
        """Save tilt profile to Firestore.
        
        Args:
            user_id: Unique user identifier
            profile_data: Tilt profile data
        """
        if not self.enabled:
            return
        
        profile_ref = self.client.collection("tilt_profiles").document(user_id)
        profile_data["updated_at"] = firestore.SERVER_TIMESTAMP
        await profile_ref.set(profile_data, merge=True)
    
    async def get_tilt_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get tilt profile from Firestore.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Tilt profile data or None
        """
        if not self.enabled:
            return None
        
        profile_ref = self.client.collection("tilt_profiles").document(user_id)
        doc = await profile_ref.get()
        return doc.to_dict() if doc.exists else None
    
    async def save_playbook(
        self, 
        user_id: str, 
        playbook_data: Dict[str, Any]
    ) -> None:
        """Save mental game playbook to Firestore.
        
        Args:
            user_id: Unique user identifier
            playbook_data: Playbook data
        """
        if not self.enabled:
            return
        
        playbook_ref = self.client.collection("playbooks").document(user_id)
        playbook_data["updated_at"] = firestore.SERVER_TIMESTAMP
        await playbook_ref.set(playbook_data, merge=True)
    
    async def get_playbook(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get mental game playbook from Firestore.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Playbook data or None
        """
        if not self.enabled:
            return None
        
        playbook_ref = self.client.collection("playbooks").document(user_id)
        doc = await playbook_ref.get()
        return doc.to_dict() if doc.exists else None
    
    async def save_message(
        self, 
        user_id: str, 
        role: str, 
        content: str,
        session_id: Optional[str] = None
    ) -> str:
        """Save chat message to Firestore.
        
        Args:
            user_id: Unique user identifier
            role: Message role (user, assistant, system)
            content: Message content
            session_id: Optional session ID
            
        Returns:
            Message document ID
        """
        if not self.enabled:
            return ""
        
        message_data = {
            "user_id": user_id,
            "role": role,
            "content": content,
            "session_id": session_id,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        doc_ref = await self.client.collection("messages").add(message_data)
        return doc_ref[1].id
    
    async def get_user_messages(
        self, 
        user_id: str, 
        limit: int = 50,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get user's chat messages from Firestore.
        
        Args:
            user_id: Unique user identifier
            limit: Maximum number of messages to retrieve
            session_id: Optional session ID filter
            
        Returns:
            List of message documents
        """
        if not self.enabled:
            return []
        
        query = self.client.collection("messages").where("user_id", "==", user_id)
        
        if session_id:
            query = query.where("session_id", "==", session_id)
        
        query = query.order_by("created_at").limit(limit)
        
        docs = await query.get()
        return [doc.to_dict() for doc in docs]
    
    async def save_hand_history(
        self, 
        hand_data: Dict[str, Any]
    ) -> str:
        """Save hand history to Firestore.
        
        Args:
            hand_data: Hand history data
            
        Returns:
            Hand history document ID
        """
        if not self.enabled:
            return ""
        
        hand_data["created_at"] = firestore.SERVER_TIMESTAMP
        doc_ref = await self.client.collection("hand_histories").add(hand_data)
        return doc_ref[1].id
    
    async def get_user_hands(
        self, 
        user_id: str,
        session_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get user's hand histories from Firestore.
        
        Args:
            user_id: Unique user identifier
            session_id: Optional session ID filter
            limit: Maximum number of hands to retrieve
            
        Returns:
            List of hand history documents
        """
        if not self.enabled:
            return []
        
        query = self.client.collection("hand_histories").where("user_id", "==", user_id)
        
        if session_id:
            query = query.where("session_id", "==", session_id)
        
        query = query.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
        
        docs = await query.get()
        return [doc.to_dict() for doc in docs]


# Global Firestore adapter instance
firestore_adapter = FirestoreAdapter()
