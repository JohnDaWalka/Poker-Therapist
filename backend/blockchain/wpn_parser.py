"""WinningPokerNetwork (WPN) hand history parsing for BetACR, Americas Cardroom, etc.

WPN sites include:
- Americas Cardroom (ACR)
- BetACR
- Black Chip Poker
- True Poker

This parser extracts hand information from WPN hand history exports for:
- hand_id (Game No)
- date_played
- stakes
- hero cards
- board (flop, turn, river)
- actions
- pot and winnings
- player information
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# WPN uses #Game No : 123456789 format
_HAND_ID_RE = re.compile(r"#Game\s+No\s*:\s*(?P<id>\d+)", re.IGNORECASE)

# Split hands by Game No
_HAND_SPLIT_RE = re.compile(r"(?=#Game\s+No\s*:)", re.IGNORECASE)

# Stakes: "$0.50/$1", "€2/$4", etc.
_STAKES_RE = re.compile(
    r"(?P<s1>(?:\$|€|£)?\d+(?:\.\d+)?)[\s/]+(?P<s2>(?:\$|€|£)?\d+(?:\.\d+)?)"
)

# Tournament format: "Tournament #12345"
_TOURNAMENT_RE = re.compile(r"Tournament\s+#(?P<tid>\d+)", re.IGNORECASE)

# Date/time: "2024/01/01 20:30:00 UTC" or "2024-01-01 20:30:00"
_DT_RE = re.compile(
    r"(?P<dt>\d{4}[/-]\d{2}[/-]\d{2}\s+\d{2}:\d{2}:\d{2})(?:\s*(?P<tz>UTC|GMT|EST|PST|[A-Z]{2,5}))?"
)

# Dealt to PlayerName [cards]
_DEALT_RE = re.compile(
    r"Dealt\s+to\s+(?P<player>\S+)\s+\[(?P<cards>[2-9TJQKA][cdhs](?:\s+[2-9TJQKA][cdhs]){1,3})\]",
    re.IGNORECASE,
)

# FLOP, TURN, RIVER patterns
_FLOP_RE = re.compile(
    r"\*\*\*\s*FLOP\s*\*\*\*.*?\[(?P<flop>[2-9TJQKA][cdhs]\s+[2-9TJQKA][cdhs]\s+[2-9TJQKA][cdhs])\]",
    re.IGNORECASE,
)
_TURN_RE = re.compile(
    r"\*\*\*\s*TURN\s*\*\*\*.*?\[(?P<turn>[2-9TJQKA][cdhs])\]",
    re.IGNORECASE,
)
_RIVER_RE = re.compile(
    r"\*\*\*\s*RIVER\s*\*\*\*.*?\[(?P<river>[2-9TJQKA][cdhs])\]",
    re.IGNORECASE,
)

# Game variant: "Holdem(No Limit)", "Omaha(Pot Limit)", etc.
_GAME_VARIANT_RE = re.compile(
    r"(Holdem|Omaha|Seven Card Stud|Razz|HORSE)\s*\((?P<limit>[^)]+)\)",
    re.IGNORECASE,
)

# Player position at table: "Seat 3: PlayerName ($100)"
_SEAT_RE = re.compile(
    r"Seat\s+(?P<position>\d+):\s+(?P<player>\S+)\s+\(\$?(?P<stack>[\d.]+)\)",
    re.IGNORECASE,
)

# Winnings: "PlayerName wins $50" or "PlayerName collected $50 from pot"
_WON_RE = re.compile(
    r"(?P<player>\S+)\s+(?:wins?|collected)\s+\$?(?P<amt>[\d.]+)",
    re.IGNORECASE,
)

# Total pot from summary: "Total pot $50"
_POT_RE = re.compile(r"Total\s+pot\s+\$?(?P<pot>[\d.]+)", re.IGNORECASE)


def _parse_dt(dt_raw: str) -> Optional[datetime]:
    """Parse datetime from various WPN formats."""
    # Normalize separators
    dt_normalized = dt_raw.replace("/", "-")
    
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ):
        try:
            return datetime.strptime(dt_normalized, fmt)
        except Exception:
            continue
    return None


@dataclass(frozen=True)
class ParsedHand:
    """Parsed WPN hand history data."""
    hand_id: Optional[str]
    date_played: Optional[datetime]
    stakes: Optional[str]
    game_variant: Optional[str]
    tournament_id: Optional[str]
    player_name: Optional[str]
    position: Optional[str]
    hole_cards: Optional[str]
    board: Optional[str]
    actions: Optional[str]
    won_amount: Optional[float]
    pot_size: Optional[float]
    raw_text: str


def split_hands(text: str) -> list[str]:
    """Split multi-hand history text into individual hands."""
    hands = []
    last_start = None
    
    for m in _HAND_ID_RE.finditer(text):
        if last_start is not None:
            # Extract the previous hand
            hand_text = text[last_start:m.start()].strip()
            if hand_text:
                hands.append(hand_text)
        last_start = m.start()
    
    # Don't forget the last hand
    if last_start is not None:
        hand_text = text[last_start:].strip()
        if hand_text:
            hands.append(hand_text)
    
    # If no hands found, treat entire text as one chunk
    if not hands:
        stripped = text.strip()
        return [stripped] if stripped else []
    return hands


def parse_hand(text: str) -> ParsedHand:
    """Parse a single WPN hand history."""
    # Hand ID
    hand_id_m = _HAND_ID_RE.search(text)
    hand_id = hand_id_m.group("id") if hand_id_m else None

    # Stakes
    stakes_m = _STAKES_RE.search(text)
    stakes = f"{stakes_m.group('s1')}/{stakes_m.group('s2')}" if stakes_m else None

    # Tournament ID
    tournament_m = _TOURNAMENT_RE.search(text)
    tournament_id = tournament_m.group("tid") if tournament_m else None

    # Date/time
    dt_m = _DT_RE.search(text)
    date_played = _parse_dt(dt_m.group("dt")) if dt_m else None

    # Game variant
    variant_m = _GAME_VARIANT_RE.search(text)
    if variant_m:
        game_type = variant_m.group(1)
        limit_type = variant_m.group("limit")
        game_variant = f"{game_type} ({limit_type})"
    else:
        game_variant = None

    # Dealt cards (hero)
    dealt_m = _DEALT_RE.search(text)
    player_name = dealt_m.group("player") if dealt_m else None
    hole_cards = dealt_m.group("cards").replace(" ", "") if dealt_m else None

    # Find hero's position from seat information
    position = None
    if player_name:
        for seat_m in _SEAT_RE.finditer(text):
            if seat_m.group("player") == player_name:
                position = seat_m.group("position")
                break

    # Board cards
    flop_m = _FLOP_RE.search(text)
    turn_m = _TURN_RE.search(text)
    river_m = _RIVER_RE.search(text)

    board_parts: list[str] = []
    if flop_m:
        board_parts.append(flop_m.group("flop").replace(" ", ""))
    if turn_m:
        board_parts.append(turn_m.group("turn"))
    if river_m:
        board_parts.append(river_m.group("river"))
    board = " ".join(board_parts) if board_parts else None

    # Winnings
    won_amount = None
    if player_name:
        for won_m in _WON_RE.finditer(text):
            if won_m.group("player") == player_name:
                won_amount = float(won_m.group("amt"))
                break

    # Pot size
    pot_m = _POT_RE.search(text)
    pot_size = float(pot_m.group("pot")) if pot_m else None

    # Extract actions (best-effort)
    actions_lines: list[str] = []
    hole_idx = text.upper().find("*** HOLE CARDS ***")
    summary_idx = text.upper().find("*** SUMMARY ***")
    
    if hole_idx != -1:
        end_idx = summary_idx if summary_idx != -1 else len(text)
        seg = text[hole_idx:end_idx]
        actions_lines = [
            ln.strip()
            for ln in seg.splitlines()
            if ln.strip() and not ln.strip().startswith("***")
        ]
    actions = "; ".join(actions_lines) if actions_lines else None

    return ParsedHand(
        hand_id=hand_id,
        date_played=date_played,
        stakes=stakes,
        game_variant=game_variant,
        tournament_id=tournament_id,
        player_name=player_name,
        position=position,
        hole_cards=hole_cards,
        board=board,
        actions=actions,
        won_amount=won_amount,
        pot_size=pot_size,
        raw_text=text.strip(),
    )


def parse_many(text: str) -> list[ParsedHand]:
    """Parse multiple WPN hands from concatenated history text."""
    return [parse_hand(chunk) for chunk in split_hands(text) if chunk.strip()]
