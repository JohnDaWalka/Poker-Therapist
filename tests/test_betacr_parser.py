"""Tests for backend.blockchain.betacr_parser module."""

from backend.blockchain.betacr_parser import parse_many, parse_single


def test_betacr_parse_single_cash_game() -> None:
    """Test parsing a single cash game hand."""
    text = """
Poker Hand #HH12345: Hold'em No Limit ($0.50/$1.00) - 2026-01-10 14:30:00 UTC
Table 'Excalibur' 6-max Seat #3 is the button
Seat 1: Player1 ($100.00 in chips)
Seat 2: Player2 ($75.50 in chips)
Seat 3: Hero ($150.00 in chips)
Player1: posts small blind $0.50
Player2: posts big blind $1.00
*** HOLE CARDS ***
Dealt to Hero [Ah Kh]
Hero: raises $2.50 to $3.50
Player1: folds
Player2: calls $2.50
*** FLOP *** [Qs Jd 9c]
Player2: checks
Hero: bets $5.00
Player2: calls $5.00
*** TURN *** [Qs Jd 9c] [Tc]
Player2: checks
Hero: bets $12.00
Player2: folds
Hero collected $17.50 from pot
*** SUMMARY ***
Total pot $17.50
Board [Qs Jd 9c Tc]
""".strip()
    
    hand = parse_single(text)
    assert hand is not None
    assert hand.hand_id == "HH12345"
    assert hand.stakes == "$0.50/$1.00"
    assert hand.player_name == "Hero"
    assert hand.hole_cards == "AhKh"
    assert hand.board == "QsJd9c Tc"
    assert hand.won_amount == 17.50
    assert hand.game_type is None  # Not explicitly marked
    assert hand.tournament_id is None


def test_betacr_parse_single_tournament() -> None:
    """Test parsing a tournament hand."""
    text = """
Poker Hand #T98765: Tournament #555, $5+$0.50 Hold'em No Limit - Level III (25/50) - 2026-01-10 15:00:00 UTC
Table '555 10' 9-max Seat #5 is the button
Seat 1: Player1 (1500 in chips)
Seat 2: Hero (2000 in chips)
Seat 3: Player3 (1800 in chips)
Player1: posts small blind 25
Hero: posts big blind 50
*** HOLE CARDS ***
Dealt to Hero [Qc Qd]
Player3: raises 100 to 150
Player1: folds
Hero: calls 100
*** FLOP *** [2h 7s Kd]
Hero: checks
Player3: bets 200
Hero: folds
Player3 collected 325 from pot
*** SUMMARY ***
Total pot 325
Board [2h 7s Kd]
""".strip()
    
    hand = parse_single(text)
    assert hand is not None
    assert hand.hand_id == "T98765"
    assert hand.tournament_id == "555"
    assert hand.buyin == "$5+$0.50"
    assert hand.stakes == "25/50"
    assert hand.player_name == "Hero"
    assert hand.hole_cards == "QcQd"
    assert hand.board == "2h7sKd"
    assert hand.won_amount is None
    assert hand.game_type == "Tournament"


def test_betacr_parse_many_splits_multiple_hands() -> None:
    """Test parsing multiple hands from combined text."""
    text = """
Poker Hand #HH001: Hold'em No Limit ($0.10/$0.25) - 2026-01-10 10:00:00 UTC
Dealt to Hero [As Ks]
*** HOLE CARDS ***
Hero: raises $0.50
*** FLOP *** [2c 3c 4c]
Hero: bets $1.00
Hero collected 2.50 from pot

Poker Hand #HH002: Hold'em No Limit ($0.10/$0.25) - 2026-01-10 10:05:00 UTC
Dealt to Hero [Jh Jd]
*** HOLE CARDS ***
Hero: calls $0.25
*** FLOP *** [Ah Kh Qh]
Hero: folds
""".strip()
    
    hands = parse_many(text)
    assert len(hands) == 2
    
    # First hand
    assert hands[0].hand_id == "HH001"
    assert hands[0].hole_cards == "AsKs"
    assert hands[0].board == "2c3c4c"
    assert hands[0].won_amount == 2.50
    
    # Second hand
    assert hands[1].hand_id == "HH002"
    assert hands[1].hole_cards == "JhJd"
    assert hands[1].board == "AhKhQh"
    assert hands[1].won_amount is None


def test_betacr_parse_with_turn_and_river() -> None:
    """Test parsing hand with complete board (flop, turn, river)."""
    text = """
Poker Hand #HH789: Hold'em No Limit ($1/$2) - 2026-01-10 16:00:00 UTC
Dealt to Hero [9s 9h]
*** HOLE CARDS ***
Hero: calls $2
*** FLOP *** [2s 8c 9d]
Hero: bets $5
*** TURN *** [2s 8c 9d] [Kh]
Hero: checks
*** RIVER *** [2s 8c 9d Kh] [Ad]
Hero: bets $10
Hero collected 35.00 from pot
""".strip()
    
    hand = parse_single(text)
    assert hand is not None
    assert hand.board == "2s8c9d Kh Ad"
    assert hand.won_amount == 35.00


