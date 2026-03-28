"""
Poker Engine - Core logic for Texas Hold'em and Omaha poker games.
Handles card representation, hand evaluation, and board comparison.
"""

from enum import Enum
from typing import List, Tuple, Dict
from itertools import combinations
from collections import Counter


class Suit(Enum):
    """Card suits"""
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Rank(Enum):
    """Card ranks with values for comparison"""
    TWO = (2, "2")
    THREE = (3, "3")
    FOUR = (4, "4")
    FIVE = (5, "5")
    SIX = (6, "6")
    SEVEN = (7, "7")
    EIGHT = (8, "8")
    NINE = (9, "9")
    TEN = (10, "T")
    JACK = (11, "J")
    QUEEN = (12, "Q")
    KING = (13, "K")
    ACE = (14, "A")
    
    def __init__(self, numeric_value, symbol):
        self.numeric_value = numeric_value
        self.symbol = symbol
    
    def __lt__(self, other):
        return self.numeric_value < other.numeric_value
    
    def __le__(self, other):
        return self.numeric_value <= other.numeric_value
    
    def __gt__(self, other):
        return self.numeric_value > other.numeric_value
    
    def __ge__(self, other):
        return self.numeric_value >= other.numeric_value


class Card:
    """Represents a playing card"""
    
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
    
    def __str__(self):
        return f"{self.rank.symbol}{self.suit.value}"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self):
        return hash((self.rank, self.suit))
    
    @classmethod
    def from_string(cls, card_str: str):
        """Create a card from string like 'As' or 'Kh'"""
        rank_map = {r.symbol: r for r in Rank}
        suit_map = {
            'h': Suit.HEARTS, '♥': Suit.HEARTS,
            'd': Suit.DIAMONDS, '♦': Suit.DIAMONDS,
            'c': Suit.CLUBS, '♣': Suit.CLUBS,
            's': Suit.SPADES, '♠': Suit.SPADES
        }
        
        rank_str = card_str[0].upper()
        suit_str = card_str[1].lower()
        
        return cls(rank_map[rank_str], suit_map[suit_str])


class HandRank(Enum):
    """Poker hand rankings"""
    HIGH_CARD = (1, "High Card")
    PAIR = (2, "Pair")
    TWO_PAIR = (3, "Two Pair")
    THREE_OF_A_KIND = (4, "Three of a Kind")
    STRAIGHT = (5, "Straight")
    FLUSH = (6, "Flush")
    FULL_HOUSE = (7, "Full House")
    FOUR_OF_A_KIND = (8, "Four of a Kind")
    STRAIGHT_FLUSH = (9, "Straight Flush")
    ROYAL_FLUSH = (10, "Royal Flush")
    
    def __init__(self, rank_value, name):
        self.rank_value = rank_value
        self.hand_name = name
    
    def __lt__(self, other):
        return self.rank_value < other.rank_value


class Deck:
    """Represents a deck of cards"""
    
    def __init__(self):
        self.cards = [Card(rank, suit) for rank in Rank for suit in Suit]
    
    def __len__(self):
        return len(self.cards)


