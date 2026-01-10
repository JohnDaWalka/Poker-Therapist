"""CoinPoker post-session ingestion and review routes.

Goal: allow Therapy Rex ("Therapist") to view a user's session hands after the session
by importing exported hand histories and optionally verifying any referenced tx hashes.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sqlalchemy import case, desc, func, select

from backend.agent.ai_orchestrator import AIOrchestrator
from backend.agent.memory.database import HandHistory
from backend.agent.memory.db_session import get_db
from backend.api.models import (
    CoinPokerImportResponse,
    CoinPokerImportTextRequest,
    CoinPokerSessionHandsResponse,
    CoinPokerSessionListResponse,
    CoinPokerSessionReviewRequest,
    CoinPokerSessionReviewResponse,
    CoinPokerSessionSummary,
)
from backend.blockchain.coinpoker_parser import parse_many
from backend.blockchain.evm_rpc import verify_tx
from backend.blockchain.coinpoker_rng_verifier import verify_rng


router = APIRouter()
orchestrator = AIOrchestrator()


async def _import_text(
    *,
    user_id: str,
    session_id: Optional[str],
    hand_history_text: str,
    rpc_url: Optional[str],
    verify_onchain: bool,
    verify_rng: bool,
) -> CoinPokerImportResponse:
    parsed = parse_many(hand_history_text)
    if not parsed:
        return CoinPokerImportResponse(session_id=session_id, imported_hands=0, verified_hands=0, skipped_hands=0)

    imported = 0
    verified = 0
    rng_verified = 0
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
                site="CoinPoker",
                hand_id=h.hand_id,
                date_played=h.date_played,
                game_variant="NLHE",
                stakes=h.stakes,
                player_name=h.player_name,
                position=None,
                hole_cards=h.hole_cards,
                board=h.board,
                actions=h.actions,
                won_amount=h.won_amount,
                pot_size=None,
                raw_text=h.raw_text,
                source="coinpoker_export",
                tx_hash=h.tx_hash,
                verified=False,
                rng_phrase=h.rng_phrase,
                rng_combined_seed_hash=h.rng_combined_seed_hash,
                rng_verified=False,
                rng_verification=None,
                created_at=datetime.utcnow(),
            )

            if verify_onchain and rpc_url and h.tx_hash:
                v = await verify_tx(rpc_url, h.tx_hash)
                model.verified = bool(v.get("verified"))
                model.chain_id = v.get("chain_id")
                model.block_number = v.get("block_number")
                model.tx_status = v.get("tx_status")
                if model.verified:
                    verified += 1

            if verify_rng:
                rng = verify_rng(h.raw_text)
                model.rng_verification = rng
                model.rng_phrase = rng.get("phrase") or model.rng_phrase
                model.rng_combined_seed_hash = rng.get("combined_seed_hash") or model.rng_combined_seed_hash
                model.rng_verified = bool(rng.get("ok"))
                if model.rng_verified:
                    rng_verified += 1

            db.add(model)
            imported += 1

    return CoinPokerImportResponse(
        session_id=resolved_session_id,
        imported_hands=imported,
        verified_hands=verified,
        skipped_hands=skipped,
        rng_verified_hands=rng_verified,
    )


@router.post("/coinpoker/import-text", response_model=CoinPokerImportResponse)
async def import_coinpoker_text(request: CoinPokerImportTextRequest) -> CoinPokerImportResponse:
    """Import CoinPoker hands as raw text (JSON body)."""
    try:
        return await _import_text(
            user_id=request.user_id,
            session_id=request.session_id,
            hand_history_text=request.hand_history_text,
            rpc_url=request.rpc_url,
            verify_onchain=request.verify_onchain,
            verify_rng=request.verify_rng,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/coinpoker/import-file", response_model=CoinPokerImportResponse)
async def import_coinpoker_file(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    session_id: Optional[str] = Form(None),
    rpc_url: Optional[str] = Form(None),
    verify_onchain: bool = Form(False),
    verify_rng: bool = Form(True),
) -> CoinPokerImportResponse:
    """Import CoinPoker hands from an uploaded text file."""
    try:
        data = await file.read()
        text = data.decode("utf-8", errors="ignore")
        return await _import_text(
            user_id=user_id,
            session_id=session_id,
            hand_history_text=text,
            rpc_url=rpc_url,
            verify_onchain=verify_onchain,
            verify_rng=verify_rng,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/coinpoker/session-review", response_model=CoinPokerSessionReviewResponse)
async def coinpoker_session_review(
    request: CoinPokerSessionReviewRequest,
) -> CoinPokerSessionReviewResponse:
    """Let the Therapist review a stored session (multi-hand)."""
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

        # Build a compact provably-fair summary for the agent.
        rng_verified_count = sum(1 for h in hands if h.rng_verified)
        rng_verifiable_total = 0
        rng_verified_lines_total = 0
        rng_mismatch_total = 0
        mismatch_samples = []

        for h in hands:
            v = h.rng_verification or {}
            if isinstance(v, dict):
                rng_verifiable_total += int(v.get("verifiable_lines", 0) or 0)
                rng_verified_lines_total += int(v.get("verified_lines", 0) or 0)
                mismatches = v.get("mismatches") or []
                if isinstance(mismatches, list):
                    rng_mismatch_total += len(mismatches)
                    # Keep a couple of samples across the session.
                    for mm in mismatches[:2]:
                        if len(mismatch_samples) >= 5:
                            break
                        if isinstance(mm, dict):
                            mismatch_samples.append(mm)
            if len(mismatch_samples) >= 5:
                break

        context = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "session_hands": combined,
            "num_hands": len(hands),
            "verified_count": sum(1 for h in hands if h.verified),
            "rng_verified_count": rng_verified_count,
            "rng_verifiable_lines_total": rng_verifiable_total,
            "rng_verified_lines_total": rng_verified_lines_total,
            "rng_mismatch_total": rng_mismatch_total,
            "rng_mismatch_samples": mismatch_samples,
        }

        ai = await orchestrator.route_query("session_review", context)
        return CoinPokerSessionReviewResponse(
            strategy_review=ai.get("strategy_review", ""),
            therapy_review=ai.get("therapy_review", ""),
            citations=ai.get("citations", []),
            models=ai.get("models", ["perplexity", "openai"]),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/coinpoker/sessions/{user_id}", response_model=CoinPokerSessionListResponse)
async def list_coinpoker_sessions(user_id: str) -> CoinPokerSessionListResponse:
    """List known sessions for a user (based on imported hands)."""
    try:
        async with get_db() as db:
            stmt = (
                select(
                    HandHistory.session_id,
                    func.count(HandHistory.id).label("hands"),
                    func.sum(case((HandHistory.rng_verified.is_(True), 1), else_=0)).label(
                        "rng_verified_hands"
                    ),
                    func.max(HandHistory.date_played).label("last_played"),
                )
                .where(HandHistory.user_id == user_id)
                .where(HandHistory.session_id.isnot(None))
                .group_by(HandHistory.session_id)
                .order_by(desc(func.max(HandHistory.date_played)), desc(func.count(HandHistory.id)))
            )

            result = await db.execute(stmt)
            rows = result.all()

        sessions = [
            CoinPokerSessionSummary(
                session_id=str(r.session_id),
                hands=int(r.hands or 0),
                rng_verified_hands=int(r.rng_verified_hands or 0),
                last_played=r.last_played,
            )
            for r in rows
            if r.session_id
        ]

        return CoinPokerSessionListResponse(user_id=user_id, sessions=sessions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/coinpoker/session/{user_id}/{session_id}", response_model=CoinPokerSessionHandsResponse)
async def get_coinpoker_session_hands(
    user_id: str,
    session_id: str,
    limit: int = 200,
) -> CoinPokerSessionHandsResponse:
    """Fetch stored hands for a given session.

    Returns a lightweight list of dicts so UIs can display and the Therapist can
    pull exact hand text (including RNG proof) as needed.
    """
    try:
        limit = max(1, min(limit, 500))
        async with get_db() as db:
            stmt = (
                select(HandHistory)
                .where(HandHistory.user_id == user_id)
                .where(HandHistory.session_id == session_id)
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
                "hole_cards": h.hole_cards,
                "board": h.board,
                "won_amount": h.won_amount,
                "rng_verified": bool(h.rng_verified),
                "rng_phrase": h.rng_phrase,
                "rng_combined_seed_hash": h.rng_combined_seed_hash,
                "raw_text": h.raw_text,
            }
            for h in hands
        ]

        return CoinPokerSessionHandsResponse(user_id=user_id, session_id=session_id, hands=out)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
