"""Tests for WinningPokerNetwork (WPN) hand history parser."""

from backend.blockchain.wpn_parser import parse_hand, parse_many, split_hands


def test_wpn_parse_single_hand_basic():
    """Test parsing a basic WPN cash game hand."""
    text = """
#Game No : 123456789
***** Holdem(No Limit) - $0.50/$1 *****
Table: ACR Table 10 (Real Money)
2024/01/01 20:30:00 UTC

Seat 1: PlayerOne ($100)
Seat 2: PlayerTwo ($100)
Seat 3: PlayerThree ($100)

PlayerOne posts small blind $0.50
PlayerTwo posts big blind $1

*** HOLE CARDS ***
Dealt to PlayerThree [Ks Ah]
PlayerThree raises to $3
PlayerOne calls $3
PlayerTwo folds

*** FLOP *** [7c 4h Qs]
PlayerOne checks
PlayerThree bets $5
PlayerOne calls $5

*** TURN *** [7c 4h Qs] [Ac]
PlayerOne checks
PlayerThree bets $14
PlayerOne calls $14

*** RIVER *** [7c 4h Qs Ac] [2d]
PlayerOne checks
PlayerThree bets $30
PlayerOne folds

Uncalled bet ($30) returned to PlayerThree
PlayerThree wins $36.50

*** SUMMARY ***
Total pot $36.50
    """.strip()

    hand = parse_hand(text)
    
    assert hand.hand_id == "123456789"
    assert hand.stakes == "$0.50/$1"
    assert hand.game_variant == "Holdem (No Limit)"
    assert hand.player_name == "PlayerThree"
    assert hand.position == "3"
    assert hand.hole_cards == "KsAh"
    assert hand.board == "7c4hQs Ac 2d"
    assert hand.won_amount == 36.50
    assert hand.pot_size == 36.50
    assert hand.date_played is not None
    assert hand.date_played.year == 2024
    assert hand.date_played.month == 1
    assert hand.date_played.day == 1


def test_wpn_parse_multiple_hands():
    """Test splitting and parsing multiple hands."""
    text = """
#Game No : 111111111
***** Holdem(No Limit) - $0.50/$1 *****
2024/01/01 20:30:00 UTC
Dealt to Hero [As Kd]
*** HOLE CARDS ***
Hero raises to $3
*** SUMMARY ***
Total pot $5

#Game No : 222222222
***** Holdem(No Limit) - $0.50/$1 *****
2024/01/01 20:35:00 UTC
Dealt to Hero [2c 2d]
*** HOLE CARDS ***
Hero calls $1
Hero wins $8
*** SUMMARY ***
Total pot $8
    """.strip()

    hands = parse_many(text)
    
    assert len(hands) == 2
    assert hands[0].hand_id == "111111111"
    assert hands[0].hole_cards == "AsKd"
    assert hands[0].pot_size == 5.0
    assert hands[1].hand_id == "222222222"
    assert hands[1].hole_cards == "2c2d"
    assert hands[1].won_amount == 8.0


def test_wpn_parse_tournament_hand():
    """Test parsing a tournament hand with tournament ID."""
    text = """
#Game No : 987654321
***** Tournament #12345 - Holdem(No Limit) - $0/$0 *****
2024/01/01 21:00:00 UTC
Seat 1: Player1 ($1500)
Seat 2: Hero ($1500)

*** HOLE CARDS ***
Dealt to Hero [Jh Js]
Player1 raises to $150
Hero calls $150

*** FLOP *** [9d 3c 2s]
Player1 bets $300
Hero raises to $900
Player1 folds

Hero wins $1350

*** SUMMARY ***
Total pot $1350
    """.strip()

    hand = parse_hand(text)
    
    assert hand.hand_id == "987654321"
    assert hand.tournament_id == "12345"
    assert hand.game_variant == "Holdem (No Limit)"
    assert hand.player_name == "Hero"
    assert hand.hole_cards == "JhJs"
    assert hand.board == "9d3c2s"
    assert hand.won_amount == 1350.0
    assert hand.pot_size == 1350.0