class HandEvaluator:
    """Evaluates poker hands and determines winners"""
    
    @staticmethod
    def evaluate_hand(cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """
        Evaluate a 5-card poker hand.
        Returns (HandRank, tiebreaker_values)
        """
        if len(cards) != 5:
            raise ValueError("Must evaluate exactly 5 cards")
        
        # Sort cards by rank (descending)
        sorted_cards = sorted(cards, key=lambda c: c.rank.numeric_value, reverse=True)
        ranks = [c.rank.numeric_value for c in sorted_cards]
        suits = [c.suit for c in sorted_cards]
        rank_counts = Counter(ranks)
        
        is_flush = len(set(suits)) == 1
        is_straight = HandEvaluator._is_straight(ranks)
        
        # Check for straight flush variations
        if is_flush and is_straight:
            if ranks[0] == 14:  # Ace high straight
                return (HandRank.ROYAL_FLUSH, ranks)
            return (HandRank.STRAIGHT_FLUSH, ranks)
        
        # Four of a kind
        if 4 in rank_counts.values():
            quad = [r for r, count in rank_counts.items() if count == 4][0]
            kicker = [r for r in ranks if r != quad][0]
            return (HandRank.FOUR_OF_A_KIND, [quad, kicker])
        
        # Full house
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            trips = [r for r, count in rank_counts.items() if count == 3][0]
            pair = [r for r, count in rank_counts.items() if count == 2][0]
            return (HandRank.FULL_HOUSE, [trips, pair])
        
        # Flush
        if is_flush:
            return (HandRank.FLUSH, ranks)
        
        # Straight
        if is_straight:
            return (HandRank.STRAIGHT, ranks)
        
        # Three of a kind
        if 3 in rank_counts.values():
            trips = [r for r, count in rank_counts.items() if count == 3][0]
            kickers = sorted([r for r in ranks if r != trips], reverse=True)
            return (HandRank.THREE_OF_A_KIND, [trips] + kickers)
        
        # Two pair
        if list(rank_counts.values()).count(2) == 2:
            pairs = sorted([r for r, count in rank_counts.items() if count == 2], reverse=True)
            kicker = [r for r in ranks if r not in pairs][0]
            return (HandRank.TWO_PAIR, pairs + [kicker])
        
        # One pair
        if 2 in rank_counts.values():
            pair = [r for r, count in rank_counts.items() if count == 2][0]
            kickers = sorted([r for r in ranks if r != pair], reverse=True)
            return (HandRank.PAIR, [pair] + kickers)
        
        # High card
        return (HandRank.HIGH_CARD, ranks)
    
    @staticmethod
    def _is_straight(ranks: List[int]) -> bool:
        """Check if ranks form a straight"""
        sorted_ranks = sorted(set(ranks), reverse=True)
        if len(sorted_ranks) != 5:
            return False
        
        # Regular straight
        if sorted_ranks[0] - sorted_ranks[4] == 4:
            return True
        
        # Wheel (A-2-3-4-5)
        if sorted_ranks == [14, 5, 4, 3, 2]:
            return True
        
        return False
    
    @staticmethod
    def best_hand(cards: List[Card]) -> Tuple[List[Card], HandRank, List[int]]:
        """
        Find the best 5-card hand from 5+ cards.
        Returns (best_5_cards, HandRank, tiebreaker_values)
        """
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards")
        
        if len(cards) == 5:
            hand_rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
            return (cards, hand_rank, tiebreakers)
        
        # Try all 5-card combinations
        best = None
        best_rank = None
        best_tiebreakers = None
        
        for combo in combinations(cards, 5):
            combo_list = list(combo)
            rank, tiebreakers = HandEvaluator.evaluate_hand(combo_list)
            
            if best is None or HandEvaluator._compare_hands(
                (rank, tiebreakers), (best_rank, best_tiebreakers)
            ) > 0:
                best = combo_list
                best_rank = rank
                best_tiebreakers = tiebreakers
        
        return (best, best_rank, best_tiebreakers)
    
    @staticmethod
    def _compare_hands(hand1: Tuple[HandRank, List[int]], 
                      hand2: Tuple[HandRank, List[int]]) -> int:
        """
        Compare two hands. Returns 1 if hand1 wins, -1 if hand2 wins, 0 if tie.
        """
        rank1, tie1 = hand1
        rank2, tie2 = hand2
        
        if rank1.value > rank2.value:
            return 1
        elif rank1.value < rank2.value:
            return -1
        else:
            # Same rank, compare tiebreakers
            for t1, t2 in zip(tie1, tie2):
                if t1 > t2:
                    return 1
                elif t1 < t2:
                    return -1
            return 0


class LowballEvaluator:
    """Evaluates lowball poker hands (for Razz, etc.)"""
    
    @staticmethod
    def evaluate_lowball_hand(cards: List[Card]) -> Tuple[List[int], str]:
        """
        Evaluate a lowball hand (A-5 low - straights/flushes don't count).
        Returns (hand_values, description) where lower is better.
        In Razz/A-5 lowball: A=1, 2-K are face value.
        Best hand is A-2-3-4-5 (wheel).
        """
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards for lowball")
        
        # Convert aces to 1 for low evaluation
        values = []
        for card in cards:
            if card.rank == Rank.ACE:
                values.append(1)
            else:
                values.append(card.rank.numeric_value)
        
        # Sort and take the 5 lowest cards
        values.sort()
        low_hand = values[:5]
        
        # Create description
        rank_names = {1: 'A', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
                     8: '8', 9: '9', 10: 'T', 11: 'J', 12: 'Q', 13: 'K'}
        desc = '-'.join([rank_names.get(v, str(v)) for v in low_hand])
        
        return (low_hand, f"{desc} low")
    
    @staticmethod
    def compare_lowball_hands(hand1_values: List[int], hand2_values: List[int]) -> int:
        """
        Compare two lowball hands. Returns 1 if hand1 is better (lower),
        -1 if hand2 is better, 0 if tie.
        """
        for v1, v2 in zip(hand1_values, hand2_values):
            if v1 < v2:
                return 1  # hand1 is better (lower)
            elif v1 > v2:
                return -1  # hand2 is better (lower)
        return 0  # Tie


class PokerGame:
    """Manages poker game logic for Texas Hold'em, Omaha, Stud, and Razz"""
    
    @staticmethod
    def evaluate_holdem_hand(hole_cards: List[Card], board: List[Card]) -> Dict:
        """
        Evaluate a Texas Hold'em hand (2 hole cards + 5 board cards).
        """
        if len(hole_cards) != 2:
            raise ValueError("Texas Hold'em requires exactly 2 hole cards")
        if len(board) < 3 or len(board) > 5:
            raise ValueError("Board must have 3-5 cards")
        
        all_cards = hole_cards + board
        best_cards, hand_rank, tiebreakers = HandEvaluator.best_hand(all_cards)
        
        return {
            'game_type': 'Texas Hold\'em',
            'hole_cards': [str(c) for c in hole_cards],
            'board': [str(c) for c in board],
            'best_hand': [str(c) for c in best_cards],
            'hand_rank': hand_rank.hand_name,
            'rank_value': hand_rank.rank_value
        }
    
    @staticmethod
    def evaluate_omaha_hand(hole_cards: List[Card], board: List[Card]) -> Dict:
        """
        Evaluate an Omaha hand (4 hole cards + 5 board cards).
        Must use exactly 2 hole cards and 3 board cards.
        """
        if len(hole_cards) != 4:
            raise ValueError("Omaha requires exactly 4 hole cards")
        if len(board) != 5:
            raise ValueError("Omaha requires exactly 5 board cards")
        
        best = None
        best_rank = None
        best_tiebreakers = None
        best_cards = None
        
        # Try all combinations of 2 hole cards and 3 board cards
        for hole_combo in combinations(hole_cards, 2):
            for board_combo in combinations(board, 3):
                hand = list(hole_combo) + list(board_combo)
                rank, tiebreakers = HandEvaluator.evaluate_hand(hand)
                
                if best is None or HandEvaluator._compare_hands(
                    (rank, tiebreakers), (best_rank, best_tiebreakers)
                ) > 0:
                    best_cards = hand
                    best_rank = rank
                    best_tiebreakers = tiebreakers
        
        return {
            'game_type': 'Omaha',
            'hole_cards': [str(c) for c in hole_cards],
            'board': [str(c) for c in board],
            'best_hand': [str(c) for c in best_cards],
            'hand_rank': best_rank.hand_name,
            'rank_value': best_rank.rank_value
        }
    
    @staticmethod
    def compare_boards(hole_cards: List[Card], boards: List[List[Card]], 
                      game_type: str = 'holdem') -> List[Dict]:
        """
        Compare the same hand across different boards.
        Returns results sorted by hand strength.
        """
        results = []
        
        for i, board in enumerate(boards):
            try:
                if game_type == 'holdem':
                    result = PokerGame.evaluate_holdem_hand(hole_cards, board)
                else:
                    result = PokerGame.evaluate_omaha_hand(hole_cards, board)
                result['board_number'] = i + 1
                results.append(result)
            except Exception as e:
                results.append({
                    'board_number': i + 1,
                    'error': str(e)
                })
        
        # Sort by rank value (best first)
        results.sort(key=lambda x: x.get('rank_value', 0), reverse=True)
        return results
    
    @staticmethod
    def evaluate_stud_hand(hole_cards: List[Card]) -> Dict:
        """
        Evaluate a 7-Card Stud hand (7 cards total).
        Uses best 5-card combination.
        """
        if len(hole_cards) != 7:
            raise ValueError("7-Card Stud requires exactly 7 cards")
        
        best_cards, hand_rank, tiebreakers = HandEvaluator.best_hand(hole_cards)
        
        return {
            'game_type': '7-Card Stud',
            'hole_cards': [str(c) for c in hole_cards],
            'best_hand': [str(c) for c in best_cards],
            'hand_rank': hand_rank.hand_name,
            'rank_value': hand_rank.rank_value
        }
    
    @staticmethod
    def evaluate_razz_hand(hole_cards: List[Card]) -> Dict:
        """
        Evaluate a Razz hand (7-card lowball).
        Best 5-card low hand wins. Straights and flushes don't count.
        Ace is low (best card).
        """
        if len(hole_cards) != 7:
            raise ValueError("Razz requires exactly 7 cards")
        
        low_values, description = LowballEvaluator.evaluate_lowball_hand(hole_cards)
        
        # Find the actual cards that make up the low hand
        # Convert values back to cards
        best_cards = []
        remaining_cards = hole_cards.copy()
        for val in low_values:
            for card in remaining_cards:
                card_val = 1 if card.rank == Rank.ACE else card.rank.numeric_value
                if card_val == val:
                    best_cards.append(card)
                    remaining_cards.remove(card)
                    break
        
        return {
            'game_type': 'Razz',
            'hole_cards': [str(c) for c in hole_cards],
            'best_hand': [str(c) for c in best_cards[:5]],
            'hand_rank': description,
            'rank_value': low_values  # Lower is better in Razz
        }
