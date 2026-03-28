"""
Advanced Poker Tools - Range Visualizer, Equity Calculator, GTO Trainer
"""

from poker_engine import Card, Deck, HandEvaluator, Rank, Suit, PokerGame
from typing import List, Dict, Set, Tuple
import random
from collections import defaultdict
import re


class HandRange:
    """Represents and manipulates poker hand ranges"""
    
    def __init__(self):
        self.hands = set()  # Set of hand strings like "AA", "AKs", "AKo"
    
    def add_hand(self, hand_str: str):
        """Add a hand to the range (e.g., 'AA', 'AKs', 'AKo')"""
        self.hands.add(hand_str)
    
    def remove_hand(self, hand_str: str):
        """Remove a hand from the range"""
        self.hands.discard(hand_str)
    
    def add_preset_range(self, range_type: str):
        """Add common preset ranges"""
        if range_type == "all_pairs":
            for r in ['AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22']:
                self.add_hand(r)
        elif range_type == "premium_pairs":
            for r in ['AA', 'KK', 'QQ', 'JJ']:
                self.add_hand(r)
        elif range_type == "broadway":
            # All broadway cards (T or higher)
            ranks = ['A', 'K', 'Q', 'J', 'T']
            for i, r1 in enumerate(ranks):
                for r2 in ranks[i:]:
                    if r1 == r2:
                        self.add_hand(f"{r1}{r2}")
                    else:
                        self.add_hand(f"{r1}{r2}s")
                        self.add_hand(f"{r1}{r2}o")
        elif range_type == "suited_connectors":
            rank_order = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
            rank_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10,
                          '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2}
            for i, r1 in enumerate(rank_order[:-1]):
                r2 = rank_order[i+1]
                self.add_hand(f"{r1}{r2}s")
        elif range_type == "suited_aces":
            for r in ['K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']:
                self.add_hand(f"A{r}s")
        elif range_type == "any_ace":
            for r in ['K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']:
                self.add_hand(f"A{r}s")
                self.add_hand(f"A{r}o")
            self.add_hand("AA")
    
    def to_combos(self, dead_cards: Set[Card] = None) -> List[Tuple[Card, Card]]:
        """Convert range to specific card combinations"""
        if dead_cards is None:
            dead_cards = set()
        
        combos = []
        deck = Deck()
        available_cards = [c for c in deck.cards if c not in dead_cards]
        
        rank_map = {r.symbol: r for r in Rank}
        
        for hand_str in self.hands:
            if len(hand_str) == 2:  # Pair like "AA"
                rank = rank_map[hand_str[0]]
                cards_of_rank = [c for c in available_cards if c.rank == rank]
                # All pair combinations
                for i, c1 in enumerate(cards_of_rank):
                    for c2 in cards_of_rank[i+1:]:
                        combos.append((c1, c2))
            
            elif len(hand_str) == 3:  # Like "AKs" or "AKo"
                r1, r2, suit_type = hand_str[0], hand_str[1], hand_str[2]
                rank1 = rank_map[r1]
                rank2 = rank_map[r2]
                
                cards_r1 = [c for c in available_cards if c.rank == rank1]
                cards_r2 = [c for c in available_cards if c.rank == rank2]
                
                if suit_type == 's':  # Suited
                    for c1 in cards_r1:
                        for c2 in cards_r2:
                            if c1.suit == c2.suit:
                                combos.append((c1, c2))
                else:  # Offsuit
                    for c1 in cards_r1:
                        for c2 in cards_r2:
                            if c1.suit != c2.suit:
                                combos.append((c1, c2))
        
        return combos
    
    def get_matrix_representation(self) -> Dict[str, bool]:
        """Get a 13x13 matrix representation of the range"""
        ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        matrix = {}
        
        for i, r1 in enumerate(ranks):
            for j, r2 in enumerate(ranks):
                if i == j:  # Pair
                    key = f"{r1}{r2}"
                elif i < j:  # Suited (upper triangle)
                    key = f"{r1}{r2}s"
                else:  # Offsuit (lower triangle)
                    key = f"{r2}{r1}o"
                
                matrix[key] = key in self.hands
        
        return matrix


