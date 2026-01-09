"""Game state representation for poker CFR."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


class PokerAction(Enum):
    """Possible poker actions."""
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"


@dataclass
class GameState:
    """Represents a game state in poker."""
    
    player_hands: List[List[str]]  # Cards for each player
    community_cards: List[str]  # Community cards on board
    pot: int  # Current pot size
    bets: List[int]  # Current bets for each player
    active_players: List[bool]  # Whether each player is still in hand
    current_player: int  # Index of current player to act
    round: int  # Betting round (0=preflop, 1=flop, 2=turn, 3=river)
    history: List[Tuple[int, PokerAction, Optional[int]]]  # Action history
    
    def __post_init__(self):
        """Validate game state."""
        if not self.player_hands:
            raise ValueError("Must have at least one player")
        if len(self.bets) != len(self.player_hands):
            raise ValueError("Bets length must match player count")
        if len(self.active_players) != len(self.player_hands):
            raise ValueError("Active players length must match player count")
    
    @property
    def num_players(self) -> int:
        """Return number of players."""
        return len(self.player_hands)
    
    @property
    def active_player_count(self) -> int:
        """Return number of active players."""
        return sum(self.active_players)
    
    def is_terminal(self) -> bool:
        """Check if game state is terminal."""
        # Game ends if only one player remains or all betting is complete
        if self.active_player_count <= 1:
            return True
        
        # Check if all active players have equal bets (betting round complete)
        active_bets = [bet for bet, active in zip(self.bets, self.active_players) if active]
        if len(set(active_bets)) == 1 and self.round >= 3:  # River complete
            return True
        
        return False
    
    def get_utility(self, player: int) -> float:
        """Calculate utility for a player at terminal state.
        
        Args:
            player: Player index
            
        Returns:
            Utility value (winnings)
        """
        if not self.is_terminal():
            raise ValueError("Can only calculate utility at terminal states")
        
        # If only one active player, they win the pot
        if self.active_player_count == 1:
            winner = self.active_players.index(True)
            if player == winner:
                return float(self.pot - self.bets[player])
            else:
                return float(-self.bets[player])
        
        # Otherwise, showdown - compare hands (simplified)
        # In real implementation, would use proper hand evaluator
        if self.active_players[player]:
            # Simplified: assume uniform random outcomes
            return 0.0
        else:
            return float(-self.bets[player])
    
    def get_legal_actions(self) -> List[PokerAction]:
        """Get legal actions for current player."""
        if self.is_terminal():
            return []
        
        actions = []
        current_bet = max(self.bets)
        player_bet = self.bets[self.current_player]
        
        # Can always fold
        actions.append(PokerAction.FOLD)
        
        # Can check if no bet to call
        if player_bet == current_bet:
            actions.append(PokerAction.CHECK)
        else:
            # Can call if there's a bet
            actions.append(PokerAction.CALL)
        
        # Can bet/raise
        if player_bet == current_bet:
            actions.append(PokerAction.BET)
        else:
            actions.append(PokerAction.RAISE)
        
        return actions
    
    def clone(self) -> "GameState":
        """Create a deep copy of this game state."""
        return GameState(
            player_hands=[hand.copy() for hand in self.player_hands],
            community_cards=self.community_cards.copy(),
            pot=self.pot,
            bets=self.bets.copy(),
            active_players=self.active_players.copy(),
            current_player=self.current_player,
            round=self.round,
            history=self.history.copy()
        )


class InfoSet:
    """Information set representing player's observable game state."""
    
    def __init__(self, hand: List[str], history: str, round: int):
        """Initialize information set.
        
        Args:
            hand: Player's cards
            history: Action history string
            round: Current betting round
        """
        self.hand = tuple(sorted(hand))  # Sorted tuple for hashing
        self.history = history
        self.round = round
        
        # CFR data structures
        self.regret_sum: Dict[PokerAction, float] = {}
        self.strategy_sum: Dict[PokerAction, float] = {}
        self.num_actions = 0
    
    def __hash__(self) -> int:
        """Hash for use as dictionary key."""
        return hash((self.hand, self.history, self.round))
    
    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, InfoSet):
            return False
        return (self.hand == other.hand and 
                self.history == other.history and 
                self.round == other.round)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"InfoSet(hand={self.hand}, history='{self.history}', round={self.round})"
    
    def get_strategy(self, actions: List[PokerAction]) -> Dict[PokerAction, float]:
        """Get current mixed strategy using regret matching.
        
        Args:
            actions: Available actions
            
        Returns:
            Strategy dict mapping actions to probabilities
        """
        strategy = {}
        normalizing_sum = 0.0
        
        # Calculate positive regrets
        for action in actions:
            regret = self.regret_sum.get(action, 0.0)
            strategy[action] = max(0.0, regret)
            normalizing_sum += strategy[action]
        
        # Normalize to probabilities
        if normalizing_sum > 0:
            for action in actions:
                strategy[action] /= normalizing_sum
        else:
            # Uniform random if no positive regrets
            prob = 1.0 / len(actions)
            for action in actions:
                strategy[action] = prob
        
        # Accumulate strategy for average computation
        for action in actions:
            self.strategy_sum[action] = self.strategy_sum.get(action, 0.0) + strategy[action]
        
        self.num_actions += 1
        
        return strategy
    
    def get_average_strategy(self, actions: List[PokerAction]) -> Dict[PokerAction, float]:
        """Get average strategy over all iterations.
        
        Args:
            actions: Available actions
            
        Returns:
            Average strategy dict
        """
        avg_strategy = {}
        normalizing_sum = sum(self.strategy_sum.get(a, 0.0) for a in actions)
        
        if normalizing_sum > 0:
            for action in actions:
                avg_strategy[action] = self.strategy_sum.get(action, 0.0) / normalizing_sum
        else:
            # Uniform if no data
            prob = 1.0 / len(actions)
            for action in actions:
                avg_strategy[action] = prob
        
        return avg_strategy
    
    def update_regret(self, action: PokerAction, regret: float) -> None:
        """Update regret for an action.
        
        Args:
            action: Action taken
            regret: Regret value to add
        """
        self.regret_sum[action] = self.regret_sum.get(action, 0.0) + regret
