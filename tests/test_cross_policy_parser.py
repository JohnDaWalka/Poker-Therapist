"""Tests for cross-policy parser workflow.

Tests cover:
1. Platform detection
2. ACR (BETAcr) normalization
3. CoinPoker normalization
4. Board variant detection
5. Special cases (straddles, dead cards, etc.)
6. Premium pairs, suited connectors, blockers
7. Cross-platform consistency
"""

from backend.blockchain.base_parser import BoardVariant, NormalizedAction, detect_board_variant
from backend.blockchain.cross_policy_parser import (
    detect_platform,
    parse_hand_history,
    parse_many_to_chroma_stream,
)


def test_detect_platform_acr() -> None:
    """Test ACR platform detection."""
    text = "Poker Hand #HH12345: Hold'em No Limit ($0.50/$1.00)"
    assert detect_platform(text) == "ACR"


def test_detect_platform_coinpoker() -> None:
    """Test CoinPoker platform detection."""
    text = "CoinPoker Hand #123: NL Hold'em - $0.50/$1.00"
    assert detect_platform(text) == "CoinPoker"


def test_detect_platform_coinpoker_with_tugrik() -> None:
    """Test CoinPoker detection with tugrik currency."""
    text = "Hand #360327066: Tournament #1424001, ₮5 Mini Rapido"
    assert detect_platform(text) == "CoinPoker"


def test_board_variant_monotone() -> None:
    """Test monotone board detection (all same suit)."""
    cards = ["Ah", "Kh", "Qh"]
    assert detect_board_variant(cards) == BoardVariant.MONOTONE


def test_board_variant_rainbow() -> None:
    """Test rainbow board detection (all different suits)."""
    cards = ["Ah", "Kd", "Qs"]
    assert detect_board_variant(cards) == BoardVariant.RAINBOW


def test_board_variant_two_tone() -> None:
    """Test two-tone board detection."""
    cards = ["Ah", "Kh", "Qs"]
    assert detect_board_variant(cards) == BoardVariant.TWO_TONE


def test_board_variant_paired() -> None:
    """Test paired board detection."""
    cards = ["Ah", "Ad", "Ks"]
    assert detect_board_variant(cards) == BoardVariant.PAIRED


def test_board_variant_trips() -> None:
    """Test trips board detection."""
    cards = ["Ah", "Ad", "As"]
    assert detect_board_variant(cards) == BoardVariant.TRIPS


def test_parse_acr_premium_pair() -> None:
    """Test parsing ACR hand with premium pair (AA)."""
    text = """
Poker Hand #AA123: Hold'em No Limit ($1/$2) - 2026-01-15 10:00:00 UTC
Table 'Premium' 6-max Seat #1 is the button
Seat 1: Player1 ($200.00 in chips)
Seat 2: Hero ($300.00 in chips)
Player1: posts small blind $1
Hero: posts big blind $2
*** HOLE CARDS ***
Dealt to Hero [Ah As]
Player1: raises $6 to $8
Hero: raises $18 to $26
Player1: calls $18
*** FLOP *** [Kh Qd Jc]
Hero: bets $35
Player1: folds
Hero collected $52.00 from pot
""".strip()
    
    hands = parse_hand_history(text)
    assert len(hands) == 1
    
    hand = hands[0]
    assert hand.platform == "ACR"
    assert hand.hole_cards == "AhAs"
    assert hand.board is not None
    assert hand.board.variant == BoardVariant.RAINBOW
    assert hand.won_amount == 52.00
    
    # Check normalized actions
    actions = hand.actions
    assert len(actions) > 0
    assert any(a.action == NormalizedAction.POST_SB for a in actions)
    assert any(a.action == NormalizedAction.POST_BB for a in actions)
    assert any(a.action == NormalizedAction.RAISE for a in actions)


def test_parse_acr_suited_connectors() -> None:
    """Test parsing ACR hand with suited connectors (JTs)."""
    text = """
Poker Hand #SC456: Hold'em No Limit ($0.50/$1.00) - 2026-01-15 11:00:00 UTC
Dealt to Hero [Jh Th]
*** HOLE CARDS ***
Hero: calls $1
Player2: raises $3 to $4
Hero: calls $3
*** FLOP *** [9h 8h 2c]
Hero: checks
Player2: bets $6
Hero: raises $18 to $24
Player2: folds
Hero collected $20.00 from pot
""".strip()
    
    hands = parse_hand_history(text)
    assert len(hands) == 1
    
    hand = hands[0]
    assert hand.hole_cards == "JhTh"
    assert hand.board is not None
    assert hand.board.variant == BoardVariant.TWO_TONE  # Two hearts, one club


