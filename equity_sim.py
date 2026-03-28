"""
Monte Carlo Equity Calculator - Improved version with proper range parsing
and hand evaluation integration.
"""

import random
from poker_engine import Card, HandEvaluator, PokerGame, Deck, Rank, Suit
from typing import List, Tuple, Set

RANKS = '23456789TJQKA'
SUITS = 'shdc'  # spades, hearts, diamonds, clubs


def parse_range(hand_range: str) -> List[str]:
    """
    Parse a hand range string into specific card combinations.
    Examples: "AKs" -> all suited AK combos, "22" -> all pocket deuces
    """
    res = []
    
    # Check if it's suited or offsuit
    if hand_range.endswith('s'):
        suited = True
        hand_range = hand_range[:-1]
    elif hand_range.endswith('o'):
        suited = False
        hand_range = hand_range[:-1]
    else:
        # Assume it's a pair or no designation
        suited = None
    
    # Extract the two ranks
    r1, r2 = hand_range[0], hand_range[1]
    
    if r1 == r2:
        # Pair - all 6 combinations
        for i, s1 in enumerate(SUITS):
            for s2 in SUITS[i+1:]:
                res.append(f"{r1}{s1}{r2}{s2}")
    else:
        # Two different ranks
        if suited:
            # Only suited combinations (4 combos)
            for suit in SUITS:
                res.append(f"{r1}{suit}{r2}{suit}")
        elif suited is False:
            # Only offsuit combinations (12 combos)
            for s1 in SUITS:
                for s2 in SUITS:
                    if s1 != s2:
                        res.append(f"{r1}{s1}{r2}{s2}")
        else:
            # All combinations (16 combos)
            for s1 in SUITS:
                for s2 in SUITS:
                    res.append(f"{r1}{s1}{r2}{s2}")
    
    return res


def card_str_to_card(card_str: str) -> Card:
    """Convert a 2-character string like 'As' to a Card object"""
    rank_char = card_str[0].upper()
    suit_char = card_str[1].lower()
    
    # Map to Card object
    rank_map = {r.symbol: r for r in Rank}
    suit_map = {'s': Suit.SPADES, 'h': Suit.HEARTS, 'd': Suit.DIAMONDS, 'c': Suit.CLUBS}
    
    return Card(rank_map[rank_char], suit_map[suit_char])


def evaluate_hand(board: Tuple[Card, ...], hand: Tuple[Card, Card]) -> Tuple[int, List[int]]:
    """
    Evaluate a hand given a board.
    Returns (rank_value, tiebreakers) for comparison.
    """
    all_cards = list(hand) + list(board)
    best_cards, hand_rank, tiebreakers = HandEvaluator.best_hand(all_cards)
    return (hand_rank.rank_value, tiebreakers)


def run_sim(hand1: Tuple[Card, Card], hand2: Tuple[Card, Card], 
           board: Tuple[Card, ...] = ()) -> Tuple[bool, bool]:
    """
    Run a single simulation comparing two hands.
    Returns (hand1_wins, tie)
    """
    # Get all used cards
    used_cards = set(hand1 + hand2 + board)
    
    # Create deck and remove used cards
    deck = Deck()
    available = [c for c in deck.cards if c not in used_cards]
    
    # Deal remaining board cards if needed
    cards_needed = 5 - len(board)
    if cards_needed > 0:
        dealt_cards = random.sample(available, cards_needed)
        full_board = board + tuple(dealt_cards)
    else:
        full_board = board
    
    # Evaluate both hands
    score1 = evaluate_hand(full_board, hand1)
    score2 = evaluate_hand(full_board, hand2)
    
    # Compare
    if score1[0] > score2[0]:
        return True, False
    elif score1[0] < score2[0]:
        return False, False
    else:
        # Same hand rank, compare tiebreakers
        for t1, t2 in zip(score1[1], score2[1]):
            if t1 > t2:
                return True, False
            elif t1 < t2:
                return False, False
        return False, True  # Tie


def calculate_equity_fast(hand1_combos: List[str], hand2_combos: List[str], 
                         board_strs: List[str] = None, trials: int = 10000) -> dict:
    """
    Fast equity calculation between two ranges.
    
    Args:
        hand1_combos: List of hand combinations for player 1 (e.g., from parse_range)
        hand2_combos: List of hand combinations for player 2
        board_strs: Optional board cards as strings (e.g., ['As', 'Kh', 'Qd'])
        trials: Number of Monte Carlo trials
    
    Returns:
        Dictionary with equity percentages and statistics
    """
    if board_strs:
        board = tuple(card_str_to_card(c) for c in board_strs)
    else:
        board = ()
    
    # Remove dead card combos
    dead_cards = set(board)
    
    # Filter valid combos
    valid_h1 = []
    for combo in hand1_combos:
        c1 = card_str_to_card(combo[0:2])
        c2 = card_str_to_card(combo[2:4])
        if c1 not in dead_cards and c2 not in dead_cards and c1 != c2:
            valid_h1.append((c1, c2))
    
    valid_h2 = []
    for combo in hand2_combos:
        c1 = card_str_to_card(combo[0:2])
        c2 = card_str_to_card(combo[2:4])
        if c1 not in dead_cards and c2 not in dead_cards and c1 != c2:
            valid_h2.append((c1, c2))
    
    if not valid_h1 or not valid_h2:
        return {'error': 'No valid hand combinations'}
    
    # Run simulations
    h1_wins = 0
    h2_wins = 0
    ties = 0
    
    for _ in range(trials):
        # Pick random hands from each range
        hand1 = random.choice(valid_h1)
        hand2 = random.choice(valid_h2)
        
        # Make sure hands don't overlap
        if hand1[0] == hand2[0] or hand1[0] == hand2[1] or \
           hand1[1] == hand2[0] or hand1[1] == hand2[1]:
            continue
        
        h1_win, is_tie = run_sim(hand1, hand2, board)
        
        if is_tie:
            ties += 1
        elif h1_win:
            h1_wins += 1
        else:
            h2_wins += 1
    
    total = h1_wins + h2_wins + ties
    if total == 0:
        return {'error': 'No valid simulations'}
    
    return {
        'hand1_equity': round((h1_wins + ties * 0.5) / total * 100, 2),
        'hand2_equity': round((h2_wins + ties * 0.5) / total * 100, 2),
        'hand1_wins': h1_wins,
        'hand2_wins': h2_wins,
        'ties': ties,
        'total_trials': total
    }


