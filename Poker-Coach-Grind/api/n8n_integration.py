"""n8n workflow integration for Poker-Coach-Grind.

This module provides webhook endpoints and utilities to integrate with n8n workflows
for automated bankroll tracking, hand analysis, and crypto monitoring.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


class N8NWebhookPayload(BaseModel):
    """Generic n8n webhook payload."""
    
    workflow_id: Optional[str] = None
    execution_id: Optional[str] = None
    trigger: str
    data: Dict[str, Any]


class N8NWorkflowTrigger(BaseModel):
    """Trigger data sent to n8n workflows."""
    
    event_type: str
    timestamp: str
    user_id: str
    data: Dict[str, Any]


class N8NClient:
    """Client for interacting with n8n workflows."""
    
    def __init__(self, n8n_url: str, api_key: Optional[str] = None):
        """Initialize n8n client.
        
        Args:
            n8n_url: Base URL of n8n instance (e.g., https://your-n8n.com)
            api_key: Optional API key for authentication
        """
        self.n8n_url = n8n_url.rstrip("/")
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers["X-N8N-API-KEY"] = api_key
    
    async def trigger_webhook(
        self,
        webhook_path: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger an n8n webhook.
        
        Args:
            webhook_path: Webhook path (e.g., 'bankroll-update')
            data: Data to send to webhook
            
        Returns:
            Response from n8n webhook
        """
        url = f"{self.n8n_url}/webhook/{webhook_path}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=data,
                    headers=self.headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json() if response.text else {"status": "success"}
        
        except httpx.HTTPError as e:
            print(f"Error triggering n8n webhook: {e}")
            return {"status": "error", "message": str(e)}
    
    async def trigger_workflow(
        self,
        workflow_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger an n8n workflow by ID.
        
        Args:
            workflow_id: n8n workflow ID
            data: Data to pass to workflow
            
        Returns:
            Workflow execution result
        """
        url = f"{self.n8n_url}/api/v1/workflows/{workflow_id}/execute"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={"data": data},
                    headers=self.headers,
                    timeout=60.0,
                )
                response.raise_for_status()
                return response.json()
        
        except httpx.HTTPError as e:
            print(f"Error executing n8n workflow: {e}")
            return {"status": "error", "message": str(e)}


# Webhook endpoints for n8n to call

@router.post("/webhook/bankroll-transaction")
async def n8n_bankroll_transaction(request: Request):
    """Webhook endpoint for n8n to create bankroll transactions.
    
    Expected payload:
    {
        "user_id": "user123",
        "amount": 250.00,
        "transaction_type": "cash_game",
        "stakes": "1/2",
        "notes": "Good session"
    }
    """
    try:
        payload = await request.json()
        
        # Validate required fields
        required = ["user_id", "amount", "transaction_type"]
        for field in required:
            if field not in payload:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Import here to avoid circular imports
        from ..api.bankroll import create_transaction, TransactionRequest
        
        # Create transaction
        transaction_request = TransactionRequest(
            user_id=payload["user_id"],
            amount=float(payload["amount"]),
            transaction_type=payload["transaction_type"],
            platform=payload.get("platform"),
            stakes=payload.get("stakes"),
            session_id=payload.get("session_id"),
            notes=payload.get("notes"),
            currency=payload.get("currency", "USD"),
            crypto_currency=payload.get("crypto_currency"),
        )
        
        result = await create_transaction(transaction_request)
        
        return {
            "status": "success",
            "transaction_id": result.id,
            "balance_after": result.balance_after,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/webhook/hand-import")
async def n8n_hand_import(request: Request):
    """Webhook endpoint for n8n to import hand histories.
    
    Expected payload:
    {
        "user_id": "user123",
        "platform": "CoinPoker",
        "session_id": "session123",
        "hands": [
            {
                "hand_id": "12345",
                "date_played": "2026-01-11T03:00:00",
                "stakes": "1/2",
                "won_amount": 50.0,
                ...
            }
        ]
    }
    """
    try:
        payload = await request.json()
        
        # Validate required fields
        if "user_id" not in payload or "platform" not in payload or "hands" not in payload:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        from ..api.hands import import_hands, HandImportRequest
        
        import_request = HandImportRequest(
            user_id=payload["user_id"],
            session_id=payload.get("session_id"),
            platform=payload["platform"],
            hands=payload["hands"],
        )
        
        result = await import_hands(import_request)
        
        return {
            "status": "success",
            "session_id": result.session_id,
            "imported_count": result.imported_count,
            "skipped_count": result.skipped_count,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/webhook/crypto-alert")
async def n8n_crypto_alert(request: Request):
    """Webhook endpoint for n8n to receive crypto price alerts.
    
    Expected payload:
    {
        "user_id": "user123",
        "symbol": "ETH",
        "price": 2500.00,
        "alert_type": "price_above",
        "threshold": 2400.00
    }
    """
    try:
        payload = await request.json()
        
        return {
            "status": "success",
            "message": f"Crypto alert received for {payload.get('symbol')}",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/webhook/therapy-session")
async def n8n_therapy_session(request: Request):
    """Webhook endpoint for n8n to trigger Therapy Rex sessions.
    
    Expected payload:
    {
        "user_id": "user123",
        "session_type": "tilt_triage",
        "trigger_reason": "downswing_detected",
        "context": {
            "recent_loss": -500.00,
            "session_duration": 180,
            "hands_played": 150
        }
    }
    """
    try:
        payload = await request.json()
        
        # In production, this would trigger a Therapy Rex session
        # For now, return acknowledgment
        
        return {
            "status": "success",
            "message": "Therapy session triggered",
            "session_type": payload.get("session_type"),
            "user_id": payload.get("user_id"),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# Outbound workflow triggers

async def trigger_bankroll_alert(
    n8n_client: N8NClient,
    user_id: str,
    alert_type: str,
    data: Dict[str, Any]
):
    """Trigger n8n workflow for bankroll alerts.
    
    Args:
        n8n_client: Initialized N8NClient
        user_id: User ID
        alert_type: Type of alert (low_balance, big_win, big_loss, etc.)
        data: Additional alert data
    """
    payload = N8NWorkflowTrigger(
        event_type="bankroll_alert",
        timestamp=datetime.utcnow().isoformat(),
        user_id=user_id,
        data={
            "alert_type": alert_type,
            **data,
        },
    )
    
    return await n8n_client.trigger_webhook(
        "bankroll-alert",
        payload.model_dump()
    )


async def trigger_session_complete(
    n8n_client: N8NClient,
    user_id: str,
    session_id: str,
    stats: Dict[str, Any]
):
    """Trigger n8n workflow when a poker session is complete.
    
    Args:
        n8n_client: Initialized N8NClient
        user_id: User ID
        session_id: Session ID
        stats: Session statistics
    """
    payload = N8NWorkflowTrigger(
        event_type="session_complete",
        timestamp=datetime.utcnow().isoformat(),
        user_id=user_id,
        data={
            "session_id": session_id,
            "stats": stats,
        },
    )
    
    return await n8n_client.trigger_webhook(
        "session-complete",
        payload.model_dump()
    )


async def trigger_crypto_portfolio_update(
    n8n_client: N8NClient,
    user_id: str,
    portfolio_value: float,
    change_percent: float
):
    """Trigger n8n workflow for crypto portfolio updates.
    
    Args:
        n8n_client: Initialized N8NClient
        user_id: User ID
        portfolio_value: Current portfolio value
        change_percent: Percentage change
    """
    payload = N8NWorkflowTrigger(
        event_type="crypto_portfolio_update",
        timestamp=datetime.utcnow().isoformat(),
        user_id=user_id,
        data={
            "portfolio_value": portfolio_value,
            "change_percent": change_percent,
        },
    )
    
    return await n8n_client.trigger_webhook(
        "crypto-portfolio-update",
        payload.model_dump()
    )


__all__ = [
    "N8NClient",
    "N8NWebhookPayload",
    "N8NWorkflowTrigger",
    "router",
    "trigger_bankroll_alert",
    "trigger_session_complete",
    "trigger_crypto_portfolio_update",
]