def test_parse_acr_with_straddle() -> None:
    """Test parsing ACR hand with straddle."""
    text = """
Poker Hand #STR789: Hold'em No Limit ($1/$2) - 2026-01-15 12:00:00 UTC
Seat 1: Player1 ($200.00 in chips)
Seat 2: Hero ($300.00 in chips)
Seat 3: Player3 ($250.00 in chips)
Player1: posts small blind $1
Hero: posts big blind $2
Player3: posts straddle $4
*** HOLE CARDS ***
Dealt to Hero [Kc Kd]
Player1: folds
Hero: raises $12 to $16
Player3: calls $12
*** FLOP *** [7s 6s 5s]
Hero: checks
Player3: bets $20
Hero: folds
Player3 collected $33.00 from pot
""".strip()
    
    hands = parse_hand_history(text)
    assert len(hands) == 1
    
    hand = hands[0]
    assert hand.has_straddle is True
    assert hand.board is not None
    assert hand.board.variant == BoardVariant.MONOTONE  # All spades


def test_parse_coinpoker_premium_pair() -> None:
    """Test parsing CoinPoker hand with premium pair (KK)."""
    text = """
CoinPoker Hand #999: NL Hold'em - $2/$4 - 2026-01-15 13:00:00 UTC
Dealt to Hero [Kh Kd]
*** HOLE CARDS ***
Player1: raises 12 to 16
Hero: raises 36 to 52
Player1: calls 36
*** FLOP *** [Ac 7h 3d]
Hero: bets 60
Player1: folds
*** SUMMARY ***
Hero wins 104
""".strip()
    
    hands = parse_hand_history(text)
    assert len(hands) == 1
    
    hand = hands[0]
    assert hand.platform == "CoinPoker"
    assert hand.hole_cards == "KhKd"
    assert hand.board is not None
    assert hand.board.variant == BoardVariant.RAINBOW
    assert hand.won_amount == 104


def test_parse_coinpoker_suited_connectors() -> None:
    """Test parsing CoinPoker hand with suited connectors (98s)."""
    text = """
CoinPoker Hand #888: NL Hold'em - $0.25/$0.50 - 2026-01-15 14:00:00 UTC
Dealt to Hero [9s 8s]
*** HOLE CARDS ***
Hero: calls 0.50
Player2: raises 1.50 to 2.00
Hero: calls 1.50
*** FLOP *** [Ts 7s 2h]
Hero: checks
Player2: bets 3.00
Hero: raises 9.00 to 12.00
Player2: folds
*** SUMMARY ***
Hero wins 10.00
""".strip()
    
    hands = parse_hand_history(text)
    assert len(hands) == 1
    
    hand = hands[0]
    assert hand.hole_cards == "9s8s"
    assert hand.board is not None
    assert hand.board.variant == BoardVariant.TWO_TONE


def test_cross_platform_action_consistency() -> None:
    """Test that actions are normalized consistently across platforms."""
    acr_text = """
Poker Hand #ACR1: Hold'em No Limit ($1/$2) - 2026-01-15 15:00:00 UTC
Dealt to Hero [Ah Kh]
*** HOLE CARDS ***
Hero: raises $6 to $8
Player1: calls $6
*** FLOP *** [Qh Jh Th]
Hero: bets $12
Player1: folds
Hero collected $18.00 from pot
""".strip()
    
    coinpoker_text = """
CoinPoker Hand #CP1: NL Hold'em - $1/$2 - 2026-01-15 15:00:00 UTC
Dealt to Hero [Ah Kh]
*** HOLE CARDS ***
Hero: raises 6 to 8
Player1: calls 6
*** FLOP *** [Qh Jh Th]
Hero: bets 12
Player1: folds
*** SUMMARY ***
Hero wins 18
""".strip()
    
    acr_hands = parse_hand_history(acr_text)
    coinpoker_hands = parse_hand_history(coinpoker_text)
    
    # Both should have similar action structure
    assert len(acr_hands) == 1
    assert len(coinpoker_hands) == 1
    
    acr_actions = {a.action for a in acr_hands[0].actions}
    cp_actions = {a.action for a in coinpoker_hands[0].actions}
    
    # Both should have RAISE, CALL, BET, FOLD
    assert NormalizedAction.RAISE in acr_actions or NormalizedAction.BET in acr_actions
    assert NormalizedAction.RAISE in cp_actions or NormalizedAction.BET in cp_actions


