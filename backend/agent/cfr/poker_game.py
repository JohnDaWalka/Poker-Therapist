"""Poker game implementations for CFR."""

import random
from typing import List, Optional

from .game_state import GameState, PokerAction


class KuhnPoker:
    """Kuhn Poker - a simple 3-card poker game for testing CFR.
    
    Rules:
    - 3 cards: Jack, Queen, King
    - 2 players each get 1 card
    - 1 chip ante from each player
    - First player can check or bet 1 chip
    - If check: second player can check (showdown) or bet (first player can fold or call)
    - If bet: second player can fold or call (showdown)
    - Higher card wins at showdown
    """
    
    def __init__(self):
        """Initialize Kuhn Poker game."""
        self.deck = ['J', 'Q', 'K']
        self.num_players = 2
        self.ante = 1
    
    def get_initial_state(self) -> GameState:
        """Create initial game state with random card deal.
        
        Returns:
            Initial game state
        """
        # Shuffle and deal cards
        deck = self.deck.copy()
        random.shuffle(deck)
        
        player_hands = [[deck[i]] for i in range(self.num_players)]
        
        return GameState(
            player_hands=player_hands,
            community_cards=[],
            pot=self.num_players * self.ante,
            bets=[self.ante] * self.num_players,
            active_players=[True] * self.num_players,
            current_player=0,
            round=0,
            history=[]
        )
    
    def apply_action(self, state: GameState, action: PokerAction) -> GameState:
        """Apply action to state and return new state.
        
        Args:
            state: Current game state
            action: Action to apply
            
        Returns:
            New game state after action
        """
        new_state = state.clone()
        player = state.current_player
        
        # Record action in history
        new_state.history.append((player, action, None))
        
        if action == PokerAction.FOLD:
            new_state.active_players[player] = False
            # Game ends when player folds
            return new_state
        
        elif action == PokerAction.CHECK:
            # Move to next player or end round
            if len([1 for p, a, _ in state.history if p == 0]) == 1:
                # First player checked, second player's turn
                new_state.current_player = 1
            else:
                # Both checked, showdown
                pass
        
        elif action == PokerAction.BET or action == PokerAction.CALL:
            bet_amount = 1  # Fixed bet size in Kuhn Poker
            new_state.bets[player] += bet_amount
            new_state.pot += bet_amount
            
            if action == PokerAction.BET:
                # Move to next player
                new_state.current_player = (player + 1) % self.num_players
            # else CALL ends the round (showdown)
        
        elif action == PokerAction.RAISE:
            # Not used in basic Kuhn Poker
            pass
        
        return new_state
    
    def evaluate_hand(self, cards: List[str]) -> int:
        """Evaluate hand strength for Kuhn Poker.
        
        Args:
            cards: Player's cards
            
        Returns:
            Hand strength (higher is better)
        """
        card_values = {'J': 1, 'Q': 2, 'K': 3}
        return card_values[cards[0]]
    
    def determine_winner(self, state: GameState) -> int:
        """Determine winner at showdown.
        
        Args:
            state: Terminal game state
            
        Returns:
            Winner's player index
        """
        # Find active players
        active = [i for i, a in enumerate(state.active_players) if a]
        
        if len(active) == 1:
            return active[0]
        
        # Compare hands
        strengths = [(i, self.evaluate_hand(state.player_hands[i])) for i in active]
        winner = max(strengths, key=lambda x: x[1])
        return winner[0]


