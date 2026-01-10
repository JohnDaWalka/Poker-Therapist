"""CoinPoker hand history parsing (best-effort).

CoinPoker exports vary by client/version and by tracker export settings.
This parser aims to extract enough structure for Therapy Rex session review:
- hand_id
- date_played (best-effort)
- stakes (best-effort)
- hero cards / board (best-effort)
- tx_hash if present (0x + 64 hex)

If your CoinPoker export looks different, paste one full hand block and we can
tighten patterns.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


_TX_HASH_RE = re.compile(r"0x[a-fA-F0-9]{64}")

# Split by occurrences of "Hand #" or "CoinPoker Hand #".
_HAND_SPLIT_RE = re.compile(r"(?=\b(?:CoinPoker\s+)?Hand\s*#\s*\d+\b)")

_HAND_ID_RE = re.compile(r"\b(?:CoinPoker\s+)?Hand\s*#\s*(?P<id>\d+)\b")
_STAKES_RE = re.compile(
    r"(?P<s1>(?:\$|€)?\d+(?:\.\d+)?)[\s/]*/[\s/]*(?P<s2>(?:\$|€)?\d+(?:\.\d+)?)"
)

# Tournament blind/ante format seen in CoinPoker exports:
# "(... No Limit (160/320 ante 40 play) 2026/01/10 01:08:19 GMT)"
_TOURNEY_BLINDS_RE = re.compile(
    r"\((?P<sb>\d+)\s*/\s*(?P<bb>\d+)\s+ante\s+(?P<ante>\d+)",
    re.IGNORECASE,
)

# Try to catch common ISO-like stamps: 2026-01-09 21:13:00 UTC
_DT_RE = re.compile(
    r"(?P<dt>\d{4}[-/]\d{2}[-/]\d{2}[ T]\d{2}:\d{2}:\d{2})(?:\s*(?P<tz>[A-Z]{2,5}))?"
)

_DEALT_RE = re.compile(
    r"Dealt\s+to\s+(?P<player>[^\s]+)\s+\[(?P<cards>[2-9TJQKA][cdhs](?:\s+[2-9TJQKA][cdhs]){1,3})\]",
    re.IGNORECASE,
)

_FLOP_RE = re.compile(
    r"(\*\*\*\s*FLOP\s*\*\*\*|\bFlop\b).*?\[(?P<flop>[2-9TJQKA][cdhs]\s+[2-9TJQKA][cdhs]\s+[2-9TJQKA][cdhs])\]",
    re.IGNORECASE,
)
_TURN_RE = re.compile(
    r"(\*\*\*\s*TURN\s*\*\*\*|\bTurn\b).*?\[(?P<turn>[2-9TJQKA][cdhs])\]",
    re.IGNORECASE,
)
_RIVER_RE = re.compile(
    r"(\*\*\*\s*RIVER\s*\*\*\*|\bRiver\b).*?\[(?P<river>[2-9TJQKA][cdhs])\]",
    re.IGNORECASE,
)

_WON_RE = re.compile(
    r"(wins|collected)[^\d]*(?P<amt>-?\d+(?:\.\d+)?)\s*(?:CP|chips|\$|€)?",
    re.IGNORECASE,
)

_RNG_PHRASE_RE = re.compile(r"^\s*phrase:\s*(?P<phrase>.+?)\s*$", re.IGNORECASE | re.MULTILINE)
_COMBINED_SEED_RE = re.compile(r"^\s*(?P<hex>[a-f0-9]{64})\s*\(combined\)\s*$", re.IGNORECASE | re.MULTILINE)


def _parse_dt(dt_raw: str) -> Optional[datetime]:
    # Store naive UTC (the rest of the app uses datetime.utcnow without tzinfo)
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%dT%H:%M:%S",
    ):
        try:
            return datetime.strptime(dt_raw, fmt)
        except Exception:
            continue
    return None


@dataclass(frozen=True)
class ParsedHand:
    hand_id: Optional[str]
    date_played: Optional[datetime]
    stakes: Optional[str]
    player_name: Optional[str]
    hole_cards: Optional[str]
    board: Optional[str]
    actions: Optional[str]
    won_amount: Optional[float]
    tx_hash: Optional[str]
    rng_phrase: Optional[str]
    rng_combined_seed_hash: Optional[str]
    raw_text: str


def split_hands(text: str) -> list[str]:
    chunks = [c.strip() for c in _HAND_SPLIT_RE.split(text) if c.strip()]
    # If split failed (single-hand or unknown format), treat entire text as one chunk.
    return chunks or [text.strip()]


def parse_hand(text: str) -> ParsedHand:
    hand_id_m = _HAND_ID_RE.search(text)
    hand_id = hand_id_m.group("id") if hand_id_m else None

    stakes_m = _STAKES_RE.search(text)
    stakes = None
    if stakes_m:
        stakes = f"{stakes_m.group('s1')}/{stakes_m.group('s2')}"
    else:
        tourney_m = _TOURNEY_BLINDS_RE.search(text)
        if tourney_m:
            stakes = f"{tourney_m.group('sb')}/{tourney_m.group('bb')} ante {tourney_m.group('ante')}"

    dt_m = _DT_RE.search(text)
    date_played = _parse_dt(dt_m.group("dt")) if dt_m else None

    dealt_m = _DEALT_RE.search(text)
    player_name = dealt_m.group("player") if dealt_m else None
    hole_cards = dealt_m.group("cards").replace(" ", "") if dealt_m else None

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

    won_m = _WON_RE.search(text)
    won_amount = float(won_m.group("amt")) if won_m else None

    tx_m = _TX_HASH_RE.search(text)
    tx_hash = tx_m.group(0) if tx_m else None

    rng_phrase_m = _RNG_PHRASE_RE.search(text)
    rng_phrase = rng_phrase_m.group("phrase").strip() if rng_phrase_m else None

    combined_m = _COMBINED_SEED_RE.search(text)
    rng_combined_seed_hash = combined_m.group("hex").lower() if combined_m else None

    # Actions: keep something human-readable; best-effort slice.
    actions_lines: list[str] = []
    hole_idx = text.upper().find("HOLE CARDS")
    end_idx = max(text.upper().find("SHOW DOWN"), text.upper().find("SUMMARY"))
    if hole_idx != -1 and end_idx != -1 and end_idx > hole_idx:
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
        player_name=player_name,
        hole_cards=hole_cards,
        board=board,
        actions=actions,
        won_amount=won_amount,
        tx_hash=tx_hash,
        rng_phrase=rng_phrase,
        rng_combined_seed_hash=rng_combined_seed_hash,
        raw_text=text.strip(),
    )


def parse_many(text: str) -> list[ParsedHand]:
    return [parse_hand(chunk) for chunk in split_hands(text) if chunk.strip()]