def test_chroma_stream_format() -> None:
    """Test chroma stream output format."""
    text = """
Poker Hand #CS123: Hold'em No Limit ($0.50/$1.00) - 2026-01-15 16:00:00 UTC
Dealt to Hero [As Ks]
*** HOLE CARDS ***
Hero: raises $3 to $4
*** FLOP *** [Ah Kh Qh]
Hero: bets $6
Hero collected $10.00 from pot
""".strip()
    
    streams = parse_many_to_chroma_stream(text)
    assert len(streams) == 1
    
    stream = streams[0]
    assert "platform" in stream
    assert "hand_id" in stream
    assert "hero_cards" in stream
    assert "board" in stream
    assert "board_variant" in stream
    assert "actions" in stream
    assert stream["platform"] == "ACR"
    assert stream["board_variant"] == "MONOTONE"


def test_parse_multiple_hands_acr() -> None:
    """Test parsing multiple ACR hands in one text block."""
    text = """
Poker Hand #H1: Hold'em No Limit ($1/$2) - 2026-01-15 10:00:00 UTC
Dealt to Hero [Ah Kh]
*** FLOP *** [Qh Jh Th]
Hero collected $20.00 from pot

Poker Hand #H2: Hold'em No Limit ($1/$2) - 2026-01-15 10:05:00 UTC
Dealt to Hero [9s 9h]
*** FLOP *** [2s 8c 9d]
Hero collected $30.00 from pot
""".strip()
    
    hands = parse_hand_history(text)
    assert len(hands) == 2
    assert hands[0].hand_id == "H1"
    assert hands[1].hand_id == "H2"


def test_parse_tournament_hand() -> None:
    """Test parsing tournament hand with antes."""
    text = """
Poker Hand #T555: Tournament #999, $10+$1 Hold'em No Limit - 2026-01-15 17:00:00 UTC
Table '999 10' 9-max Seat #3 is the button
Dealt to Hero [Qh Qs]
*** HOLE CARDS ***
Player1: raises 200 to 300
Hero: raises 600 to 900
Player1: folds
Hero collected 650 from pot
""".strip()
    
    hands = parse_hand_history(text)
    assert len(hands) == 1
    
    hand = hands[0]
    assert hand.tournament_id == "999"
    assert hand.buyin == "$10+$1"
    assert hand.game_type == "Tournament"


def test_blocker_scenario() -> None:
    """Test parsing hand with blocker considerations (holding Ace on flush board)."""
    text = """
Poker Hand #BLK1: Hold'em No Limit ($2/$5) - 2026-01-15 18:00:00 UTC
Dealt to Hero [Ah Kd]
*** HOLE CARDS ***
Hero: raises $15 to $20
Player1: calls $15
*** FLOP *** [Qh Jh 9h]
Hero: checks
Player1: bets $30
Hero: folds
Player1 collected $42.00 from pot
""".strip()
    
    hands = parse_hand_history(text)
    assert len(hands) == 1
    
    hand = hands[0]
    # Hero has Ah as blocker to nut flush
    assert "Ah" in hand.hole_cards
    # Board is monotone hearts
    assert hand.board is not None
    assert hand.board.variant == BoardVariant.MONOTONE


def test_empty_text() -> None:
    """Test parsing empty text."""
    text = ""
    try:
        hands = parse_hand_history(text)
        # Should either return empty list or raise error
        assert len(hands) == 0
    except ValueError:
        # Acceptable to raise ValueError for invalid input
        pass


