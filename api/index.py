"""Vercel serverless handler for Poker Therapist API.

Exposes player classification, HUD formatting, and stats cache
functionality via FastAPI running as a Vercel serverless function.

Vercel executes this file as a serverless function.  The project root
directory (one level above ``api/``) is added to ``sys.path`` so the
sibling modules (``player_classifier``, ``player_stats_cache``, ``hud``,
etc.) can be imported with simple top-level names.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Path fix – make project root importable in Vercel's serverless environment.
# Vercel runs api/index.py from the repo root, but Python's default path
# may not include it.  Insert it explicitly so local modules resolve.
# ---------------------------------------------------------------------------
_project_root = str(Path(__file__).parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from player_classifier import classify_player, get_strategy_suggestions
from player_stats_cache import PlayerStatsCache
from hud import format_hud_display, format_hud_compact

app = FastAPI(
    title="Poker Therapist API",
    description="Player style classification, stats cache, and HUD display.",
    version="1.0.0",
)

_cache = PlayerStatsCache()
# Note: in Vercel's serverless environment each function instance is isolated;
# the SQLite database lives in an ephemeral /tmp directory.  Stats persist
# within a single warm instance but are not shared across concurrent invocations.
# For durable storage replace PlayerStatsCache with an external database.


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class PlayerStats(BaseModel):
    player_id: str
    vpip: float = Field(..., ge=0, le=100)
    pfr: float = Field(..., ge=0, le=100)
    threebet: float = Field(0.0, ge=0, le=100)
    af: Optional[float] = None
    wtsd: Optional[float] = None
    hands: int = Field(0, ge=0)
    player_style: Optional[str] = None


class ClassifyRequest(BaseModel):
    vpip: float = Field(..., ge=0, le=100)
    pfr: float = Field(..., ge=0, le=100)
    threebet: float = Field(0.0, ge=0, le=100)


class ClassifyResponse(BaseModel):
    style: str
    suggestions: List[str]


class HudResponse(BaseModel):
    full: str
    compact: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def root() -> Dict[str, str]:
    """Health-check / index."""
    return {"status": "ok", "service": "Poker Therapist API"}


@app.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest) -> ClassifyResponse:
    """Classify a player's style from VPIP / PFR / 3BET stats."""
    style = classify_player(vpip=req.vpip, pfr=req.pfr, threebet=req.threebet)
    suggestions = get_strategy_suggestions(style)
    return ClassifyResponse(style=style, suggestions=suggestions)


@app.post("/hud", response_model=HudResponse)
def hud(stats: PlayerStats) -> HudResponse:
    """Return formatted HUD strings for the given player stats.

    If ``player_style`` is omitted it is derived automatically from the
    VPIP / PFR / 3BET values via the classifier.
    """
    stats_dict: Dict[str, Any] = stats.model_dump()
    if not stats_dict.get("player_style"):
        stats_dict["player_style"] = classify_player(
            vpip=stats.vpip, pfr=stats.pfr, threebet=stats.threebet
        )
    return HudResponse(
        full=format_hud_display(stats_dict),
        compact=format_hud_compact(stats_dict),
    )


@app.post("/stats/update")
def update_stats(stats: PlayerStats) -> Dict[str, Any]:
    """Persist player stats to the SQLite cache and return the stored row."""
    _cache.update_stats(
        player_id=stats.player_id,
        vpip=stats.vpip,
        pfr=stats.pfr,
        threebet=stats.threebet,
        af=stats.af if stats.af is not None else 0.0,
        wtsd=stats.wtsd if stats.wtsd is not None else 0.0,
        hands=stats.hands,
    )
    row = _cache.get_player_stats(stats.player_id)
    if row is None:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stats for player '{stats.player_id}' after update")
    return row


@app.get("/stats/{player_id}")
def get_stats(player_id: str) -> Dict[str, Any]:
    """Retrieve cached stats for a player."""
    row = _cache.get_player_stats(player_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return row


# ---------------------------------------------------------------------------
# Vercel entry-point – the runtime looks for a symbol named ``handler``
# or the ASGI ``app`` object directly.
# ---------------------------------------------------------------------------
handler = app