def test_wpn_parse_showdown_hand():
    """Test parsing a hand that goes to showdown."""
    text = """
#Game No : 555555555
***** Holdem(No Limit) - $1/$2 *****
2024/01/02 10:15:00 UTC

Seat 1: Villain ($200)
Seat 2: Hero ($200)

Villain posts small blind $1
Hero posts big blind $2

*** HOLE CARDS ***
Dealt to Hero [Ad Kh]
Villain raises to $6
Hero raises to $18
Villain calls $12

*** FLOP *** [Ac 7h 3d]
Hero bets $12
Villain calls $12

*** TURN *** [Ac 7h 3d] [Ks]
Hero bets $30
Villain calls $30

*** RIVER *** [Ac 7h 3d Ks] [2c]
Hero bets $60
Villain calls $60

*** SHOW DOWN ***
Hero shows [Ad Kh]
Villain shows [As Qs]
Hero wins $238

*** SUMMARY ***
Total pot $238
    """.strip()

    hand = parse_hand(text)
    
    assert hand.hand_id == "555555555"
    assert hand.stakes == "$1/$2"
    assert hand.player_name == "Hero"
    assert hand.hole_cards == "AdKh"
    assert hand.board == "Ac7h3d Ks 2c"
    assert hand.won_amount == 238.0
    assert hand.pot_size == 238.0


def test_wpn_parse_hand_no_showdown():
    """Test parsing a hand where hero folds (no win)."""
    text = """
#Game No : 666666666
***** Holdem(No Limit) - $2/$5 *****
2024/01/03 15:45:00 UTC

Seat 1: Hero ($500)
Seat 2: Villain ($500)

Hero posts small blind $2
Villain posts big blind $5

*** HOLE CARDS ***
Dealt to Hero [8c 7d]
Hero raises to $15
Villain raises to $45
Hero folds

Villain wins $30

*** SUMMARY ***
Total pot $30
    """.strip()

    hand = parse_hand(text)
    
    assert hand.hand_id == "666666666"
    assert hand.stakes == "$2/$5"
    assert hand.player_name == "Hero"
    assert hand.hole_cards == "8c7d"
    assert hand.board is None  # No flop seen
    assert hand.won_amount is None  # Hero didn't win
    assert hand.pot_size == 30.0


def test_wpn_split_hands():
    """Test the hand splitting function."""
    text = """
#Game No : 111
Some hand text here

#Game No : 222
Another hand text

#Game No : 333
Third hand
    """.strip()

    hands = split_hands(text)
    
    assert len(hands) == 3
    assert "#Game No : 111" in hands[0]
    assert "#Game No : 222" in hands[1]
    assert "#Game No : 333" in hands[2]


def test_wpn_parse_omaha_hand():
    """Test parsing an Omaha PLO hand."""
    text = """
#Game No : 777777777
***** Omaha(Pot Limit) - $0.25/$0.50 *****
2024/01/04 12:00:00 UTC

Seat 1: Hero ($50)
Seat 2: Player2 ($50)

*** HOLE CARDS ***
Dealt to Hero [As Kh Qd Jc]
Hero raises to $1.50
Player2 calls $1.50

*** FLOP *** [Th 9h 8d]
Hero bets $3
Player2 calls $3

*** TURN *** [Th 9h 8d] [2c]
Hero checks
Player2 bets $9
Hero calls $9

*** RIVER *** [Th 9h 8d 2c] [7h]
Hero checks
Player2 bets $27
Hero folds

Player2 wins $30

*** SUMMARY ***
Total pot $30
    """.strip()

    hand = parse_hand(text)
    
    assert hand.hand_id == "777777777"
    assert hand.stakes == "$0.25/$0.50"
    assert hand.game_variant == "Omaha (Pot Limit)"
    assert hand.player_name == "Hero"
    assert hand.hole_cards == "AsKhQdJc"
    assert hand.board == "Th9h8d 2c 7h"
    assert hand.won_amount is None
    assert hand.pot_size == 30.0
