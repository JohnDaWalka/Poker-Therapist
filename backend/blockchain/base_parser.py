"""Base parser module for hand history parsing with cross-policy support.

This module defines the common interface and data structures for parsing
hand histories from different poker platforms (ACR/WPN, CoinPoker, etc.).

The cross-policy design ensures:
1. Normalized action types across platforms
2. Consistent card/board encoding
3. Standardized output format (chroma stream compatible)
4. Easy extension for new platforms
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class NormalizedAction(str, Enum):
    """Normalized action types across all poker platforms.
    
    These actions are standardized across ACR, CoinPoker, and other platforms
    to enable consistent analysis and AI processing.
    """
    
    FOLD = "FOLD"
    CHECK = "CHECK"
    CALL = "CALL"
    RAISE = "RAISE"
    BET = "BET"
    ALL_IN = "ALL_IN"
    POST_SB = "POST_SB"
    POST_BB = "POST_BB"
    POST_ANTE = "POST_ANTE"
    POST_STRADDLE = "POST_STRADDLE"
    SHOW = "SHOW"
    MUCK = "MUCK"
    RETURN_UNCALLED = "RETURN_UNCALLED"
    COLLECTED = "COLLECTED"


class BoardVariant(str, Enum):
    """Board texture classifications for strategic analysis."""
    
    MONOTONE = "MONOTONE"  # All same suit (e.g., Ah Kh Qh)
    RAINBOW = "RAINBOW"  # All different suits (e.g., Ah Kd Qs)
    TWO_TONE = "TWO_TONE"  # Two suits (e.g., Ah Kh Qs)
    PAIRED = "PAIRED"  # Contains a pair (e.g., Ah Ad Ks)
    TRIPS = "TRIPS"  # Three of a kind (e.g., Ah Ad As)


@dataclass
class NormalizedPlayerAction:
    """A single player action with normalized representation."""
    
    player_name: str
    action: NormalizedAction
    amount: Optional[float] = None
    street: Optional[str] = None  # PREFLOP, FLOP, TURN, RIVER
    raw_text: Optional[str] = None  # Original action text for reference


@dataclass
class BoardCards:
    """Structured board representation with analysis."""
    
    flop: Optional[str] = None  # e.g., "AhKhQh"
    turn: Optional[str] = None  # e.g., "Jh"
    river: Optional[str] = None  # e.g., "Th"
    variant: Optional[BoardVariant] = None
    
    @property
    def full_board(self) -> Optional[str]:
        """Return complete board as space-separated string."""
        parts = []
        if self.flop:
            parts.append(self.flop)
        if self.turn:
            parts.append(self.turn)
        if self.river:
            parts.append(self.river)
        return " ".join(parts) if parts else None
    
    @property
    def cards_list(self) -> list[str]:
        """Return list of individual cards."""
        if not self.flop:
            return []
        cards = []
        # Parse flop (3 cards)
        if self.flop:
            cards.extend([self.flop[i:i+2] for i in range(0, len(self.flop), 2)])
        if self.turn:
            cards.append(self.turn)
        if self.river:
            cards.append(self.river)
        return cards


@dataclass
class PlayerInfo:
    """Player information including stack sizes."""
    
    name: str
    seat: Optional[int] = None
    stack_size: Optional[float] = None
    position: Optional[str] = None  # BTN, SB, BB, UTG, etc.


@dataclass
class NormalizedHandHistory:
    """Normalized hand history structure compatible across all platforms.
    
    This structure serves as the output format for all parsers, ensuring
    consistent data for downstream processing (AI analysis, database storage,
    chroma stream encoding).
    """
    
    # Core identifiers
    hand_id: str
    platform: str  # "ACR", "CoinPoker", etc.
    date_played: Optional[datetime]
    
    # Game info
    game_type: Optional[str]  # "Cash Game", "Tournament", "SNG", etc.
    game_variant: Optional[str]  # "NLHE", "PLO", etc.
    stakes: Optional[str]
    
    # Tournament specific
    tournament_id: Optional[str] = None
    buyin: Optional[str] = None
    
    # Player info
    hero_name: Optional[str] = None
    hole_cards: Optional[str] = None  # e.g., "AhKh"
    players: list[PlayerInfo] = None
    
    # Board
    board: Optional[BoardCards] = None
    
    # Actions (normalized)
    actions: list[NormalizedPlayerAction] = None
    
    # Results
    pot_size: Optional[float] = None
    won_amount: Optional[float] = None
    
    # Special features
    has_straddle: bool = False
    dead_cards: Optional[list[str]] = None
    
    # Platform-specific data (preserved for compatibility)
    platform_specific: Optional[dict] = None
    
    # Raw text (for reference)
    raw_text: str = ""
    
    def __post_init__(self) -> None:
        """Initialize default values for mutable fields."""
        if self.players is None:
            self.players = []
        if self.actions is None:
            self.actions = []
        if self.platform_specific is None:
            self.platform_specific = {}
    
    def to_chroma_stream(self) -> dict:
        """Convert to fixed-length chroma stream format for AI processing.
        
        The chroma stream is a standardized format that can be used for:
        - Vector embeddings
        - AI model input
        - Cross-platform analysis
        """
        return {
            "platform": self.platform,
            "hand_id": self.hand_id,
            "timestamp": self.date_played.isoformat() if self.date_played else None,
            "game_type": self.game_type,
            "stakes": self.stakes,
            "hero_cards": self.hole_cards,
            "board": self.board.full_board if self.board else None,
            "board_variant": self.board.variant.value if self.board and self.board.variant else None,
            "actions": [
                {
                    "player": a.player_name,
                    "action": a.action.value,
                    "amount": a.amount,
                    "street": a.street,
                }
                for a in self.actions
            ],
            "pot_size": self.pot_size,
            "won_amount": self.won_amount,
            "has_straddle": self.has_straddle,
            "num_players": len(self.players),
            "tournament_id": self.tournament_id,
        }


def detect_board_variant(cards: list[str]) -> Optional[BoardVariant]:
    """Detect board variant from a list of cards.
    
    Args:
        cards: List of card strings (e.g., ["Ah", "Kh", "Qh"])
        
    Returns:
        BoardVariant enum or None if cannot determine
    """
    if not cards or len(cards) < 3:
        return None
    
    # Extract suits
    suits = [card[-1] for card in cards if len(card) == 2]
    if len(suits) < 3:
        return None
    
    # Extract ranks
    ranks = [card[0] for card in cards if len(card) == 2]
    
    # Check for trips (three of same rank)
    rank_counts = {}
    for rank in ranks:
        rank_counts[rank] = rank_counts.get(rank, 0) + 1
    if 3 in rank_counts.values():
        return BoardVariant.TRIPS
    
    # Check for paired (two of same rank)
    if 2 in rank_counts.values():
        return BoardVariant.PAIRED
    
    # Check suit distribution
    unique_suits = len(set(suits))
    if unique_suits == 1:
        return BoardVariant.MONOTONE
    elif unique_suits == 3:
        return BoardVariant.RAINBOW
    else:
        return BoardVariant.TWO_TONE


def normalize_cards(cards: str) -> str:
    """Normalize card string by removing whitespace.
    
    Args:
        cards: Card string with possible spaces (e.g., "Ah Kh")
        
    Returns:
        Normalized card string (e.g., "AhKh")
    """
    return re.sub(r"\s+", "", cards) if cards else ""