def range_vs_range(range1_str: str, range2_str: str, 
                   board_strs: List[str] = None, trials: int = 10000) -> dict:
    """
    Calculate equity for range vs range.
    
    Examples:
        range_vs_range("AKs", "QQ", trials=10000)
        range_vs_range("AKo", "TT", ["As", "Kh", "7d"], trials=10000)
    """
    combos1 = parse_range(range1_str)
    combos2 = parse_range(range2_str)
    
    result = calculate_equity_fast(combos1, combos2, board_strs, trials)
    result['range1'] = range1_str
    result['range2'] = range2_str
    result['range1_combos'] = len(combos1)
    result['range2_combos'] = len(combos2)
    
    return result


def multi_way_equity(ranges: List[str], board_strs: List[str] = None, 
                      trials: int = 10000) -> dict:
    """
    Calculate equity for multiple players (3+).
    
    Args:
        ranges: List of hand range strings for each player (e.g., ["AA", "KK", "QQ"])
        board_strs: Optional board cards as strings
        trials: Number of Monte Carlo trials
    
    Returns:
        Dictionary with equity percentages for each player
    
    Examples:
        multi_way_equity(["AA", "KK", "QQ"], trials=10000)
        multi_way_equity(["AKs", "TT", "88"], ["As", "Kh", "7d"], trials=10000)
    """
    if len(ranges) < 2:
        return {'error': 'Need at least 2 ranges'}
    
    if board_strs:
        board = tuple(card_str_to_card(c) for c in board_strs)
    else:
        board = ()
    
    # Parse all ranges
    all_combos = []
    dead_cards = set(board)
    
    for range_str in ranges:
        combos = parse_range(range_str)
        valid_combos = []
        for combo in combos:
            c1 = card_str_to_card(combo[0:2])
            c2 = card_str_to_card(combo[2:4])
            if c1 not in dead_cards and c2 not in dead_cards and c1 != c2:
                valid_combos.append((c1, c2))
        all_combos.append(valid_combos)
    
    # Check if all ranges have valid combos
    if any(len(combos) == 0 for combos in all_combos):
        return {'error': 'One or more ranges have no valid combinations'}
    
    # Initialize win counters
    wins = [0.0] * len(ranges)
    valid_trials = 0
    
    for _ in range(trials):
        # Pick random hand from each range
        hands = []
        all_cards_used = set(board)
        conflict = False
        
        for combos in all_combos:
            hand = random.choice(combos)
            # Check for card conflicts
            if hand[0] in all_cards_used or hand[1] in all_cards_used:
                conflict = True
                break
            hands.append(hand)
            all_cards_used.add(hand[0])
            all_cards_used.add(hand[1])
        
        if conflict:
            continue
        
        # Complete the board
        deck = Deck()
        available = [c for c in deck.cards if c not in all_cards_used]
        cards_needed = 5 - len(board)
        if cards_needed > 0:
            dealt_cards = random.sample(available, cards_needed)
            full_board = board + tuple(dealt_cards)
        else:
            full_board = board
        
        # Evaluate all hands
        scores = []
        for hand in hands:
            score = evaluate_hand(full_board, hand)
            scores.append(score)
        
        # Find winner(s)
        best_score = max(scores)
        winners = [i for i, score in enumerate(scores) if score == best_score]
        
        if len(winners) == 1:
            wins[winners[0]] += 1
        else:
            # Multiple winners - split the equity
            for winner_idx in winners:
                wins[winner_idx] += 1.0 / len(winners)
        
        valid_trials += 1
    
    if valid_trials == 0:
        return {'error': 'No valid simulations completed'}
    
    # Calculate equities
    result = {
        'players': len(ranges),
        'ranges': ranges,
        'total_trials': valid_trials,
        'equities': []
    }
    
    for i, range_str in enumerate(ranges):
        equity = wins[i] / valid_trials * 100
        result['equities'].append({
            'player': i + 1,
            'range': range_str,
            'equity': round(equity, 2),
            'wins': int(wins[i])
        })
    
    return result


# Quick test
if __name__ == '__main__':
    print("Testing range parser...")
    print("AKs combos:", parse_range("AKs"))
    print("22 combos:", parse_range("22"))
    print("AKo combos:", parse_range("AKo"))
    
    print("\nTesting equity calculator...")
    result = range_vs_range("AA", "KK", trials=1000)
    print(f"AA vs KK: {result}")
    
    print("\nWith board:")
    result = range_vs_range("AKs", "QQ", ["As", "Kh", "7d"], trials=1000)
    print(f"AKs vs QQ on AsKh7d: {result}")
    
    print("\nTesting multi-way equity (3 players):")
    result = multi_way_equity(["AA", "KK", "QQ"], trials=1000)
    print(f"AA vs KK vs QQ: {result}")
