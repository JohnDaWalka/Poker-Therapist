"""
Advanced Training Scenarios Module - Specific poker situations and scenarios
"""

import random
from typing import Dict, List, Tuple
from poker_engine import Card, Deck, Rank, Suit
from enum import Enum


class ScenarioType(Enum):
    """Types of training scenarios"""
    SQUEEZE_PLAY = "squeeze_play"
    THREE_BET_POT = "3bet_pot"
    CONTINUATION_BET = "continuation_bet"
    CHECK_RAISE = "check_raise"
    RIVER_BLUFF = "river_bluff"
    SET_MINING = "set_mining"
    FLUSH_DRAW = "flush_draw"
    STRAIGHT_DRAW = "straight_draw"
    OVERCARDS = "overcards"
    MULTI_WAY_POT = "multiway_pot"


class TrainingScenario:
    """Represents a specific training scenario"""
    
    def __init__(self, scenario_type: ScenarioType, difficulty: str = 'medium'):
        self.scenario_type = scenario_type
        self.difficulty = difficulty
        self.description = ""
        self.setup = {}
        self.questions = []
        self.correct_answers = []
    
    def to_dict(self) -> Dict:
        """Convert scenario to dictionary"""
        return {
            'type': self.scenario_type.value,
            'difficulty': self.difficulty,
            'description': self.description,
            'setup': self.setup,
            'questions': self.questions
        }


