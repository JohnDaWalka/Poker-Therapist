"""CFR solver implementations (Vanilla CFR and Monte Carlo CFR)."""

import random
from typing import Dict, List, Optional

from .game_state import GameState, InfoSet, PokerAction


class CFRSolver:
    """Vanilla Counterfactual Regret Minimization solver."""
    
    def __init__(self, game):
        """Initialize CFR solver.
        
        Args:
            game: Game instance (KuhnPoker or SimplifiedTexasHoldem)
        """
        self.game = game
        self.info_sets: Dict[str, InfoSet] = {}
        self.iterations = 0
    
    def get_info_set(self, state: GameState, player: int) -> InfoSet:
        """Get or create information set for current state.
        
        Args:
            state: Current game state
            player: Player index
            
        Returns:
            InfoSet object
        """
        # Create info set key from player's observable information
        hand = state.player_hands[player]
        history = self._get_history_string(state)
        round_num = state.round
        
        key = f"{player}:{tuple(sorted(hand))}:{history}:{round_num}"
        
        if key not in self.info_sets:
            self.info_sets[key] = InfoSet(hand, history, round_num)
        
        return self.info_sets[key]
    
    def _get_history_string(self, state: GameState) -> str:
        """Convert action history to string.
        
        Args:
            state: Game state
            
        Returns:
            History string
        """
        return "".join([
            f"{player}{action.value[0]}"  # e.g., "0b" for player 0 bet
            for player, action, _ in state.history
        ])
    
    def train(self, iterations: int) -> None:
        """Train CFR solver for specified iterations.
        
        Args:
            iterations: Number of iterations to run
        """
        for i in range(iterations):
            # Start from initial state
            state = self.game.get_initial_state()
            
            # Run CFR for each player
            for player in range(state.num_players):
                self._cfr(state, player, 1.0, 1.0)
            
            self.iterations += 1
            
            if (i + 1) % 1000 == 0:
                print(f"Completed {i + 1} iterations")
    
    def _cfr(
        self,
        state: GameState,
        player: int,
        reach_prob_player: float,
        reach_prob_opponent: float
    ) -> float:
        """Recursive CFR algorithm.
        
        Args:
            state: Current game state
            player: Player whose regrets we're computing
            reach_prob_player: Probability player reaches this state
            reach_prob_opponent: Probability opponent reaches this state
            
        Returns:
            Expected utility for player at this state
        """
        # Terminal state
        if state.is_terminal():
            return state.get_utility(player)
        
        # Not player's turn - recurse with opponent's action
        if state.current_player != player:
            info_set = self.get_info_set(state, state.current_player)
            actions = state.get_legal_actions()
            strategy = info_set.get_strategy(actions)
            
            value = 0.0
            for action in actions:
                next_state = self.game.apply_action(state, action)
                
                # Update reach probabilities
                if state.current_player == player:
                    value += strategy[action] * self._cfr(
                        next_state, player,
                        reach_prob_player * strategy[action],
                        reach_prob_opponent
                    )
                else:
                    value += strategy[action] * self._cfr(
                        next_state, player,
                        reach_prob_player,
                        reach_prob_opponent * strategy[action]
                    )
            
            return value
        
        # Player's turn - compute counterfactual values
        info_set = self.get_info_set(state, player)
        actions = state.get_legal_actions()
        strategy = info_set.get_strategy(actions)
        
        # Compute value for each action
        action_values = {}
        node_value = 0.0
        
        for action in actions:
            next_state = self.game.apply_action(state, action)
            action_values[action] = self._cfr(
                next_state, player,
                reach_prob_player * strategy[action],
                reach_prob_opponent
            )
            node_value += strategy[action] * action_values[action]
        
        # Update regrets
        for action in actions:
            regret = action_values[action] - node_value
            info_set.update_regret(action, reach_prob_opponent * regret)
        
        return node_value
    
    def get_strategy(self, state: GameState, player: int) -> Dict[PokerAction, float]:
        """Get recommended strategy for current state.
        
        Args:
            state: Current game state
            player: Player index
            
        Returns:
            Strategy dict mapping actions to probabilities
        """
        info_set = self.get_info_set(state, player)
        actions = state.get_legal_actions()
        return info_set.get_average_strategy(actions)
    
    def get_exploitability(self) -> float:
        """Calculate exploitability of current strategy.
        
        Lower exploitability means closer to Nash Equilibrium.
        
        Returns:
            Exploitability value
        """
        # Simplified exploitability calculation
        # In full implementation, would compute best response
        return 0.0