class EquityCalculator:
    """Monte Carlo equity calculator"""
    
    @staticmethod
    def calculate_equity(
        hero_hand: List[Card],
        villain_range: HandRange,
        board: List[Card] = None,
        num_simulations: int = 10000,
        game_type: str = 'holdem'
    ) -> Dict:
        """
        Calculate equity using Monte Carlo simulation
        
        Args:
            hero_hand: Hero's hole cards
            villain_range: Villain's range
            board: Current board cards (can be empty, flop, turn, or river)
            num_simulations: Number of simulations to run
            game_type: 'holdem' or 'omaha'
        
        Returns:
            Dict with equity percentages and win/tie counts
        """
        if board is None:
            board = []
        
        dead_cards = set(hero_hand + board)
        villain_combos = villain_range.to_combos(dead_cards)
        
        if not villain_combos:
            return {'error': 'No valid villain combos in range'}
        
        hero_wins = 0
        villain_wins = 0
        ties = 0
        
        deck = Deck()
        available_for_board = [c for c in deck.cards if c not in dead_cards]
        
        for _ in range(num_simulations):
            # Pick random villain hand
            villain_hand = list(random.choice(villain_combos))
            
            # Complete the board if needed
            current_board = board.copy()
            used_cards = set(hero_hand + villain_hand + current_board)
            available = [c for c in deck.cards if c not in used_cards]
            
            cards_needed = 5 - len(current_board)
            if cards_needed > 0:
                current_board.extend(random.sample(available, cards_needed))
            
            # Evaluate hands
            try:
                if game_type == 'holdem':
                    hero_result = PokerGame.evaluate_holdem_hand(hero_hand, current_board)
                    villain_result = PokerGame.evaluate_holdem_hand(villain_hand, current_board)
                else:
                    hero_result = PokerGame.evaluate_omaha_hand(hero_hand, current_board)
                    villain_result = PokerGame.evaluate_omaha_hand(villain_hand, current_board)
                
                # Compare
                if hero_result['rank_value'] > villain_result['rank_value']:
                    hero_wins += 1
                elif hero_result['rank_value'] < villain_result['rank_value']:
                    villain_wins += 1
                else:
                    ties += 1
            except:
                # Invalid hand, skip
                ties += 1
        
        total = num_simulations
        return {
            'hero_equity': round((hero_wins + ties * 0.5) / total * 100, 2),
            'villain_equity': round((villain_wins + ties * 0.5) / total * 100, 2),
            'hero_wins': hero_wins,
            'villain_wins': villain_wins,
            'ties': ties,
            'simulations': num_simulations
        }


class GTOTrainer:
    """GTO (Game Theory Optimal) training scenarios"""
    
    # Simplified GTO ranges for common situations
    GTO_RANGES = {
        'BTN_vs_BB_15bb': {
            'open_size': 2.5,
            'open_frequency': 0.48,
            'open_range': ['AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                          'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'ATs', 'ATo', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s',
                          'KQs', 'KQo', 'KJs', 'KJo', 'KTs', 'KTo', 'K9s',
                          'QJs', 'QJo', 'QTs', 'Q9s',
                          'JTs', 'J9s', 'T9s', '98s', '87s', '76s', '65s', '54s']
        },
        'BTN_vs_BB_30bb': {
            'open_size': 2.5,
            'open_frequency': 0.45,
            'open_range': ['AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                          'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'ATs', 'A9s', 'A8s', 'A7s', 'A5s', 'A4s',
                          'KQs', 'KQo', 'KJs', 'KJo', 'KTs', 'K9s',
                          'QJs', 'QTs', 'Q9s',
                          'JTs', 'J9s', 'T9s', '98s', '87s', '76s', '65s']
        },
        'CO_vs_BTN_100bb': {
            'open_size': 2.5,
            'open_frequency': 0.35,
            'open_range': ['AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44',
                          'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'ATs', 'A9s', 'A5s',
                          'KQs', 'KQo', 'KJs', 'KTs',
                          'QJs', 'QTs',
                          'JTs', 'T9s', '98s', '87s', '76s']
        }
    }
    
    @staticmethod
    def get_scenario(scenario_name: str) -> Dict:
        """Get GTO recommendations for a scenario"""
        if scenario_name not in GTOTrainer.GTO_RANGES:
            return {'error': f'Scenario {scenario_name} not found'}
        
        scenario = GTOTrainer.GTO_RANGES[scenario_name]
        return {
            'scenario': scenario_name,
            'open_size': f"{scenario['open_size']}bb",
            'open_frequency': f"{scenario['open_frequency'] * 100}%",
            'num_hands': len(scenario['open_range']),
            'range': scenario['open_range']
        }
    
    @staticmethod
    def list_scenarios() -> List[str]:
        """List all available scenarios"""
        return list(GTOTrainer.GTO_RANGES.keys())
    
    @staticmethod
    def should_open(hand_str: str, scenario_name: str) -> Dict:
        """Check if a hand should be opened in a scenario"""
        if scenario_name not in GTOTrainer.GTO_RANGES:
            return {'error': f'Scenario {scenario_name} not found'}
        
        opening_range = GTOTrainer.GTO_RANGES[scenario_name]['open_range']
        should_open = hand_str in opening_range
        
        return {
            'hand': hand_str,
            'scenario': scenario_name,
            'should_open': should_open,
            'action': 'Open' if should_open else 'Fold',
            'open_size': GTOTrainer.GTO_RANGES[scenario_name]['open_size']
        }