class SimplifiedTexasHoldem:
    """Simplified Texas Hold'em for CFR.
    
    Simplifications:
    - Limited deck (e.g., 13 cards: A-K in one suit + one random card)
    - 2 players (heads-up)
    - Fixed bet sizes
    - Simplified betting rounds
    """
    
    def __init__(self, deck_size: int = 13):
        """Initialize simplified Texas Hold'em.
        
        Args:
            deck_size: Size of deck (default 13 for single suit)
        """
        self.num_players = 2
        self.deck_size = deck_size
        self.ante = 1
        self.bet_sizes = [2, 4, 8]  # Small, medium, big bets
        
        # Create simplified deck
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        self.deck = [f"{rank}s" for rank in ranks[:deck_size]]
    
    def get_initial_state(self) -> GameState:
        """Create initial game state.
        
        Returns:
            Initial game state with dealt cards
        """
        # Shuffle deck
        deck = self.deck.copy()
        random.shuffle(deck)
        
        # Deal 2 cards to each player
        player_hands = [
            [deck[0], deck[1]],
            [deck[2], deck[3]]
        ]
        
        # Community cards come from remaining deck
        community_cards = []
        
        return GameState(
            player_hands=player_hands,
            community_cards=community_cards,
            pot=self.num_players * self.ante,
            bets=[self.ante] * self.num_players,
            active_players=[True] * self.num_players,
            current_player=0,
            round=0,  # Preflop
            history=[]
        )
    
    def apply_action(
        self,
        state: GameState,
        action: PokerAction,
        bet_size: Optional[int] = None
    ) -> GameState:
        """Apply action to state.
        
        Args:
            state: Current game state
            action: Action to apply
            bet_size: Optional bet size (for bets/raises)
            
        Returns:
            New game state
        """
        new_state = state.clone()
        player = state.current_player
        
        # Record action
        new_state.history.append((player, action, bet_size))
        
        if action == PokerAction.FOLD:
            new_state.active_players[player] = False
            return new_state
        
        elif action == PokerAction.CHECK:
            # Advance to next player or next round
            next_player = (player + 1) % self.num_players
            
            # Check if all players have acted
            if self._all_players_acted(new_state):
                new_state = self._advance_round(new_state)
            else:
                new_state.current_player = next_player
        
        elif action == PokerAction.CALL:
            # Match current bet
            call_amount = max(state.bets) - state.bets[player]
            new_state.bets[player] += call_amount
            new_state.pot += call_amount
            
            # Check if round is complete
            if self._all_players_acted(new_state):
                new_state = self._advance_round(new_state)
            else:
                new_state.current_player = (player + 1) % self.num_players
        
        elif action == PokerAction.BET or action == PokerAction.RAISE:
            # Use provided bet size or default
            if bet_size is None:
                bet_size = self.bet_sizes[new_state.round]
            
            new_state.bets[player] += bet_size
            new_state.pot += bet_size
            new_state.current_player = (player + 1) % self.num_players
        
        return new_state
    
    def _all_players_acted(self, state: GameState) -> bool:
        """Check if all active players have acted with equal bets.
        
        Args:
            state: Game state to check
            
        Returns:
            True if round is complete
        """
        active_bets = [bet for bet, active in zip(state.bets, state.active_players) if active]
        return len(set(active_bets)) <= 1
    
    def _advance_round(self, state: GameState) -> GameState:
        """Advance to next betting round.
        
        Args:
            state: Current state
            
        Returns:
            State with next round
        """
        state.round += 1
        state.current_player = 0
        
        # Deal community cards based on round
        if state.round == 1:  # Flop
            # Deal 3 community cards
            deck = [c for c in self.deck if c not in sum(state.player_hands, [])]
            state.community_cards.extend(deck[:3])
        elif state.round == 2:  # Turn
            # Deal 1 card
            deck = [c for c in self.deck 
                   if c not in sum(state.player_hands, []) + state.community_cards]
            state.community_cards.append(deck[0])
        elif state.round == 3:  # River
            # Deal 1 card
            deck = [c for c in self.deck 
                   if c not in sum(state.player_hands, []) + state.community_cards]
            state.community_cards.append(deck[0])
        
        return state
    
    def evaluate_hand(self, hand: List[str], community: List[str]) -> int:
        """Evaluate hand strength (simplified).
        
        Args:
            hand: Player's hole cards
            community: Community cards
            
        Returns:
            Hand strength value
        """
        # Simplified evaluation: just sum card ranks
        rank_values = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
            '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
        }
        
        all_cards = hand + community
        return sum(rank_values[card[0]] for card in all_cards)
    
    def determine_winner(self, state: GameState) -> int:
        """Determine winner at showdown.
        
        Args:
            state: Terminal game state
            
        Returns:
            Winner's player index
        """
        active = [i for i, a in enumerate(state.active_players) if a]
        
        if len(active) == 1:
            return active[0]
        
        # Evaluate hands
        strengths = [
            (i, self.evaluate_hand(state.player_hands[i], state.community_cards))
            for i in active
        ]
        
        winner = max(strengths, key=lambda x: x[1])
        return winner[0]
