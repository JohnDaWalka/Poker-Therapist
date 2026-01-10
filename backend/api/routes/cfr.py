"""CFR strategy API routes."""

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.agent.cfr_service import CFRService


router = APIRouter()
cfr_service = CFRService()


class KuhnStrategyRequest(BaseModel):
    """Request for Kuhn Poker strategy."""
    player_card: str = Field(..., description="Player's card (J, Q, or K)")
    history: str = Field(default="", description="Action history")


class HoldemStrategyRequest(BaseModel):
    """Request for Hold'em strategy advice."""
    hand: List[str] = Field(..., description="Player's hole cards (e.g., ['As', 'Kh'])")
    community_cards: List[str] = Field(default=[], description="Community cards")
    pot: int = Field(..., description="Current pot size")
    bets: List[int] = Field(default=[0, 0], description="Current bets for each player")
    history: str = Field(default="", description="Action history")


class StrategicAdviceRequest(BaseModel):
    """Request for strategic advice."""
    hand: List[str] = Field(..., description="Player's hole cards")
    community_cards: List[str] = Field(default=[], description="Community cards")
    pot: int = Field(..., description="Current pot size")
    position: str = Field(..., description="Player position (BTN, CO, MP, etc.)")
    opponent_tendency: Optional[str] = Field(None, description="Opponent tendency")


class TrainRequest(BaseModel):
    """Request to train CFR model."""
    game: str = Field(..., description="Game type (kuhn_poker or holdem)")
    iterations: int = Field(default=10000, description="Number of training iterations")


@router.post("/cfr/train")
async def train_cfr(request: TrainRequest) -> Dict:
    """Train CFR model for specified game.
    
    Args:
        request: Training request
        
    Returns:
        Training results
    """
    try:
        if request.game == "kuhn_poker":
            result = cfr_service.train_kuhn_poker(request.iterations)
        elif request.game == "holdem":
            result = cfr_service.train_holdem(request.iterations)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown game type: {request.game}"
            )
        
        return {
            "success": True,
            "message": f"Successfully trained {request.game}",
            "results": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cfr/strategy/kuhn")
async def get_kuhn_strategy(request: KuhnStrategyRequest) -> Dict:
    """Get CFR strategy for Kuhn Poker position.
    
    Args:
        request: Strategy request
        
    Returns:
        Strategy with action probabilities
    """
    try:
        strategy = cfr_service.get_kuhn_strategy(
            player_card=request.player_card,
            history=request.history
        )
        
        if "error" in strategy:
            raise HTTPException(status_code=400, detail=strategy["error"])
        
        return {
            "success": True,
            "strategy": strategy,
            "explanation": "Strategy based on CFR Nash equilibrium approximation"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cfr/strategy/holdem")
async def get_holdem_strategy(request: HoldemStrategyRequest) -> Dict:
    """Get CFR strategy advice for Hold'em position.
    
    Args:
        request: Strategy request
        
    Returns:
        Strategy advice with recommendations
    """
    try:
        advice = cfr_service.get_holdem_advice(
            hand=request.hand,
            community_cards=request.community_cards,
            pot=request.pot,
            bets=request.bets,
            history=request.history
        )
        
        if "error" in advice:
            raise HTTPException(status_code=400, detail=advice["error"])
        
        return {
            "success": True,
            "advice": advice,
            "explanation": "Recommendations based on CFR (Counterfactual Regret Minimization)"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cfr/advice")
async def get_strategic_advice(request: StrategicAdviceRequest) -> Dict:
    """Get high-level strategic advice using CFR principles.
    
    Args:
        request: Advice request
        
    Returns:
        Strategic advice and analysis
    """
    try:
        advice = cfr_service.get_strategic_advice(
            hand=request.hand,
            community_cards=request.community_cards,
            pot=request.pot,
            position=request.position,
            opponent_tendency=request.opponent_tendency
        )
        
        return {
            "success": True,
            "advice": advice,
            "methodology": "CFR-based Game Theory Optimal (GTO) strategy with exploitative adjustments"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cfr/status")
async def get_cfr_status() -> Dict:
    """Get status of CFR models.
    
    Returns:
        Status information about trained models
    """
    status = {
        "kuhn_poker": {
            "trained": cfr_service.kuhn_solver is not None,
            "iterations": cfr_service.kuhn_solver.iterations if cfr_service.kuhn_solver else 0,
            "info_sets": len(cfr_service.kuhn_solver.info_sets) if cfr_service.kuhn_solver else 0
        },
        "holdem": {
            "trained": cfr_service.holdem_solver is not None,
            "iterations": cfr_service.holdem_solver.iterations if cfr_service.holdem_solver else 0,
            "info_sets": len(cfr_service.holdem_solver.info_sets) if cfr_service.holdem_solver else 0
        }
    }
    
    return {
        "success": True,
        "models": status,
        "description": "CFR (Counterfactual Regret Minimization) models for poker strategy"
    }


@router.get("/cfr/info")
async def get_cfr_info() -> Dict:
    """Get information about CFR implementation.
    
    Returns:
        Information about CFR and its capabilities
    """
    return {
        "name": "Counterfactual Regret Minimization (CFR)",
        "description": (
            "CFR is a powerful algorithm for solving imperfect-information games like poker. "
            "It iteratively minimizes regret to converge toward a Nash Equilibrium strategy."
        ),
        "features": [
            "Vanilla CFR for small games (Kuhn Poker)",
            "Monte Carlo CFR (MCCFR) for larger games (Texas Hold'em)",
            "Game Theory Optimal (GTO) strategy recommendations",
            "Exploitability analysis",
            "Strategic advice based on CFR principles"
        ],
        "supported_games": [
            {
                "name": "Kuhn Poker",
                "description": "Simple 3-card poker for CFR demonstration",
                "players": 2,
                "solver": "Vanilla CFR"
            },
            {
                "name": "Simplified Texas Hold'em",
                "description": "Heads-up Hold'em with simplified deck and betting",
                "players": 2,
                "solver": "Monte Carlo CFR (MCCFR)"
            }
        ],
        "endpoints": {
            "/cfr/train": "Train CFR models",
            "/cfr/strategy/kuhn": "Get Kuhn Poker strategy",
            "/cfr/strategy/holdem": "Get Hold'em strategy",
            "/cfr/advice": "Get strategic advice",
            "/cfr/status": "Check model status",
            "/cfr/info": "Get CFR information"
        }
    }
