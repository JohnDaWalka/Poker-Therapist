"""BETAcr (Winning Poker Network) hand history parsing.

BETAcr/WPN uses a regular database (not blockchain verified).
Hand histories are organized in layered folders:
- tournaments
- Cash
- MTT's
- Sit n' Go's

This parser extracts structure for Therapy Rex session review:
- hand_id
- date_played
- stakes
- hero cards / board
- tournament info (if applicable)
- game type (Cash, Tournament, SNG, etc.)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# Split by occurrences of "Hand #" or "Poker Hand #".
_HAND_SPLIT_RE = re.compile(r"(?=\bPoker\s+Hand\s*#\s*\w+\b)")

# Hand ID can be alphanumeric
_HAND_ID_RE = re.compile(r"\bPoker\s+Hand\s*#\s*(?P<id>[\w-]+)\b")

# Stakes formats: "$0.50/$1.00", "€1/€2", "100/200", etc.
_STAKES_RE = re.compile(
    r"(?P<s1>(?:\$|€|₮)?\d+(?:\.\d+)?)[\s/]+(?P<s2>(?:\$|€|₮)?\d+(?:\.\d+)?)"
)

# Tournament info: "Tournament #12345"
_TOURNAMENT_RE = re.compile(r"Tournament\s*#\s*(?P<id>\d+)")

# Buy-in info: "$5+$0.50"
_BUYIN_RE = re.compile(r"(?P<buyin>\$\d+(?:\.\d+)?)\s*\+\s*(?P<fee>\$\d+(?:\.\d+)?)")

# Date formats: "2026-01-09 21:13:00 UTC", "2026/01/10 01:08:19 GMT"
_DT_RE = re.compile(
    r"(?P<dt>\d{4}[-/]\d{2}[-/]\d{2}[\sT]\d{2}:\d{2}:\d{2})(?:\s*(?P<tz>[A-Z]{2,5}))?"
)

# Dealt cards: "Dealt to Hero [Ah Kh]"
_DEALT_RE = re.compile(
    r"Dealt\s+to\s+(?P<player>[^\s]+)\s+\[(?P<cards>[2-9TJQKA][cdhs](?:\s+[2-9TJQKA][cdhs]){1,3})\]",
    re.IGNORECASE,
)

# Board cards
_FLOP_RE = re.compile(
    r"\*\*\*\s*FLOP\s*\*\*\*\s*\[(?P<cards>[^\]]+)\]",
    re.IGNORECASE,
)
_TURN_RE = re.compile(
    r"\*\*\*\s*TURN\s*\*\*\*\s*\[[^\]]*\]\s*\[(?P<card>[^\]]+)\]",
    re.IGNORECASE,
)
_RIVER_RE = re.compile(
    r"\*\*\*\s*RIVER\s*\*\*\*\s*\[[^\]]*\]\s*\[(?P<card>[^\]]+)\]",
    re.IGNORECASE,
)

# Game type indicators
_GAME_TYPE_RE = re.compile(
    r"\b(Cash\s+Game|Tournament|Sit\s*&\s*Go|SNG|MTT)\b",
    re.IGNORECASE,
)

# Win amount: "Hero collected $12.50 from pot" or "Hero collected 12.50 from pot"
_WIN_RE = re.compile(
    r"(?P<player>\w+)\s+(?:collected|wins?)\s+(?:\$|€|₮)?(?P<amount>[\d,.]+)",
    re.IGNORECASE,
)

# Player stack sizes: "Seat 1: Player1 ($100.00 in chips)" or "Seat 1: Player1 (1500 in chips)"
_SEAT_RE = re.compile(
    r"Seat\s+(?P<seat>\d+):\s+(?P<player>\S+)\s+\((?:\$|€|₮)?(?P<stack>[\d,.]+)\s+in\s+chips\)",
    re.IGNORECASE,
)

# Straddle detection: "Player: posts straddle $4"
_STRADDLE_RE = re.compile(
    r"(?P<player>\w+):\s+posts\s+straddle",
    re.IGNORECASE,
)


@dataclass
class BetacrHand:
    """Represents a single parsed BETAcr/WPN hand."""

    hand_id: str
    date_played: Optional[datetime]
    stakes: Optional[str]
    player_name: Optional[str]
    hole_cards: Optional[str]
    board: Optional[str]
    actions: list[str]
    won_amount: Optional[float]
    raw_text: str
    tournament_id: Optional[str] = None
    game_type: Optional[str] = None
    buyin: Optional[str] = None
    player_stacks: Optional[dict[str, float]] = None  # {player_name: stack_size}
    has_straddle: bool = False


def _normalize_cards(cards: str) -> str:
    """Strip spaces from card list: 'Ah Kh' -> 'AhKh'."""
    return re.sub(r"\s+", "", cards) if cards else ""


def _parse_datetime(text: str) -> Optional[datetime]:
    """Best-effort datetime parsing."""
    m = _DT_RE.search(text)
    if not m:
        return None
    dt_str = m.group("dt")
    # Try common formats
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ):
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    return None


def _detect_game_type(text: str) -> Optional[str]:
    """Detect game type from hand text."""
    # Check for SNG/Sit & Go first (more specific)
    if re.search(r"Sit\s*&\s*Go|SNG", text, re.IGNORECASE):
        return "SNG"
    
    m = _GAME_TYPE_RE.search(text)
    if not m:
        # Check for tournament in header
        if _TOURNAMENT_RE.search(text):
            return "Tournament"
        return None
    
    game_type = m.group(0).strip()
    return game_type.title()


def _extract_stakes(text: str) -> Optional[str]:
    """Extract stakes from hand text."""
    m = _STAKES_RE.search(text)
    if not m:
        return None
    s1 = m.group("s1")
    s2 = m.group("s2")
    return f"{s1}/{s2}"


def _extract_board(text: str) -> Optional[str]:
    """Combine flop, turn, river into single board string."""
    cards = []
    
    flop_m = _FLOP_RE.search(text)
    if flop_m:
        flop_cards = _normalize_cards(flop_m.group("cards"))
        cards.append(flop_cards)
    
    turn_m = _TURN_RE.search(text)
    if turn_m:
        turn_card = _normalize_cards(turn_m.group("card"))
        cards.append(turn_card)
    
    river_m = _RIVER_RE.search(text)
    if river_m:
        river_card = _normalize_cards(river_m.group("card"))
        cards.append(river_card)
    
    if not cards:
        return None
    
    return " ".join(cards)


def _extract_won_amount(text: str, player_name: Optional[str]) -> Optional[float]:
    """Extract won amount if player won the hand."""
    if not player_name:
        return None
    
    for m in _WIN_RE.finditer(text):
        if m.group("player").lower() == player_name.lower():
            amount_str = m.group("amount").replace(",", "")
            try:
                return float(amount_str)
            except ValueError:
                pass
    return None


def _extract_player_stacks(text: str) -> dict[str, float]:
    """Extract player stack sizes from seat information."""
    stacks = {}
    for m in _SEAT_RE.finditer(text):
        player = m.group("player")
        stack_str = m.group("stack").replace(",", "")
        try:
            stacks[player] = float(stack_str)
        except ValueError:
            pass
    return stacks


def _has_straddle(text: str) -> bool:
    """Check if hand includes a straddle."""
    return bool(_STRADDLE_RE.search(text))


def _extract_actions(text: str) -> list[str]:
    """Extract action lines from hand text."""
    actions = []
    # Look for lines with common action keywords
    # Note: We need to match full lines, not just partial words
    action_re = re.compile(
        r"^.+?:\s+(?:folds?|checks?|calls?[^:]*(?:and\s+is\s+all-in)?|raises?[^:]*(?:and\s+is\s+all-in)?|bets?|posts?\s+(?:small\s+blind|big\s+blind|ante|straddle)|collected|wins?)",
        re.IGNORECASE | re.MULTILINE,
    )
    for m in action_re.finditer(text):
        actions.append(m.group(0).strip())
    return actions


def parse_single(text: str) -> Optional[BetacrHand]:
    """Parse a single BETAcr/WPN hand from text.
    
    Returns None if the text doesn't look like a valid hand.
    """
    text = text.strip()
    if not text:
        return None
    
    # Extract hand ID
    hand_id_m = _HAND_ID_RE.search(text)
    if not hand_id_m:
        return None
    
    hand_id = hand_id_m.group("id")
    
    # Extract date
    date_played = _parse_datetime(text)
    
    # Extract stakes
    stakes = _extract_stakes(text)
    
    # Extract player name and hole cards
    dealt_m = _DEALT_RE.search(text)
    player_name = dealt_m.group("player") if dealt_m else None
    hole_cards = _normalize_cards(dealt_m.group("cards")) if dealt_m else None
    
    # Extract board
    board = _extract_board(text)
    
    # Extract tournament info
    tournament_m = _TOURNAMENT_RE.search(text)
    tournament_id = tournament_m.group("id") if tournament_m else None
    
    # Detect game type
    game_type = _detect_game_type(text)
    
    # Extract buy-in (for tournaments)
    buyin_m = _BUYIN_RE.search(text)
    buyin = f"{buyin_m.group('buyin')}+{buyin_m.group('fee')}" if buyin_m else None
    
    # Extract won amount
    won_amount = _extract_won_amount(text, player_name)
    
    # Extract actions
    actions = _extract_actions(text)
    
    # Extract player stacks
    player_stacks = _extract_player_stacks(text)
    
    # Check for straddle
    has_straddle = _has_straddle(text)
    
    return BetacrHand(
        hand_id=hand_id,
        date_played=date_played,
        stakes=stakes,
        player_name=player_name,
        hole_cards=hole_cards,
        board=board,
        actions=actions,
        won_amount=won_amount,
        raw_text=text,
        tournament_id=tournament_id,
        game_type=game_type,
        buyin=buyin,
        player_stacks=player_stacks,
        has_straddle=has_straddle,
    )


def parse_many(text: str) -> list[BetacrHand]:
    """Split and parse multiple BETAcr/WPN hands from text.
    
    Returns a list of successfully parsed hands.
    """
    chunks = _HAND_SPLIT_RE.split(text)
    hands = []
    for chunk in chunks:
        h = parse_single(chunk)
        if h:
            hands.append(h)
    return hands
