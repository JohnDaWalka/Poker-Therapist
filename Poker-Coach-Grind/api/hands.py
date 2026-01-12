"""Hand history management API routes with SQL query support."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, select, text

from ..database.models import HandHistoryGrind
from ..database.session import get_grind_db

router = APIRouter()


class HandImportRequest(BaseModel):
    """Request model for importing hand histories."""
    
    user_id: str
    session_id: Optional[str] = None
    platform: str
    hands: List[Dict[str, Any]]  # List of hand data dictionaries


class HandImportResponse(BaseModel):
    """Response model for hand import."""
    
    session_id: str
    imported_count: int
    skipped_count: int
    total_processed: int


class HandQueryRequest(BaseModel):
    """Request model for SQL hand queries."""
    
    user_id: str
    sql_query: str
    limit: Optional[int] = 100


class HandResponse(BaseModel):
    """Response model for a hand."""
    
    id: int
    user_id: str
    session_id: Optional[str]
    hand_id: Optional[str]
    platform: str
    date_played: datetime
    game_type: Optional[str]
    stakes: Optional[str]
    hero_position: Optional[str]
    hole_cards: Optional[str]
    board: Optional[str]
    won_amount: Optional[float]
    pot_size: Optional[float]
    actions: Optional[str]
    summary: Optional[str]


@router.post("/import", response_model=HandImportResponse)
async def import_hands(request: HandImportRequest) -> HandImportResponse:
    """Import hand histories."""
    try:
        from uuid import uuid4
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid4())
        
        imported = 0
        skipped = 0
        
        async with get_grind_db() as db:
            for hand_data in request.hands:
                try:
                    # Parse date if string
                    date_played = hand_data.get("date_played")
                    if isinstance(date_played, str):
                        date_played = datetime.fromisoformat(date_played)
                    elif not isinstance(date_played, datetime):
                        date_played = datetime.utcnow()
                    
                    hand = HandHistoryGrind(
                        user_id=request.user_id,
                        session_id=session_id,
                        hand_id=hand_data.get("hand_id"),
                        platform=request.platform,
                        date_played=date_played,
                        game_type=hand_data.get("game_type"),
                        stakes=hand_data.get("stakes"),
                        table_name=hand_data.get("table_name"),
                        num_players=hand_data.get("num_players"),
                        hero_position=hand_data.get("hero_position"),
                        hole_cards=hand_data.get("hole_cards"),
                        board=hand_data.get("board"),
                        pot_size=hand_data.get("pot_size"),
                        won_amount=hand_data.get("won_amount"),
                        vpip=hand_data.get("vpip"),
                        pfr=hand_data.get("pfr"),
                        aggression_factor=hand_data.get("aggression_factor"),
                        showdown_won=hand_data.get("showdown_won", 0),
                        all_in=hand_data.get("all_in", 0),
                        actions=hand_data.get("actions"),
                        summary=hand_data.get("summary"),
                        raw_text=hand_data.get("raw_text", ""),
                        tx_hash=hand_data.get("tx_hash"),
                        verified=hand_data.get("verified", 0),
                    )
                    
                    db.add(hand)
                    imported += 1
                
                except Exception as e:
                    print(f"Error importing hand: {e}")
                    skipped += 1
            
            await db.commit()
        
        return HandImportResponse(
            session_id=session_id,
            imported_count=imported,
            skipped_count=skipped,
            total_processed=len(request.hands),
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/query")
async def query_hands(request: HandQueryRequest) -> List[Dict[str, Any]]:
    """Execute SQL query on hand histories.
    
    Note: This is a powerful feature. In production, implement:
    - Query validation to prevent malicious SQL
    - Rate limiting
    - Query timeout limits
    - Read-only access
    """
    try:
        # Enhanced SQL injection protection
        # Note: For production, consider implementing a query builder or using stored procedures
        dangerous_patterns = [
            "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE",
            "EXEC", "EXECUTE", "GRANT", "REVOKE", "--", "/*", "*/", ";",
            "UNION", "INTO OUTFILE", "INTO DUMPFILE", "LOAD_FILE"
        ]
        query_upper = request.sql_query.upper()
        
        for pattern in dangerous_patterns:
            if pattern in query_upper:
                raise HTTPException(
                    status_code=400,
                    detail=f"Query contains forbidden pattern: {pattern}. For security, only SELECT queries with user_id filter are allowed."
                )
        
        # Ensure it's a SELECT query
        if not query_upper.strip().startswith("SELECT"):
            raise HTTPException(
                status_code=400,
                detail="Only SELECT queries are allowed"
            )
        
        # Ensure user_id filter is in query for security
        if "user_id" not in request.sql_query.lower():
            raise HTTPException(
                status_code=400,
                detail="Query must include user_id filter for security"
            )
        
        # Apply limit
        limit = min(request.limit or 100, 500)
        
        async with get_grind_db() as db:
            # Execute query
            result = await db.execute(text(request.sql_query))
            rows = result.fetchmany(limit)
            
            # Convert to list of dicts
            columns = result.keys()
            hands = [dict(zip(columns, row)) for row in rows]
            
            return hands
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{hand_id}", response_model=HandResponse)
async def get_hand(hand_id: int) -> HandResponse:
    """Get a specific hand by ID."""
    try:
        async with get_grind_db() as db:
            stmt = select(HandHistoryGrind).where(HandHistoryGrind.id == hand_id)
            result = await db.execute(stmt)
            hand = result.scalar_one_or_none()
            
            if not hand:
                raise HTTPException(status_code=404, detail="Hand not found")
            
            return HandResponse(
                id=hand.id,
                user_id=hand.user_id,
                session_id=hand.session_id,
                hand_id=hand.hand_id,
                platform=hand.platform,
                date_played=hand.date_played,
                game_type=hand.game_type,
                stakes=hand.stakes,
                hero_position=hand.hero_position,
                hole_cards=hand.hole_cards,
                board=hand.board,
                won_amount=hand.won_amount,
                pot_size=hand.pot_size,
                actions=hand.actions,
                summary=hand.summary,
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/session/{session_id}", response_model=List[HandResponse])
async def get_session_hands(
    session_id: str,
    limit: int = 200
) -> List[HandResponse]:
    """Get all hands from a session."""
    try:
        async with get_grind_db() as db:
            stmt = (
                select(HandHistoryGrind)
                .where(HandHistoryGrind.session_id == session_id)
                .order_by(desc(HandHistoryGrind.date_played))
                .limit(min(limit, 500))
            )
            result = await db.execute(stmt)
            hands = result.scalars().all()
            
            return [
                HandResponse(
                    id=hand.id,
                    user_id=hand.user_id,
                    session_id=hand.session_id,
                    hand_id=hand.hand_id,
                    platform=hand.platform,
                    date_played=hand.date_played,
                    game_type=hand.game_type,
                    stakes=hand.stakes,
                    hero_position=hand.hero_position,
                    hole_cards=hand.hole_cards,
                    board=hand.board,
                    won_amount=hand.won_amount,
                    pot_size=hand.pot_size,
                    actions=hand.actions,
                    summary=hand.summary,
                )
                for hand in hands
            ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/user/{user_id}/recent", response_model=List[HandResponse])
async def get_recent_hands(
    user_id: str,
    limit: int = 50
) -> List[HandResponse]:
    """Get recent hands for a user."""
    try:
        async with get_grind_db() as db:
            stmt = (
                select(HandHistoryGrind)
                .where(HandHistoryGrind.user_id == user_id)
                .order_by(desc(HandHistoryGrind.date_played))
                .limit(min(limit, 200))
            )
            result = await db.execute(stmt)
            hands = result.scalars().all()
            
            return [
                HandResponse(
                    id=hand.id,
                    user_id=hand.user_id,
                    session_id=hand.session_id,
                    hand_id=hand.hand_id,
                    platform=hand.platform,
                    date_played=hand.date_played,
                    game_type=hand.game_type,
                    stakes=hand.stakes,
                    hero_position=hand.hero_position,
                    hole_cards=hand.hole_cards,
                    board=hand.board,
                    won_amount=hand.won_amount,
                    pot_size=hand.pot_size,
                    actions=hand.actions,
                    summary=hand.summary,
                )
                for hand in hands
            ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