class MCCFRSolver(CFRSolver):
    """Monte Carlo CFR solver for improved efficiency."""
    
    def __init__(self, game, sampling_strategy: str = "external"):
        """Initialize MCCFR solver.
        
        Args:
            game: Game instance
            sampling_strategy: Sampling strategy ("external", "outcome", "chance")
        """
        super().__init__(game)
        self.sampling_strategy = sampling_strategy
    
    def train(self, iterations: int) -> None:
        """Train MCCFR solver with sampling.
        
        Args:
            iterations: Number of iterations to run
        """
        for i in range(iterations):
            # Sample initial state (includes chance events like card deals)
            state = self.game.get_initial_state()
            
            # Run MCCFR for each player
            for player in range(state.num_players):
                if self.sampling_strategy == "external":
                    self._external_sampling_cfr(state, player)
                elif self.sampling_strategy == "outcome":
                    self._outcome_sampling_cfr(state, player)
                else:
                    # Fallback to vanilla CFR
                    self._cfr(state, player, 1.0, 1.0)
            
            self.iterations += 1
            
            if (i + 1) % 1000 == 0:
                print(f"Completed {i + 1} MCCFR iterations")
    
    def _external_sampling_cfr(
        self,
        state: GameState,
        player: int,
        sample_prob: float = 1.0
    ) -> float:
        """MCCFR with external sampling (sample opponent actions).
        
        Args:
            state: Current game state
            player: Player whose regrets we're computing
            sample_prob: Sampling probability
            
        Returns:
            Sampled utility value
        """
        # Terminal state
        if state.is_terminal():
            return state.get_utility(player) / sample_prob
        
        actions = state.get_legal_actions()
        
        # Player's turn
        if state.current_player == player:
            info_set = self.get_info_set(state, player)
            strategy = info_set.get_strategy(actions)
            
            # Compute value for each action
            action_values = {}
            node_value = 0.0
            
            for action in actions:
                next_state = self.game.apply_action(state, action)
                action_values[action] = self._external_sampling_cfr(
                    next_state, player, sample_prob
                )
                node_value += strategy[action] * action_values[action]
            
            # Update regrets
            for action in actions:
                regret = action_values[action] - node_value
                info_set.update_regret(action, regret)
            
            return node_value
        
        # Opponent's turn - sample one action
        else:
            info_set = self.get_info_set(state, state.current_player)
            strategy = info_set.get_strategy(actions)
            
            # Sample action according to strategy
            action = self._sample_action(actions, strategy)
            next_state = self.game.apply_action(state, action)
            
            return self._external_sampling_cfr(
                next_state, player, sample_prob * strategy[action]
            )
    
    def _outcome_sampling_cfr(
        self,
        state: GameState,
        player: int
    ) -> float:
        """MCCFR with outcome sampling (sample all players' actions).
        
        Args:
            state: Current game state
            player: Player whose regrets we're computing
            
        Returns:
            Sampled utility value
        """
        # Terminal state
        if state.is_terminal():
            return state.get_utility(player)
        
        actions = state.get_legal_actions()
        info_set = self.get_info_set(state, state.current_player)
        strategy = info_set.get_strategy(actions)
        
        # Sample one action
        action = self._sample_action(actions, strategy)
        next_state = self.game.apply_action(state, action)
        
        value = self._outcome_sampling_cfr(next_state, player)
        
        # Update regrets only for current player
        if state.current_player == player:
            for a in actions:
                if a == action:
                    regret = value * (1.0 - strategy[action]) / strategy[action]
                else:
                    regret = -value
                info_set.update_regret(a, regret)
        
        return value
    
    def _sample_action(
        self,
        actions: List[PokerAction],
        strategy: Dict[PokerAction, float]
    ) -> PokerAction:
        """Sample action according to strategy probabilities.
        
        Args:
            actions: Available actions
            strategy: Strategy probabilities
            
        Returns:
            Sampled action
        """
        r = random.random()
        cumulative = 0.0
        
        for action in actions:
            cumulative += strategy[action]
            if r < cumulative:
                return action
        
        # Fallback (shouldn't reach here)
        return actions[-1]