class HandHistoryParser:
    """Parse poker hand histories from PokerStars and GGPoker"""
    
    @staticmethod
    def parse_pokerstars(hand_text: str) -> Dict:
        """Parse a PokerStars hand history"""
        lines = hand_text.strip().split('\n')
        
        # Extract basic info
        hand_info = {
            'players': [],
            'actions': [],
            'board': [],
            'pot': 0,
            'stakes': None
        }
        
        # Parse hand ID and stakes
        if lines:
            first_line = lines[0]
            stakes_match = re.search(r'\$?([\d.]+)/\$?([\d.]+)', first_line)
            if stakes_match:
                hand_info['stakes'] = f"${stakes_match.group(1)}/${stakes_match.group(2)}"
        
        # Parse players and actions
        for line in lines:
            # Player seats
            if 'Seat' in line and ':' in line:
                player_match = re.search(r'Seat \d+: (.+?) \(\$?([\d.]+)', line)
                if player_match:
                    hand_info['players'].append({
                        'name': player_match.group(1),
                        'stack': float(player_match.group(2))
                    })
            
            # Actions (calls, raises, folds)
            if any(action in line for action in [': folds', ': calls', ': raises', ': bets', ': checks']):
                hand_info['actions'].append(line.strip())
            
            # Board cards
            if 'FLOP' in line or 'TURN' in line or 'RIVER' in line:
                cards_match = re.search(r'\[([^\]]+)\]', line)
                if cards_match:
                    cards = cards_match.group(1).split()
                    hand_info['board'].extend(cards)
        
        return hand_info
    
    @staticmethod
    def calculate_stats(hand_histories: List[Dict]) -> Dict:
        """Calculate poker statistics from multiple hand histories"""
        stats = {
            'total_hands': len(hand_histories),
            'vpip_count': 0,  # Voluntarily Put money In Pot
            'pfr_count': 0,   # Pre-Flop Raise
            'threeb_count': 0,  # 3-bet
            'fold_to_3bet_count': 0
        }
        
        for hand in hand_histories:
            actions = hand.get('actions', [])
            
            # Simple heuristic stats (would need more complex parsing in production)
            for action in actions:
                if 'calls' in action or 'raises' in action or 'bets' in action:
                    stats['vpip_count'] += 1
                    break
            
            for action in actions:
                if 'raises' in action:
                    stats['pfr_count'] += 1
                    break
        
        # Calculate percentages
        if stats['total_hands'] > 0:
            stats['vpip'] = round(stats['vpip_count'] / stats['total_hands'] * 100, 1)
            stats['pfr'] = round(stats['pfr_count'] / stats['total_hands'] * 100, 1)
            stats['threeb'] = round(stats['threeb_count'] / stats['total_hands'] * 100, 1) if stats['threeb_count'] > 0 else 0
        
        return stats
