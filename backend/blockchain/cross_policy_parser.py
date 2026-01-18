"""Cross-policy parser workflow for unified hand history processing.

This module provides a unified interface for parsing hand histories from
multiple platforms (ACR/WPN and CoinPoker) with consistent normalization.

Key features:
1. Automatic platform detection
2. Unified action normalization
3. Consistent output format
4. Board variant analysis
5. Support for straddles, dead cards, and other special cases
"""

from __future__ import annotations

import re
from typing import Optional

from backend.blockchain.base_parser import (
    BoardCards,
    BoardVariant,
    NormalizedAction,
    NormalizedHandHistory,
    NormalizedPlayerAction,
    PlayerInfo,
    detect_board_variant,
    normalize_cards,
)
from backend.blockchain.betacr_parser import BetacrHand, parse_many as parse_betacr
from backend.blockchain.coinpoker_parser import ParsedHand, parse_many as parse_coinpoker


# Platform detection patterns
_ACR_PATTERN = re.compile(r"\bPoker\s+Hand\s*#", re.IGNORECASE)
_COINPOKER_PATTERN = re.compile(r"\bCoinPoker\s+Hand\s*#|\bHand\s*#\s*\d+.*₮", re.IGNORECASE)


def detect_platform(text: str) -> Optional[str]:
    """Detect poker platform from hand history text.
    
    Args:
        text: Raw hand history text
        
    Returns:
        Platform identifier ("ACR", "CoinPoker") or None if unknown
    """
    if _ACR_PATTERN.search(text):
        return "ACR"
    elif _COINPOKER_PATTERN.search(text):
        return "CoinPoker"
    return None