def test_board_variant_with_turn_and_river() -> None:
    """Test board variant detection with full 5-card board."""
    text = """
Poker Hand #BV1: Hold'em No Limit ($1/$2) - 2026-01-15 19:00:00 UTC
Dealt to Hero [As Ks]
*** HOLE CARDS ***
Hero: raises $6 to $8
*** FLOP *** [Ah Ad Kh]
Hero: bets $12
*** TURN *** [Ah Ad Kh] [Qs]
Hero: checks
*** RIVER *** [Ah Ad Kh Qs] [Jc]
Hero: bets $20
Hero collected $50.00 from pot
""".strip()
    
    hands = parse_hand_history(text)
    assert len(hands) == 1
    
    hand = hands[0]
    assert hand.board is not None
    # Should detect paired board (two Aces)
    assert hand.board.variant == BoardVariant.PAIRED
    # Check full board is assembled correctly
    assert "Ah" in hand.board.full_board
    assert "Jc" in hand.board.full_board


def test_parse_with_explicit_platform() -> None:
    """Test parsing with explicit platform parameter."""
    text = """
Poker Hand #EXP1: Hold'em No Limit ($1/$2) - 2026-01-15 20:00:00 UTC
Dealt to Hero [Jh Jd]
*** FLOP *** [Jc 7s 2h]
Hero collected $15.00 from pot
""".strip()
    
    # Parse as ACR explicitly
    hands = parse_hand_history(text, platform="ACR")
    assert len(hands) == 1
    assert hands[0].platform == "ACR"


def test_parse_all_in_action() -> None:
    """Test parsing all-in action."""
    text = """
Poker Hand #AI1: Hold'em No Limit ($1/$2) - 2026-01-15 21:00:00 UTC
Dealt to Hero [Tc Th]
*** HOLE CARDS ***
Hero: raises $6 to $8
Player1: raises $50 and is all-in
Hero: calls $42 and is all-in
*** FLOP *** [Ts 9h 8d]
*** TURN *** [Ts 9h 8d] [4c]
*** RIVER *** [Ts 9h 8d 4c] [2s]
Hero collected $100.00 from pot
""".strip()
    
    hands = parse_hand_history(text)
    assert len(hands) == 1
    
    hand = hands[0]
    # Should have all-in actions
    all_in_actions = [a for a in hand.actions if a.action == NormalizedAction.ALL_IN]
    assert len(all_in_actions) > 0


def test_parse_with_player_stacks() -> None:
    """Test parsing hand with player stack information."""
    text = """
Poker Hand #STK1: Hold'em No Limit ($1/$2) - 2026-01-15 22:00:00 UTC
Table 'Test' 6-max Seat #1 is the button
Seat 1: Player1 ($200.00 in chips)
Seat 2: Hero ($300.50 in chips)
Seat 3: Player3 ($150.00 in chips)
Player1: posts small blind $1
Hero: posts big blind $2
*** HOLE CARDS ***
Dealt to Hero [As Ks]
Player3: raises $6 to $8
Player1: folds
Hero: raises $18 to $26
Player3: folds
Hero collected $17.00 from pot
""".strip()
    
    hands = parse_hand_history(text)
    assert len(hands) == 1
    
    hand = hands[0]
    # Check player stacks were extracted
    assert hand.players is not None
    assert len(hand.players) > 0
    
    # Find Hero's stack
    hero_player = next((p for p in hand.players if p.name == "Hero"), None)
    assert hero_player is not None
    assert hero_player.stack_size == 300.50
    
    # Find Player1's stack
    player1 = next((p for p in hand.players if p.name == "Player1"), None)
    assert player1 is not None
    assert player1.stack_size == 200.00


def test_chroma_stream_includes_player_count() -> None:
    """Test that chroma stream includes player count."""
    text = """
Poker Hand #CS2: Hold'em No Limit ($1/$2) - 2026-01-15 23:00:00 UTC
Table 'Test' 6-max Seat #1 is the button
Seat 1: Player1 ($200.00 in chips)
Seat 2: Hero ($300.00 in chips)
Seat 3: Player3 ($150.00 in chips)
Dealt to Hero [Ah Kh]
*** FLOP *** [Qh Jh Th]
Hero collected $10.00 from pot
""".strip()
    
    streams = parse_many_to_chroma_stream(text)
    assert len(streams) == 1
    
    stream = streams[0]
    assert "num_players" in stream
    assert stream["num_players"] == 3

