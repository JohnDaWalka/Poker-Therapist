"""WinningPokerNetwork (WPN) post-session ingestion and review routes.

Goal: allow Therapy Rex to view a user's session hands after the session
by importing exported hand histories from WPN sites like:
- BetACR
- Americas Cardroom (ACR)
- Black Chip Poker
- True Poker
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sqlalchemy import desc, func, select

from backend.agent.ai_orchestrator import AIOrchestrator
from backend.agent.memory.database import HandHistory
from backend.agent.memory.db_session import get_db
from backend.api.models import (
    WPNImportResponse,
    WPNImportTextRequest,
    WPNSessionHandsResponse,
    WPNSessionListResponse,
    WPNSessionReviewRequest,
    WPNSessionReviewResponse,
    WPNSessionSummary,
)
from backend.blockchain.wpn_parser import parse_many


router = APIRouter()
orchestrator = AIOrchestrator()


async def _import_text(
    *,
    user_id: str,
    session_id: Optional[str],
    hand_history_text: str,
) -> WPNImportResponse:
    parsed = parse_many(hand_history_text)
    if not parsed:
        return WPNImportResponse(session_id=session_id, imported_hands=0, skipped_hands=0)

    imported = 0
    skipped = 0

    # If user didn't provide a session_id, make one so post-session review is easy.
    resolved_session_id = session_id or str(uuid4())

    async with get_db() as db:
        for h in parsed:
            if not h.raw_text:
                skipped += 1
                continue

            model = HandHistory(
                user_id=user_id,
                session_id=resolved_session_id,
                site="WinningPokerNetwork",
                hand_id=h.hand_id,
                date_played=h.date_played,
                game_variant=h.game_variant or "NLHE",
                stakes=h.stakes,
                player_name=h.player_name,
                position=h.position,
                hole_cards=h.hole_cards,
                board=h.board,
                actions=h.actions,
                won_amount=h.won_amount,
                pot_size=h.pot_size,
                raw_text=h.raw_text,
                source="wpn_export",
                tx_hash=None,
                verified=False,
                created_at=datetime.utcnow(),
            )

            db.add(model)
            imported += 1

    return WPNImportResponse(
        session_id=resolved_session_id,
        imported_hands=imported,
        skipped_hands=skipped,
    )


@router.post("/wpn/import-text", response_model=WPNImportResponse)
async def import_wpn_text(request: WPNImportTextRequest) -> WPNImportResponse:
    """Import WPN hands as raw text (JSON body)."""
    try:
        return await _import_text(
            user_id=request.user_id,
            session_id=request.session_id,
            hand_history_text=request.hand_history_text,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/wpn/import-file", response_model=WPNImportResponse)
async def import_wpn_file(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    session_id: Optional[str] = Form(None),
) -> WPNImportResponse:
    """Import WPN hands from an uploaded text file."""
    try:
        data = await file.read()
        text = data.decode("utf-8", errors="ignore")
        return await _import_text(
            user_id=user_id,
            session_id=session_id,
            hand_history_text=text,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/wpn/session-review", response_model=WPNSessionReviewResponse)
async def wpn_session_review(
    request: WPNSessionReviewRequest,
) -> WPNSessionReviewResponse:
    """Let the Therapist review a stored WPN session (multi-hand)."""
    try:
        async with get_db() as db:
            stmt = (
                select(HandHistory)
                .where(HandHistory.user_id == request.user_id)
                .where(HandHistory.session_id == request.session_id)
                .order_by(desc(HandHistory.date_played), desc(HandHistory.created_at))
                .limit(request.max_hands)
            )
            result = await db.execute(stmt)
            hands = list(result.scalars().all())

        if not hands:
            raise HTTPException(status_code=404, detail="No hands found for that session")

        combined = "\n\n".join(h.raw_text for h in hands if h.raw_text)

        context = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "session_hands": combined,
            "num_hands": len(hands),
        }

        ai = await orchestrator.route_query("session_review", context)
        return WPNSessionReviewResponse(
            strategy_review=ai.get("strategy_review", ""),
            therapy_review=ai.get("therapy_review", ""),
            citations=ai.get("citations", []),
            models=ai.get("models", ["perplexity", "openai"]),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/wpn/sessions/{user_id}", response_model=WPNSessionListResponse)
async def list_wpn_sessions(user_id: str) -> WPNSessionListResponse:
    """List known WPN sessions for a user (based on imported hands)."""
    try:
        async with get_db() as db:
            stmt = (
                select(
                    HandHistory.session_id,
                    func.count(HandHistory.id).label("hands"),
                    func.max(HandHistory.date_played).label("last_played"),
                )
                .where(HandHistory.user_id == user_id)
                .where(HandHistory.site == "WinningPokerNetwork")
                .where(HandHistory.session_id.isnot(None))
                .group_by(HandHistory.session_id)
                .order_by(desc(func.max(HandHistory.date_played)), desc(func.count(HandHistory.id)))
            )

            result = await db.execute(stmt)
            rows = result.all()

        sessions = [
            WPNSessionSummary(
                session_id=str(r.session_id),
                hands=int(r.hands or 0),
                last_played=r.last_played,
            )
            for r in rows
            if r.session_id
        ]

        return WPNSessionListResponse(user_id=user_id, sessions=sessions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/wpn/session/{user_id}/{session_id}", response_model=WPNSessionHandsResponse)
async def get_wpn_session_hands(
    user_id: str,
    session_id: str,
    limit: int = 200,
) -> WPNSessionHandsResponse:
    """Fetch stored WPN hands for a given session.

    Returns a lightweight list of dicts so UIs can display and the Therapist can
    pull exact hand text as needed.
    """
    try:
        limit = max(1, min(limit, 500))
        async with get_db() as db:
            stmt = (
                select(HandHistory)
                .where(HandHistory.user_id == user_id)
                .where(HandHistory.session_id == session_id)
                .where(HandHistory.site == "WinningPokerNetwork")
                .order_by(desc(HandHistory.date_played), desc(HandHistory.created_at))
                .limit(limit)
            )
            result = await db.execute(stmt)
            hands = list(result.scalars().all())

        out = [
            {
                "hand_id": h.hand_id,
                "date_played": h.date_played.isoformat() if h.date_played else None,
                "stakes": h.stakes,
                "game_variant": h.game_variant,
                "hole_cards": h.hole_cards,
                "board": h.board,
                "won_amount": h.won_amount,
                "pot_size": h.pot_size,
                "raw_text": h.raw_text,
            }
            for h in hands
        ]

        return WPNSessionHandsResponse(user_id=user_id, session_id=session_id, hands=out)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