def normalize_betacr_actions(betacr_hand: BetacrHand) -> list[NormalizedPlayerAction]:
    """Normalize BETAcr/ACR actions to standard format.
    
    Maps ACR-specific action formats to normalized actions.
    """
    normalized = []
    
    for action_text in betacr_hand.actions:
        # Extract player name and action
        parts = action_text.split(":")
        if len(parts) < 2:
            continue
        
        player_name = parts[0].strip()
        action_part = parts[1].strip().lower()
        
        # Determine action type and amount
        action = None
        amount = None
        
        # Check for all-in first (most specific)
        if "all-in" in action_part or "all in" in action_part or "is all-in" in action_part:
            action = NormalizedAction.ALL_IN
            # Extract amount
            amount_match = re.search(r"(\$|€|₮)?([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(2).replace(",", ""))
        elif "fold" in action_part:
            action = NormalizedAction.FOLD
        elif "check" in action_part:
            action = NormalizedAction.CHECK
        elif "raise" in action_part:
            action = NormalizedAction.RAISE
            # Extract amount - look for "to X" pattern
            amount_match = re.search(r"to\s+(\$|€|₮)?([\d,.]+)", action_part)
            if not amount_match:
                amount_match = re.search(r"(\$|€|₮)?([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(2).replace(",", ""))
        elif "bet" in action_part:
            action = NormalizedAction.BET
            # Extract amount
            amount_match = re.search(r"(\$|€|₮)?([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(2).replace(",", ""))
        elif "call" in action_part:
            action = NormalizedAction.CALL
            # Extract amount
            amount_match = re.search(r"(\$|€|₮)?([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(2).replace(",", ""))
        elif "small blind" in action_part:
            action = NormalizedAction.POST_SB
            amount_match = re.search(r"(\$|€|₮)?([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(2).replace(",", ""))
        elif "big blind" in action_part:
            action = NormalizedAction.POST_BB
            amount_match = re.search(r"(\$|€|₮)?([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(2).replace(",", ""))
        elif "ante" in action_part:
            action = NormalizedAction.POST_ANTE
            amount_match = re.search(r"(\$|€|₮)?([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(2).replace(",", ""))
        elif "straddle" in action_part:
            action = NormalizedAction.POST_STRADDLE
            amount_match = re.search(r"(\$|€|₮)?([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(2).replace(",", ""))
        elif "collected" in action_part or "wins" in action_part:
            action = NormalizedAction.COLLECTED
            amount_match = re.search(r"(\$|€|₮)?([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(2).replace(",", ""))
        
        if action:
            normalized.append(
                NormalizedPlayerAction(
                    player_name=player_name,
                    action=action,
                    amount=amount,
                    raw_text=action_text,
                )
            )
    
    return normalized


def normalize_coinpoker_actions(coinpoker_hand: ParsedHand) -> list[NormalizedPlayerAction]:
    """Normalize CoinPoker actions to standard format.
    
    Maps CoinPoker-specific action formats to normalized actions.
    """
    normalized = []
    
    if not coinpoker_hand.actions:
        return normalized
    
    # CoinPoker actions are stored as a semicolon-separated string
    action_lines = coinpoker_hand.actions.split(";") if isinstance(coinpoker_hand.actions, str) else []
    
    for action_text in action_lines:
        action_text = action_text.strip()
        if not action_text:
            continue
        
        # Skip lines that are just section headers
        if "***" in action_text or action_text.upper() in ["HOLE CARDS", "FLOP", "TURN", "RIVER"]:
            continue
        
        # Try to parse player: action format
        if ":" not in action_text:
            continue
        
        parts = action_text.split(":", 1)
        if len(parts) < 2:
            continue
        
        player_name = parts[0].strip()
        action_part = parts[1].strip().lower()
        
        # Determine action type and amount
        action = None
        amount = None
        
        if "fold" in action_part:
            action = NormalizedAction.FOLD
        elif "check" in action_part:
            action = NormalizedAction.CHECK
        elif "all-in" in action_part or "all in" in action_part:
            action = NormalizedAction.ALL_IN
            amount_match = re.search(r"([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(1).replace(",", ""))
        elif "raise" in action_part:
            action = NormalizedAction.RAISE
            # Extract the final amount from "raises X to Y" format
            amount_match = re.search(r"to\s+([\d,.]+)", action_part)
            if not amount_match:
                amount_match = re.search(r"([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(1).replace(",", ""))
        elif "bet" in action_part:
            action = NormalizedAction.BET
            amount_match = re.search(r"([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(1).replace(",", ""))
        elif "call" in action_part:
            action = NormalizedAction.CALL
            amount_match = re.search(r"([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(1).replace(",", ""))
        elif "small blind" in action_part:
            action = NormalizedAction.POST_SB
            amount_match = re.search(r"([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(1).replace(",", ""))
        elif "big blind" in action_part:
            action = NormalizedAction.POST_BB
            amount_match = re.search(r"([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(1).replace(",", ""))
        elif "ante" in action_part:
            action = NormalizedAction.POST_ANTE
            amount_match = re.search(r"([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(1).replace(",", ""))
        elif "straddle" in action_part:
            action = NormalizedAction.POST_STRADDLE
            amount_match = re.search(r"([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(1).replace(",", ""))
        elif "wins" in action_part or "collected" in action_part:
            action = NormalizedAction.COLLECTED
            amount_match = re.search(r"([\d,.]+)", action_part)
            if amount_match:
                amount = float(amount_match.group(1).replace(",", ""))
        
        if action:
            normalized.append(
                NormalizedPlayerAction(
                    player_name=player_name,
                    action=action,
                    amount=amount,
                    raw_text=action_text,
                )
            )
    
    return normalized


def betacr_to_normalized(betacr_hand: BetacrHand) -> NormalizedHandHistory:
    """Convert BETAcr/ACR hand to normalized format."""
    # Parse board cards
    board_obj = None
    if betacr_hand.board:
        parts = betacr_hand.board.split()
        board_obj = BoardCards(
            flop=parts[0] if len(parts) > 0 else None,
            turn=parts[1] if len(parts) > 1 else None,
            river=parts[2] if len(parts) > 2 else None,
        )
        # Detect variant
        if board_obj.flop:
            cards = board_obj.cards_list
            board_obj.variant = detect_board_variant(cards)
    
    # Convert player stacks to PlayerInfo objects
    players = []
    if betacr_hand.player_stacks:
        for player_name, stack in betacr_hand.player_stacks.items():
            players.append(PlayerInfo(name=player_name, stack_size=stack))
    
    return NormalizedHandHistory(
        hand_id=betacr_hand.hand_id,
        platform="ACR",
        date_played=betacr_hand.date_played,
        game_type=betacr_hand.game_type,
        game_variant="NLHE",  # Default, could be enhanced
        stakes=betacr_hand.stakes,
        tournament_id=betacr_hand.tournament_id,
        buyin=betacr_hand.buyin,
        hero_name=betacr_hand.player_name,
        hole_cards=betacr_hand.hole_cards,
        players=players,
        board=board_obj,
        actions=normalize_betacr_actions(betacr_hand),
        won_amount=betacr_hand.won_amount,
        has_straddle=betacr_hand.has_straddle,
        raw_text=betacr_hand.raw_text,
        platform_specific={
            "game_type": betacr_hand.game_type,
        },
    )


def coinpoker_to_normalized(coinpoker_hand: ParsedHand) -> NormalizedHandHistory:
    """Convert CoinPoker hand to normalized format."""
    # Parse board cards
    board_obj = None
    if coinpoker_hand.board:
        parts = coinpoker_hand.board.split()
        board_obj = BoardCards(
            flop=parts[0] if len(parts) > 0 else None,
            turn=parts[1] if len(parts) > 1 else None,
            river=parts[2] if len(parts) > 2 else None,
        )
        # Detect variant
        if board_obj.flop:
            cards = board_obj.cards_list
            board_obj.variant = detect_board_variant(cards)
    
    # Convert player stacks to PlayerInfo objects
    players = []
    if coinpoker_hand.player_stacks:
        for player_name, stack in coinpoker_hand.player_stacks.items():
            players.append(PlayerInfo(name=player_name, stack_size=stack))
    
    return NormalizedHandHistory(
        hand_id=coinpoker_hand.hand_id or "unknown",
        platform="CoinPoker",
        date_played=coinpoker_hand.date_played,
        game_type="Cash Game" if "ante" not in (coinpoker_hand.stakes or "") else "Tournament",
        game_variant="NLHE",  # Default
        stakes=coinpoker_hand.stakes,
        hero_name=coinpoker_hand.player_name,
        hole_cards=coinpoker_hand.hole_cards,
        players=players,
        board=board_obj,
        actions=normalize_coinpoker_actions(coinpoker_hand),
        won_amount=coinpoker_hand.won_amount,
        has_straddle=coinpoker_hand.has_straddle,
        raw_text=coinpoker_hand.raw_text,
        platform_specific={
            "tx_hash": coinpoker_hand.tx_hash,
            "rng_phrase": coinpoker_hand.rng_phrase,
            "rng_combined_seed_hash": coinpoker_hand.rng_combined_seed_hash,
        },
    )


def parse_hand_history(text: str, platform: Optional[str] = None) -> list[NormalizedHandHistory]:
    """Parse hand history with automatic platform detection.
    
    This is the main entry point for cross-policy parsing.
    
    Args:
        text: Raw hand history text (single or multiple hands)
        platform: Optional platform override ("ACR" or "CoinPoker")
                 If None, platform will be auto-detected
    
    Returns:
        List of normalized hand histories
        
    Example:
        >>> text = "Poker Hand #12345: ..."
        >>> hands = parse_hand_history(text)
        >>> for hand in hands:
        ...     print(hand.hand_id, hand.platform)
        ...     stream = hand.to_chroma_stream()
    """
    # Auto-detect platform if not specified
    if platform is None:
        platform = detect_platform(text)
        if platform is None:
            raise ValueError("Could not detect platform from hand history text")
    
    # Parse using platform-specific parser
    if platform == "ACR":
        betacr_hands = parse_betacr(text)
        return [betacr_to_normalized(h) for h in betacr_hands]
    elif platform == "CoinPoker":
        coinpoker_hands = parse_coinpoker(text)
        return [coinpoker_to_normalized(h) for h in coinpoker_hands]
    else:
        raise ValueError(f"Unsupported platform: {platform}")


def parse_many_to_chroma_stream(text: str, platform: Optional[str] = None) -> list[dict]:
    """Parse multiple hands and convert to chroma stream format.
    
    This is a convenience function that combines parsing and conversion
    to the chroma stream format for downstream AI processing.
    
    Args:
        text: Raw hand history text
        platform: Optional platform override
        
    Returns:
        List of chroma stream dictionaries
    """
    hands = parse_hand_history(text, platform=platform)
    return [hand.to_chroma_stream() for hand in hands]