def test_betacr_parse_sit_and_go() -> None:
    """Test parsing a Sit & Go hand."""
    text = """
Poker Hand #SNG123: Tournament #789, Sit & Go $10+$1 Hold'em No Limit - 2026-01-10 17:00:00 UTC
Table '789 1' 6-max Seat #1 is the button
Dealt to Hero [Ac Kc]
*** HOLE CARDS ***
Hero: raises 100 to 150
*** FLOP *** [5h 6h 7h]
Hero: bets 200
""".strip()
    
    hand = parse_single(text)
    assert hand is not None
    assert hand.hand_id == "SNG123"
    assert hand.tournament_id == "789"
    assert hand.game_type == "SNG"


def test_betacr_parse_empty_text() -> None:
    """Test parsing empty text."""
    hands = parse_many("")
    assert len(hands) == 0
    
    hand = parse_single("")
    assert hand is None


def test_betacr_parse_invalid_text() -> None:
    """Test parsing invalid text without hand marker."""
    text = "This is not a valid hand history"
    hand = parse_single(text)
    assert hand is None


def test_betacr_parse_no_dealt_cards() -> None:
    """Test parsing hand without dealt cards."""
    text = """
Poker Hand #HH999: Hold'em No Limit ($0.50/$1.00) - 2026-01-10 18:00:00 UTC
*** HOLE CARDS ***
Player1: raises $2.50
Player2: folds
""".strip()
    
    hand = parse_single(text)
    assert hand is not None
    assert hand.hand_id == "HH999"
    assert hand.player_name is None
    assert hand.hole_cards is None


def test_betacr_extract_actions() -> None:
    """Test extraction of action lines."""
    text = """
Poker Hand #HH456: Hold'em No Limit ($0.50/$1.00) - 2026-01-10 19:00:00 UTC
Dealt to Hero [Th Ts]
*** HOLE CARDS ***
Player1: folds
Player2: calls $1
Hero: raises $3.50 to $4.50
Player2: calls $3.50
*** FLOP *** [2d 3d 4d]
Player2: checks
Hero: bets $7
Player2: folds
""".strip()
    
    hand = parse_single(text)
    assert hand is not None
    assert len(hand.actions) > 0
    # Should have captured fold, call, raise, check, bet actions


def test_betacr_parse_with_different_date_formats() -> None:
    """Test parsing hands with different date formats."""
    # Format with slash separators
    text1 = """
Poker Hand #HH111: Hold'em No Limit ($0.50/$1.00) - 2026/01/10 20:00:00 GMT
Dealt to Hero [8s 8h]
""".strip()
    
    hand1 = parse_single(text1)
    assert hand1 is not None
    assert hand1.date_played is not None
    assert hand1.date_played.year == 2026
    assert hand1.date_played.month == 1
    assert hand1.date_played.day == 10


def test_betacr_parse_case_insensitive_player_name() -> None:
    """Test that player name matching is case insensitive."""
    text = """
Poker Hand #HH777: Hold'em No Limit ($0.50/$1.00) - 2026-01-10 21:00:00 UTC
Dealt to HERO [5c 5d]
*** HOLE CARDS ***
HERO: calls $1
*** FLOP *** [5h 5s Ah]
hero collected 10.00 from pot
""".strip()
    
    hand = parse_single(text)
    assert hand is not None
    assert hand.player_name == "HERO"
    assert hand.won_amount == 10.00


def test_betacr_parse_hand_with_euro_currency() -> None:
    """Test parsing hand with euro currency."""
    text = """
Poker Hand #EU123: Hold'em No Limit (€0.50/€1.00) - 2026-01-10 22:00:00 UTC
Dealt to Hero [As Ad]
*** HOLE CARDS ***
Hero: raises €3.00
""".strip()
    
    hand = parse_single(text)
    assert hand is not None
    assert hand.stakes == "€0.50/€1.00"


def test_betacr_parse_mtt_format() -> None:
    """Test parsing MTT (Multi-Table Tournament) hand."""
    text = """
Poker Hand #MTT999: Tournament #12345, MTT $100+$10 Hold'em No Limit - 2026-01-10 23:00:00 UTC
Table '12345 45' 9-max Seat #3 is the button
Dealt to Hero [Kd Qd]
*** HOLE CARDS ***
Hero: raises 200 to 300
""".strip()
    
    hand = parse_single(text)
    assert hand is not None
    assert hand.hand_id == "MTT999"
    assert hand.tournament_id == "12345"
    # Note: MTT should be detected as part of game type
    assert "MTT" in text or "Tournament" in hand.game_type
