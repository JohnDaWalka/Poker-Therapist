"""n8n webhook integration routes.

This module provides webhook endpoints for n8n workflow automation.
The endpoints accept webhook payloads from n8n and integrate with the
Poker Therapist backend services.

Note: Full integration with AIOrchestrator and SessionManager requires
the complete backend dependencies to be available. The current implementation
provides webhook handlers that can be extended once dependencies are loaded.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Header, Request, status
from pydantic import BaseModel, Field


router = APIRouter()


class N8nWebhookPayload(BaseModel):
    """n8n webhook payload model."""
    
    event_type: str = Field(..., description="Type of event triggering the webhook")
    user_id: Optional[str] = Field(None, description="User identifier")
    email: Optional[str] = Field(None, description="User email")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")


class N8nResponse(BaseModel):
    """n8n webhook response model."""
    
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


@router.post("/webhooks/n8n", response_model=N8nResponse, tags=["n8n"])
async def n8n_webhook(
    payload: N8nWebhookPayload,
    request: Request,
    x_n8n_webhook_id: Optional[str] = Header(None),
) -> N8nResponse:
    """
    Receive webhooks from n8n workflows.
    
    Supports various event types:
    - poker_analysis: Analyze a poker hand or session
    - triage_session: Start a tilt triage session
    - deep_session: Start a deep therapy session
    - user_notification: Send notifications to users
    - custom: Custom workflow events
    
    Args:
        payload: Webhook payload from n8n
        request: FastAPI request object
        x_n8n_webhook_id: Optional n8n webhook ID header
        
    Returns:
        Response indicating success or failure
    """
    try:
        # Log webhook receipt
        print(f"Received n8n webhook: {payload.event_type}")
        if x_n8n_webhook_id:
            print(f"Webhook ID: {x_n8n_webhook_id}")
        
        # Handle different event types
        if payload.event_type == "poker_analysis":
            return await handle_poker_analysis(payload)
        elif payload.event_type == "triage_session":
            return await handle_triage_session(payload)
        elif payload.event_type == "deep_session":
            return await handle_deep_session(payload)
        elif payload.event_type == "user_notification":
            return await handle_user_notification(payload)
        elif payload.event_type == "custom":
            return await handle_custom_event(payload)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported event type: {payload.event_type}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )


async def handle_poker_analysis(payload: N8nWebhookPayload) -> N8nResponse:
    """Handle poker analysis webhook events."""
    hand_data = payload.data.get("hand_data", {})
    user_id = payload.user_id or "n8n_user"
    
    # TODO: Initialize AI orchestrator when dependencies are available
    # orchestrator = AIOrchestrator(user_id=user_id)
    # result = await orchestrator.analyze_hand(hand_data)
    
    # For now, return a mock response
    result = {
        "hand": hand_data,
        "recommendation": "Analysis functionality will be available when AI orchestrator is initialized",
        "status": "pending"
    }
    
    return N8nResponse(
        success=True,
        message="Poker hand analysis request received",
        data={"analysis": result}
    )


async def handle_triage_session(payload: N8nWebhookPayload) -> N8nResponse:
    """Handle triage session webhook events."""
    user_id = payload.user_id or "n8n_user"
    session_data = payload.data.get("session_data", {})
    
    # TODO: Initialize session manager when dependencies are available
    # session_manager = SessionManager()
    # session_id = await session_manager.create_session(...)
    
    # For now, return a mock response
    session_id = f"triage_session_{user_id}"
    
    return N8nResponse(
        success=True,
        message="Triage session request received",
        data={"session_id": session_id, "session_data": session_data}
    )


async def handle_deep_session(payload: N8nWebhookPayload) -> N8nResponse:
    """Handle deep session webhook events."""
    user_id = payload.user_id or "n8n_user"
    session_data = payload.data.get("session_data", {})
    
    # TODO: Initialize session manager when dependencies are available
    # session_manager = SessionManager()
    # session_id = await session_manager.create_session(...)
    
    # For now, return a mock response
    session_id = f"deep_session_{user_id}"
    
    return N8nResponse(
        success=True,
        message="Deep session request received",
        data={"session_id": session_id, "session_data": session_data}
    )


async def handle_user_notification(payload: N8nWebhookPayload) -> N8nResponse:
    """Handle user notification webhook events."""
    email = payload.email
    notification_data = payload.data.get("notification", {})
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required for user notifications"
        )
    
    # Process notification (log for now, could integrate with email service)
    message = notification_data.get("message", "No message provided")
    print(f"Notification for {email}: {message}")
    
    return N8nResponse(
        success=True,
        message="Notification processed successfully",
        data={"email": email, "notification": notification_data}
    )


async def handle_custom_event(payload: N8nWebhookPayload) -> N8nResponse:
    """Handle custom webhook events."""
    # Process custom events
    custom_data = payload.data
    
    return N8nResponse(
        success=True,
        message="Custom event processed successfully",
        data=custom_data
    )


@router.post("/webhooks/n8n/test", response_model=N8nResponse, tags=["n8n"])
async def test_n8n_webhook() -> N8nResponse:
    """
    Test endpoint for n8n webhook integration.
    
    Use this to verify your n8n workflow can reach the API.
    
    Returns:
        Success response
    """
    from datetime import datetime
    
    return N8nResponse(
        success=True,
        message="n8n webhook integration is working",
        data={"timestamp": datetime.utcnow().isoformat() + "Z"}
    )


@router.get("/webhooks/n8n/status", response_model=N8nResponse, tags=["n8n"])
async def n8n_status() -> N8nResponse:
    """
    Check n8n integration status.
    
    Returns:
        Status information
    """
    return N8nResponse(
        success=True,
        message="n8n integration is active",
        data={
            "supported_events": [
                "poker_analysis",
                "triage_session",
                "deep_session",
                "user_notification",
                "custom"
            ]
        }
    )
