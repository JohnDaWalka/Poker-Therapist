"""PokerTracker 4 integration API routes."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.agent.memory.database import HandHistory
from backend.agent.memory.db_session import get_db
from backend.integrations.pt4_connector import PT4Config, PT4Connector


router = APIRouter()


class PT4ImportRequest(BaseModel):
    """Request to import hands from PT4 database."""
    user_id: str
    player_name: str
    session_id: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=500)
    site_filter: Optional[str] = Field(default=None, description="Filter by site name (e.g., 'Americas Cardroom')")
    pt4_config: Optional[dict] = Field(default=None, description="Optional PT4 database config override")


class PT4ImportResponse(BaseModel):
    """Response from PT4 import."""
    session_id: str
    imported_hands: int
    skipped_hands: int


class PT4SessionImportRequest(BaseModel):
    """Request to import a session from PT4 by time range."""
    user_id: str
    player_name: str
    session_id: Optional[str] = None
    session_start: datetime
    session_end: Optional[datetime] = None
    pt4_config: Optional[dict] = None


class PT4TestConnectionRequest(BaseModel):
    """Request to test PT4 database connection."""
    pt4_config: Optional[dict] = None


class PT4TestConnectionResponse(BaseModel):
    """Response from PT4 connection test."""
    connected: bool
    message: str
    sites: list[dict] = []


class PT4PlayerListResponse(BaseModel):
    """Response with list of players."""
    players: list[str]


@router.post("/pt4/test-connection", response_model=PT4TestConnectionResponse)
async def test_pt4_connection(
    request: PT4TestConnectionRequest,
) -> PT4TestConnectionResponse:
    """Test connection to PokerTracker 4 database.
    
    This endpoint verifies:
    1. PT4 PostgreSQL database is accessible
    2. Credentials are correct
    3. Can query site information
    """
    try:
        # Build config from request or use defaults
        if request.pt4_config:
            config = PT4Config(**request.pt4_config)
        else:
            config = PT4Config.from_env()
        
        # Try to connect
        with PT4Connector(config) as pt4:
            connected = pt4.test_connection()
            
            if not connected:
                return PT4TestConnectionResponse(
                    connected=False,
                    message="Failed to connect to PT4 database. Check credentials and ensure PT4 is running.",
                    sites=[],
                )
            
            # Get available sites
            try:
                sites = pt4.get_sites()
            except Exception:
                sites = []
            
            return PT4TestConnectionResponse(
                connected=True,
                message="Successfully connected to PokerTracker 4 database!",
                sites=sites,
            )
    
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e) + " Install psycopg2-binary to use PT4 integration."
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error connecting to PT4: {str(e)}"
        ) from e


@router.post("/pt4/list-players", response_model=PT4PlayerListResponse)
async def list_pt4_players(
    request: PT4TestConnectionRequest,
) -> PT4PlayerListResponse:
    """Get list of player names from PT4 database."""
    try:
        if request.pt4_config:
            config = PT4Config(**request.pt4_config)
        else:
            config = PT4Config.from_env()
        
        with PT4Connector(config) as pt4:
            players = pt4.get_player_names()
            return PT4PlayerListResponse(players=players)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching players from PT4: {str(e)}"
        ) from e


@router.post("/pt4/import-recent", response_model=PT4ImportResponse)
async def import_recent_hands_from_pt4(
    request: PT4ImportRequest,
) -> PT4ImportResponse:
    """Import recent hands from PokerTracker 4 database.
    
    This endpoint:
    1. Connects to PT4 PostgreSQL database
    2. Queries recent hands for the specified player
    3. Imports them into Therapy Rex database for analysis
    """
    try:
        # Build PT4 config
        if request.pt4_config:
            config = PT4Config(**request.pt4_config)
        else:
            config = PT4Config.from_env()
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid4())
        
        # Connect to PT4 and fetch hands
        with PT4Connector(config) as pt4:
            hands = pt4.get_recent_hands(
                player_name=request.player_name,
                limit=request.limit,
                site_filter=request.site_filter,
            )
        
        if not hands:
            return PT4ImportResponse(
                session_id=session_id,
                imported_hands=0,
                skipped_hands=0,
            )
        
        # Import hands into Therapy Rex database
        imported = 0
        skipped = 0
        
        async with get_db() as db:
            for h in hands:
                try:
                    # Get raw hand history text if available
                    with PT4Connector(config) as pt4:
                        raw_text = pt4.get_hand_history_text(h["id_hand"])
                    
                    model = HandHistory(
                        user_id=request.user_id,
                        session_id=session_id,
                        site=h.get("site_name", "Unknown"),
                        hand_id=str(h["id_hand"]),
                        date_played=h.get("date_played"),
                        game_variant=h.get("game_type_name", "NLHE"),
                        stakes=f"${h.get('amt_bb', 0) / 2:.2f}/${h.get('amt_bb', 0):.2f}",
                        player_name=h.get("player_name"),
                        position=str(h.get("position")) if h.get("position") is not None else None,
                        hole_cards=h.get("holecards"),
                        board=h.get("board"),
                        actions=None,  # Not extracted from PT4 summary query
                        won_amount=float(h["amt_won"]) if h.get("amt_won") is not None else None,
                        pot_size=float(h["amt_pot"]) if h.get("amt_pot") is not None else None,
                        raw_text=raw_text or "",
                        source="pt4_import",
                        created_at=datetime.utcnow(),
                    )
                    
                    db.add(model)
                    imported += 1
                
                except Exception:
                    skipped += 1
                    continue
        
        return PT4ImportResponse(
            session_id=session_id,
            imported_hands=imported,
            skipped_hands=skipped,
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error importing hands from PT4: {str(e)}"
        ) from e


@router.post("/pt4/import-session", response_model=PT4ImportResponse)
async def import_session_from_pt4(
    request: PT4SessionImportRequest,
) -> PT4ImportResponse:
    """Import a complete session from PT4 by time range.
    
    Use this for post-session analysis to import all hands played
    during a specific time period.
    """
    try:
        # Build PT4 config
        if request.pt4_config:
            config = PT4Config(**request.pt4_config)
        else:
            config = PT4Config.from_env()
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid4())
        
        # Connect to PT4 and fetch session hands
        with PT4Connector(config) as pt4:
            hands = pt4.get_hands_by_session(
                player_name=request.player_name,
                session_start=request.session_start,
                session_end=request.session_end,
            )
        
        if not hands:
            return PT4ImportResponse(
                session_id=session_id,
                imported_hands=0,
                skipped_hands=0,
            )
        
        # Import hands into Therapy Rex database
        imported = 0
        skipped = 0
        
        async with get_db() as db:
            for h in hands:
                try:
                    # Get raw hand history text if available
                    with PT4Connector(config) as pt4:
                        raw_text = pt4.get_hand_history_text(h["id_hand"])
                    
                    model = HandHistory(
                        user_id=request.user_id,
                        session_id=session_id,
                        site=h.get("site_name", "Unknown"),
                        hand_id=str(h["id_hand"]),
                        date_played=h.get("date_played"),
                        game_variant=h.get("game_type_name", "NLHE"),
                        stakes=f"${h.get('amt_bb', 0) / 2:.2f}/${h.get('amt_bb', 0):.2f}",
                        player_name=h.get("player_name"),
                        position=str(h.get("position")) if h.get("position") is not None else None,
                        hole_cards=h.get("holecards"),
                        board=h.get("board"),
                        actions=None,
                        won_amount=float(h["amt_won"]) if h.get("amt_won") is not None else None,
                        pot_size=float(h["amt_pot"]) if h.get("amt_pot") is not None else None,
                        raw_text=raw_text or "",
                        source="pt4_session_import",
                        created_at=datetime.utcnow(),
                    )
                    
                    db.add(model)
                    imported += 1
                
                except Exception:
                    skipped += 1
                    continue
        
        return PT4ImportResponse(
            session_id=session_id,
            imported_hands=imported,
            skipped_hands=skipped,
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error importing session from PT4: {str(e)}"
        ) from e
