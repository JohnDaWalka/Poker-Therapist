"""Winning Poker Network (WPN) / America's Cardroom (ACR) hand history parsing.

WPN includes America's Cardroom, BlackChip Poker, YaPoker, and other networks.
This parser aims to extract structure for Therapy Rex session review:
- hand_id
- date_played
- stakes
- hero cards / board
- actions
- pot/win amounts

WPN hand histories typically start with "***** Hand History for Game" and use
a consistent format across the network.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# Match hand header: ***** Hand History for Game 1234567890 *****
_HAND_SPLIT_RE = re.compile(r"(?=\*{5,}\s*Hand History for Game\s+\d+\s*\*{5,})")

# Extract hand ID from header
_HAND_ID_RE = re.compile(
    r"\*{5,}\s*Hand History for Game\s+(?P<id>\d+)\s*\*{5,}",
    re.IGNORECASE
)

# Extract stakes: $0.02/$0.05, 10/20, etc.
_STAKES_RE = re.compile(
    r"(?:\$|€)?(?P<sb>\d+(?:\.\d+)?)\s*/\s*(?:\$|€)?(?P<bb>\d+(?:\.\d+)?)\s+(?:NL|PL|Limit)?\s*(?:Texas\s*)?(?:Hold'?em|Omaha)?",
    re.IGNORECASE
)

# Tournament stakes format: Tournament #123456, 10/20
_TOURNEY_RE = re.compile(
    r"Tournament\s*#(?P<tourney_id>\d+).*?(?P<sb>\d+(?:\.\d+)?)\s*/\s*(?P<bb>\d+(?:\.\d+)?)",
    re.IGNORECASE
)

# Extract date/time - various formats seen in WPN exports
# Format: Thursday, January 10, 2026, 14:50:00
# Format: 2026-01-10 14:50:00
_DT_RE = re.compile(
    r"(?:(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+)?"
    r"(?:(?P<month_name>January|February|March|April|May|June|July|August|September|October|November|December)\s+(?P<day>\d{1,2}),?\s+(?P<year>\d{4}),?\s+(?P<time>\d{1,2}:\d{2}:\d{2}))"
    r"|"
    r"(?P<iso_dt>\d{4}[-/]\d{2}[-/]\d{2}\s+\d{2}:\d{2}:\d{2})",
    re.IGNORECASE
)

# Extract dealt cards: Dealt to Player [Ah Kh]
_DEALT_RE = re.compile(
    r"Dealt\s+to\s+(?P<player>[^\s\[]+)\s+\[(?P<cards>[2-9TJQKA][cdhs](?:\s+[2-9TJQKA][cdhs]){1,3})\]",
    re.IGNORECASE
)

# Board cards
_FLOP_RE = re.compile(
    r"\*\*\s*Dealing\s+Flop\s*\*\*\s+\[(?P<flop>[2-9TJQKA][cdhs]\s+[2-9TJQKA][cdhs]\s+[2-9TJQKA][cdhs])\]",
    re.IGNORECASE
)
_TURN_RE = re.compile(
    r"\*\*\s*Dealing\s+Turn\s*\*\*\s+\[(?P<turn>[2-9TJQKA][cdhs])\]",
    re.IGNORECASE
)
_RIVER_RE = re.compile(
    r"\*\*\s*Dealing\s+River\s*\*\*\s+\[(?P<river>[2-9TJQKA][cdhs])\]",
    re.IGNORECASE
)

# Player wins pot
_WON_RE = re.compile(
    r"(?P<player>\S+)\s+(?:wins|collected)\s+(?:\$|€)?(?P<amt>\d+(?:\.\d+)?)",
    re.IGNORECASE
)

# Total pot
_POT_RE = re.compile(
    r"Total\s+pot\s+(?:\$|€)?(?P<amt>\d+(?:\.\d+)?)",
    re.IGNORECASE
)

# Table name/info
_TABLE_RE = re.compile(
    r"Table\s+(?P<table_name>[^\s\(]+)(?:\s+\((?P<table_type>[^\)]+)\))?",
    re.IGNORECASE
)

# Seat info with position
_SEAT_RE = re.compile(
    r"Seat\s+(?P<seat>\d+):\s+(?P<player>\S+)",
    re.IGNORECASE
)


MONTH_MAP = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12
}


def _parse_dt(dt_match: re.Match) -> Optional[datetime]:
    """Parse datetime from WPN hand history."""
    if not dt_match:
        return None
    
    # Try ISO format first
    if dt_match.group('iso_dt'):
        dt_str = dt_match.group('iso_dt')
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
            try:
                return datetime.strptime(dt_str, fmt)
            except Exception:
                continue
    
    # Try named format: January 10, 2026, 14:50:00
    if dt_match.group('month_name'):
        try:
            month_name = dt_match.group('month_name').lower()
            month = MONTH_MAP.get(month_name)
            day = int(dt_match.group('day'))
            year = int(dt_match.group('year'))
            time_str = dt_match.group('time')
            
            # Parse time
            time_parts = time_str.split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            second = int(time_parts[2]) if len(time_parts) > 2 else 0
            
            return datetime(year, month, day, hour, minute, second)
        except Exception:
            pass
    
    return None


@dataclass(frozen=True)
class ParsedWpnHand:
    hand_id: Optional[str]
    date_played: Optional[datetime]
    stakes: Optional[str]
    table_name: Optional[str]
    player_name: Optional[str]
    seat_number: Optional[int]
    hole_cards: Optional[str]
    board: Optional[str]
    actions: Optional[str]
    won_amount: Optional[float]
    pot_size: Optional[float]
    raw_text: str


def split_hands(text: str) -> list[str]:
    """Split WPN hand history text into individual hands."""
    hands = []
    last_start = None
    
    for m in _HAND_ID_RE.finditer(text):
        if last_start is not None:
            hand_text = text[last_start:m.start()].strip()
            if hand_text:
                hands.append(hand_text)
        last_start = m.start()
    
    # Don't forget the last hand
    if last_start is not None:
        hand_text = text[last_start:].strip()
        if hand_text:
            hands.append(hand_text)
    
    # If no hands found, check if text contains valid hand header
    if not hands:
        stripped = text.strip()
        # Only return text if it contains a hand header
        if stripped and _HAND_ID_RE.search(stripped):
            return [stripped]
    return hands


def parse_hand(text: str) -> ParsedWpnHand:
    """Parse a single WPN hand history."""
    hand_id_m = _HAND_ID_RE.search(text)
    hand_id = hand_id_m.group("id") if hand_id_m else None
    
    # Parse stakes - try tournament format first, then cash game
    stakes = None
    tourney_m = _TOURNEY_RE.search(text)
    if tourney_m:
        stakes = f"{tourney_m.group('sb')}/{tourney_m.group('bb')}"
    else:
        stakes_m = _STAKES_RE.search(text)
        if stakes_m:
            stakes = f"{stakes_m.group('sb')}/{stakes_m.group('bb')}"
    
    # Parse date/time
    dt_m = _DT_RE.search(text)
    date_played = _parse_dt(dt_m) if dt_m else None
    
    # Parse table name
    table_m = _TABLE_RE.search(text)
    table_name = table_m.group('table_name') if table_m else None
    
    # Parse dealt cards (hero)
    dealt_m = _DEALT_RE.search(text)
    player_name = dealt_m.group("player") if dealt_m else None
    hole_cards = dealt_m.group("cards").replace(" ", "") if dealt_m else None
    
    # Find hero's seat number
    seat_number = None
    if player_name:
        for seat_m in _SEAT_RE.finditer(text):
            if seat_m.group('player') == player_name:
                seat_number = int(seat_m.group('seat'))
                break
    
    # Parse board cards
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
    
    # Parse pot size
    pot_m = _POT_RE.search(text)
    pot_size = float(pot_m.group("amt")) if pot_m else None
    
    # Parse won amount (for hero)
    won_amount = None
    if player_name:
        for won_m in _WON_RE.finditer(text):
            if won_m.group('player') == player_name:
                won_amount = float(won_m.group('amt'))
                break
    
    # Extract actions (best-effort)
    actions_lines: list[str] = []
    dealing_cards_idx = text.lower().find("** dealing down cards **")
    summary_idx = text.lower().find("*** summary ***")
    
    if dealing_cards_idx != -1:
        end_idx = summary_idx if summary_idx != -1 else len(text)
        seg = text[dealing_cards_idx:end_idx]
        actions_lines = [
            ln.strip()
            for ln in seg.splitlines()
            if ln.strip() and not ln.strip().startswith("**")
        ]
    actions = "; ".join(actions_lines) if actions_lines else None
    
    return ParsedWpnHand(
        hand_id=hand_id,
        date_played=date_played,
        stakes=stakes,
        table_name=table_name,
        player_name=player_name,
        seat_number=seat_number,
        hole_cards=hole_cards,
        board=board,
        actions=actions,
        won_amount=won_amount,
        pot_size=pot_size,
        raw_text=text.strip(),
    )


def parse_many(text: str) -> list[ParsedWpnHand]:
    """Parse multiple WPN hands from text."""
    return [parse_hand(chunk) for chunk in split_hands(text) if chunk.strip()]
