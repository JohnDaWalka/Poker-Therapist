"""Tests for WPN/ACR hand history parser."""

from datetime import datetime
from backend.blockchain.wpn_parser import parse_hand, parse_many


def test_wpn_basic_hand_parsing() -> None:
    """Test basic WPN hand history parsing."""
    text = """
***** Hand History for Game 1234567890 *****
$0.02/$0.05 NL Texas Hold'em - Thursday, January 10, 2026, 14:50:00
Table ACR - 6 Max (Real Money)
Seat 1: Player1 ($5.23)
Seat 2: Player2 ($4.91)
Seat 3: Player3 ($3.45)
Seat 4: Hero ($6.75)
Player1 posts small blind [$0.02]
Player2 posts big blind [$0.05]
** Dealing down cards **
Dealt to Hero [Ah Kh]
Player3 folds
Hero raises [$0.15]
Player1 calls [$0.13]
Player2 folds
** Dealing Flop ** [5h 2c Qd]
Player1 checks
Hero bets [$0.25]
Player1 folds
Hero wins $0.40
*** Summary ***
Total pot $0.40
Hero collected $0.40
""".strip()
    
    hand = parse_hand(text)
    
    assert hand.hand_id == "1234567890"
    assert hand.stakes == "0.02/0.05"
    assert hand.player_name == "Hero"
    assert hand.seat_number == 4
    assert hand.hole_cards == "AhKh"
    assert hand.board == "5h2cQd"
    assert hand.won_amount == 0.40
    assert hand.pot_size == 0.40
    assert hand.table_name == "ACR"
    assert hand.date_played is not None
    assert hand.date_played.year == 2026
    assert hand.date_played.month == 1
    assert hand.date_played.day == 10


def test_wpn_parse_many_splits_correctly() -> None:
    """Test splitting multiple WPN hands."""
    text = """
***** Hand History for Game 1111111111 *****
$0.02/$0.05 NL Texas Hold'em - Thursday, January 10, 2026, 14:50:00
Table ACR - 6 Max (Real Money)
Dealt to Hero [Ah Kh]
Hero wins $0.40

***** Hand History for Game 2222222222 *****
$0.05/$0.10 NL Texas Hold'em - Thursday, January 10, 2026, 15:00:00
Table BlackChip (Real Money)
Dealt to Hero [2c 2d]
Hero wins $1.20
""".strip()
    
    hands = parse_many(text)
    assert len(hands) == 2
    
    # First hand
    assert hands[0].hand_id == "1111111111"
    assert hands[0].stakes == "0.02/0.05"
    assert hands[0].hole_cards == "AhKh"
    assert hands[0].table_name == "ACR"
    
    # Second hand
    assert hands[1].hand_id == "2222222222"
    assert hands[1].stakes == "0.05/0.10"
    assert hands[1].hole_cards == "2c2d"
    assert hands[1].table_name == "BlackChip"


def test_wpn_board_cards_parsing() -> None:
    """Test parsing flop, turn, and river cards."""
    text = """
***** Hand History for Game 9999999999 *****
$0.10/$0.25 NL Texas Hold'em - Thursday, January 10, 2026, 16:00:00
Table Test (Real Money)
Dealt to Hero [As Ks]
** Dealing Flop ** [Kd Kc 7h]
** Dealing Turn ** [Js]
** Dealing River ** [2d]
Hero wins $5.50
""".strip()
    
    hand = parse_hand(text)
    
    assert hand.hand_id == "9999999999"
    assert hand.hole_cards == "AsKs"
    assert hand.board == "KdKc7h Js 2d"
    assert hand.won_amount == 5.50


def test_wpn_tournament_format() -> None:
    """Test parsing tournament hand history."""
    text = """
***** Hand History for Game 5555555555 *****
Tournament #123456, 10/20 NL Texas Hold'em - Thursday, January 10, 2026, 17:00:00
Table Tournament (Tournament)
Seat 1: Hero ($1500)
Seat 2: Villain ($1500)
Dealt to Hero [Qh Qd]
Hero raises [60]
Villain calls [60]
** Dealing Flop ** [Qc 9s 2h]
Hero wins 120
*** Summary ***
Total pot 120
""".strip()
    
    hand = parse_hand(text)
    
    assert hand.hand_id == "5555555555"
    assert hand.stakes == "10/20"
    assert hand.hole_cards == "QhQd"
    assert hand.board == "Qc9s2h"
    assert hand.pot_size == 120.0


def test_wpn_iso_datetime_format() -> None:
    """Test parsing ISO datetime format."""
    text = """
***** Hand History for Game 7777777777 *****
$1/$2 NL Texas Hold'em - 2026-01-10 18:30:00
Table Test (Real Money)
Dealt to Hero [Ac Kc]
Hero wins $10.00
""".strip()
    
    hand = parse_hand(text)
    
    assert hand.hand_id == "7777777777"
    assert hand.stakes == "1/2"
    assert hand.date_played == datetime(2026, 1, 10, 18, 30, 0)
    assert hand.hole_cards == "AcKc"


def test_wpn_no_board_cards() -> None:
    """Test parsing hand with no board cards (preflop fold)."""
    text = """
***** Hand History for Game 8888888888 *****
$0.05/$0.10 NL Texas Hold'em - Thursday, January 10, 2026, 19:00:00
Table Fast (Real Money)
Seat 1: Hero ($10.00)
Seat 2: Villain ($10.00)
Villain posts small blind [$0.05]
Hero posts big blind [$0.10]
** Dealing down cards **
Dealt to Hero [7c 2d]
Villain raises [$0.30]
Hero folds
Villain wins $0.20
""".strip()
    
    hand = parse_hand(text)
    
    assert hand.hand_id == "8888888888"
    assert hand.hole_cards == "7c2d"
    assert hand.board is None  # No flop dealt
    assert hand.won_amount is None  # Hero didn't win


def test_wpn_empty_text() -> None:
    """Test parsing empty or invalid text."""
    assert parse_many("") == []
    assert parse_many("   ") == []
    assert parse_many("Random text without hand history") == []


def test_wpn_actions_extraction() -> None:
    """Test that actions are extracted from the hand."""
    text = """
***** Hand History for Game 3333333333 *****
$0.25/$0.50 NL Texas Hold'em - Thursday, January 10, 2026, 20:00:00
Table Test (Real Money)
Seat 1: Hero ($50.00)
Seat 2: Villain ($50.00)
Villain posts small blind [$0.25]
Hero posts big blind [$0.50]
** Dealing down cards **
Dealt to Hero [Ad Kd]
Villain raises [$1.50]
Hero raises [$4.50]
Villain calls [$3.50]
** Dealing Flop ** [As Ks Qd]
Hero bets [$6.00]
Villain folds
Hero wins $9.50
*** Summary ***
Total pot $9.50
""".strip()
    
    hand = parse_hand(text)
    
    assert hand.hand_id == "3333333333"
    assert hand.actions is not None
    # Actions should contain the dealt line and action lines
    assert "Dealt to Hero" in hand.actions
    assert "raises" in hand.actions.lower() or "calls" in hand.actions.lower()
