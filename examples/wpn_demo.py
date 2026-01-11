#!/usr/bin/env python3
"""Example script demonstrating WPN hand history import and analysis.

This script shows how to use the WPN parser and API to import and analyze
poker hands from Winning Poker Network sites (ACR, BlackChip, etc.).
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.blockchain.wpn_parser import parse_many

# Example WPN hand history from America's Cardroom
SAMPLE_HAND = """
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
"""


def main():
    """Demonstrate WPN hand parsing."""
    print("=" * 70)
    print("WPN Hand History Parser Demo")
    print("=" * 70)
    print()
    
    # Parse the hand history
    hands = parse_many(SAMPLE_HAND)
    
    print(f"✓ Successfully parsed {len(hands)} hand(s)")
    print()
    
    # Display parsed information
    for i, hand in enumerate(hands, 1):
        print(f"Hand #{i}:")
        print(f"  Game ID:      {hand.hand_id}")
        print(f"  Date:         {hand.date_played}")
        print(f"  Stakes:       {hand.stakes}")
        print(f"  Table:        {hand.table_name}")
        print(f"  Player:       {hand.player_name}")
        print(f"  Seat:         {hand.seat_number}")
        print(f"  Hole Cards:   {hand.hole_cards}")
        print(f"  Board:        {hand.board}")
        print(f"  Won:          ${hand.won_amount}" if hand.won_amount else "  Won:          -")
        print(f"  Pot Size:     ${hand.pot_size}" if hand.pot_size else "  Pot Size:     -")
        print()
    
    print("=" * 70)
    print()
    print("Next Steps:")
    print("1. Export your hand histories from BEtAcr.exe")
    print("2. Use the API to import: POST /api/wpn/import-file")
    print("3. Get AI analysis: POST /api/wpn/session-review")
    print()
    print("See WPN_INTEGRATION.md for full documentation!")
    print("=" * 70)


if __name__ == "__main__":
    main()