class ScenarioGenerator:
    """Generate specific poker training scenarios"""
    
    @staticmethod
    def generate_squeeze_play() -> TrainingScenario:
        """
        Generate a squeeze play scenario.
        Squeeze: When there's a raise and call(s), you 3-bet to "squeeze" them out.
        """
        scenario = TrainingScenario(ScenarioType.SQUEEZE_PLAY)
        scenario.description = (
            "You're on the button. UTG raises to 3BB, MP calls. "
            "Action is on you with a strong hand. This is a squeeze spot."
        )
        
        # Generate a strong squeezing hand
        deck = Deck()
        random.shuffle(deck.cards)
        hole_cards = deck.cards[:2]
        
        scenario.setup = {
            'position': 'Button',
            'hole_cards': [str(c) for c in hole_cards],
            'action': 'UTG raises to 3BB, MP calls',
            'pot_size': '4.5BB',
            'stack_sizes': {'hero': 100, 'utg': 95, 'mp': 98}
        }
        
        scenario.questions = [
            {
                'question': 'What is the optimal play here?',
                'options': ['Fold', 'Call', '3-bet to 10-12BB', 'All-in'],
                'correct': 2
            },
            {
                'question': 'What is the main reason to 3-bet in this spot?',
                'options': [
                    'To build a bigger pot',
                    'To make opponents fold and win now',
                    'To isolate one player',
                    'To show strength'
                ],
                'correct': 1
            }
        ]
        
        return scenario
    
    @staticmethod
    def generate_three_bet_pot() -> TrainingScenario:
        """Generate a 3-bet pot scenario"""
        scenario = TrainingScenario(ScenarioType.THREE_BET_POT)
        scenario.description = (
            "You 3-bet preflop from CO, BB calls. You're in position "
            "in a 3-bet pot with initiative."
        )
        
        deck = Deck()
        random.shuffle(deck.cards)
        hole_cards = deck.cards[:2]
        flop = deck.cards[2:5]
        
        scenario.setup = {
            'position': 'CO (in position)',
            'hole_cards': [str(c) for c in hole_cards],
            'board': [str(c) for c in flop],
            'pot_size': '20BB',
            'stack_sizes': {'hero': 80, 'villain': 82},
            'action': 'Villain checks to you'
        }
        
        scenario.questions = [
            {
                'question': 'What is your continuation bet frequency in 3-bet pots?',
                'options': ['25-40%', '50-65%', '75-85%', '100%'],
                'correct': 2
            },
            {
                'question': 'What bet size should you use?',
                'options': ['25% pot', '33% pot', '50% pot', '75% pot'],
                'correct': 1
            }
        ]
        
        return scenario
    
    @staticmethod
    def generate_continuation_bet() -> TrainingScenario:
        """Generate a continuation bet scenario"""
        scenario = TrainingScenario(ScenarioType.CONTINUATION_BET)
        scenario.description = (
            "You raised preflop and got called. The flop comes and "
            "your opponent checks to you."
        )
        
        deck = Deck()
        random.shuffle(deck.cards)
        hole_cards = deck.cards[:2]
        flop = deck.cards[2:5]
        
        scenario.setup = {
            'position': 'Button',
            'hole_cards': [str(c) for c in hole_cards],
            'board': [str(c) for c in flop],
            'pot_size': '6BB',
            'stack_sizes': {'hero': 94, 'villain': 94},
            'action': 'Villain checks'
        }
        
        scenario.questions = [
            {
                'question': 'When should you continuation bet?',
                'options': [
                    'Always',
                    'When you hit the flop',
                    'Based on board texture and position',
                    'Never'
                ],
                'correct': 2
            },
            {
                'question': 'What factors favor a continuation bet?',
                'options': [
                    'Dry board, in position',
                    'Wet board, out of position',
                    'Multiple opponents',
                    'Deep stacks only'
                ],
                'correct': 0
            }
        ]
        
        return scenario
    
    @staticmethod
    def generate_check_raise() -> TrainingScenario:
        """Generate a check-raise scenario"""
        scenario = TrainingScenario(ScenarioType.CHECK_RAISE)
        scenario.description = (
            "You're out of position and check. Your opponent bets. "
            "You have a strong hand - should you check-raise?"
        )
        
        deck = Deck()
        random.shuffle(deck.cards)
        hole_cards = deck.cards[:2]
        flop = deck.cards[2:5]
        
        scenario.setup = {
            'position': 'Big Blind (out of position)',
            'hole_cards': [str(c) for c in hole_cards],
            'board': [str(c) for c in flop],
            'pot_size': '6BB',
            'stack_sizes': {'hero': 94, 'villain': 96},
            'action': 'You check, villain bets 4BB'
        }
        
        scenario.questions = [
            {
                'question': 'When is check-raising most effective?',
                'options': [
                    'With any strong hand',
                    'With strong hands and bluffs (polarized)',
                    'Only with the nuts',
                    'Only as a bluff'
                ],
                'correct': 1
            }
        ]
        
        return scenario
    
    @staticmethod
    def generate_flush_draw() -> TrainingScenario:
        """Generate a flush draw scenario"""
        scenario = TrainingScenario(ScenarioType.FLUSH_DRAW)
        scenario.description = (
            "You have a flush draw on the flop. How should you play it?"
        )
        
        # Create a flush draw scenario
        deck = Deck()
        suit = random.choice(list(Suit))
        
        # Give hero 2 cards of the same suit
        cards_of_suit = [c for c in deck.cards if c.suit == suit]
        hole_cards = random.sample(cards_of_suit, 2)
        
        # Flop has 2 cards of that suit
        remaining_suit_cards = [c for c in cards_of_suit if c not in hole_cards]
        flop_suit_cards = random.sample(remaining_suit_cards, 2)
        
        # Add one card of different suit
        other_cards = [c for c in deck.cards if c.suit != suit]
        flop = flop_suit_cards + [random.choice(other_cards)]
        random.shuffle(flop)
        
        scenario.setup = {
            'position': 'Button',
            'hole_cards': [str(c) for c in hole_cards],
            'board': [str(c) for c in flop],
            'pot_size': '8BB',
            'stack_sizes': {'hero': 92, 'villain': 92},
            'action': 'Villain bets 6BB'
        }
        
        scenario.questions = [
            {
                'question': 'What are your approximate odds of hitting the flush?',
                'options': ['~19% (turn only)', '~35% (by river)', '~50%', '~67%'],
                'correct': 1
            },
            {
                'question': 'How should you typically play a flush draw?',
                'options': [
                    'Always fold',
                    'Always call',
                    'Mix of calls, raises, and folds based on equity',
                    'Always raise'
                ],
                'correct': 2
            }
        ]
        
        return scenario
    
    @staticmethod
    def generate_river_bluff() -> TrainingScenario:
        """Generate a river bluff scenario"""
        scenario = TrainingScenario(ScenarioType.RIVER_BLUFF)
        scenario.description = (
            "The river comes and you missed your draw. Should you bluff?"
        )
        
        deck = Deck()
        random.shuffle(deck.cards)
        hole_cards = deck.cards[:2]
        board = deck.cards[2:7]
        
        scenario.setup = {
            'position': 'Cutoff',
            'hole_cards': [str(c) for c in hole_cards],
            'board': [str(c) for c in board],
            'pot_size': '30BB',
            'stack_sizes': {'hero': 70, 'villain': 75},
            'action': 'Villain checks river'
        }
        
        scenario.questions = [
            {
                'question': 'What factors favor a river bluff?',
                'options': [
                    'Large pot, credible story, opponent likely weak',
                    'Small pot, no history',
                    'Opponent is calling station',
                    'You always bluff rivers'
                ],
                'correct': 0
            },
            {
                'question': 'What bet size is typically best for river bluffs?',
                'options': ['25% pot', '50% pot', '66-75% pot', 'All-in'],
                'correct': 2
            }
        ]
        
        return scenario
    
    @staticmethod
    def generate_scenario(scenario_type: ScenarioType = None) -> TrainingScenario:
        """Generate a random scenario or a specific type"""
        if scenario_type is None:
            scenario_type = random.choice(list(ScenarioType))
        
        generators = {
            ScenarioType.SQUEEZE_PLAY: ScenarioGenerator.generate_squeeze_play,
            ScenarioType.THREE_BET_POT: ScenarioGenerator.generate_three_bet_pot,
            ScenarioType.CONTINUATION_BET: ScenarioGenerator.generate_continuation_bet,
            ScenarioType.CHECK_RAISE: ScenarioGenerator.generate_check_raise,
            ScenarioType.FLUSH_DRAW: ScenarioGenerator.generate_flush_draw,
            ScenarioType.RIVER_BLUFF: ScenarioGenerator.generate_river_bluff,
        }
        
        generator = generators.get(scenario_type)
        if generator:
            return generator()
        else:
            return ScenarioGenerator.generate_continuation_bet()
    
    @staticmethod
    def list_scenario_types() -> List[str]:
        """List all available scenario types"""
        return [s.value for s in ScenarioType]


# Quick test
if __name__ == '__main__':
    print("Testing scenario generation...")
    
    scenario = ScenarioGenerator.generate_squeeze_play()
    print(f"\nScenario Type: {scenario.scenario_type.value}")
    print(f"Description: {scenario.description}")
    print(f"Setup: {scenario.setup}")
    print(f"Questions: {len(scenario.questions)}")
    
    scenario = ScenarioGenerator.generate_flush_draw()
    print(f"\nScenario Type: {scenario.scenario_type.value}")
    print(f"Setup: {scenario.setup}")
