"""
nash_train.py - Nash Equilibrium Trainer using Counterfactual Regret Minimization (CFR)

This module implements a simplified CFR algorithm for poker strategy training.
Players learn optimal strategies through self-play by minimizing regret.
"""

import random
import numpy as np
from equity_sim import range_vs_range, parse_range
from poker_engine import Card, Deck

# Try to import PyTorch, fall back to NumPy if not available
try:
    import torch
    USE_TORCH = True
except ImportError:
    USE_TORCH = False
    print("Warning: PyTorch not available, using NumPy arrays instead")

# Actions
FOLD, CALL, RAISE = 0, 1, 2
ACTION_NAMES = ['FOLD', 'CALL', 'RAISE']


class Player:
    """
    A poker player with a regret-matching based strategy.
    Uses CFR to learn optimal play through self-play.
    """
    
    def __init__(self, player_id=0):
        self.player_id = player_id
        
        if USE_TORCH:
            self.strategy = torch.zeros(3) + 1/3  # uniform start
            self.regret_sum = torch.zeros(3)
            self.strategy_sum = torch.zeros(3)
        else:
            self.strategy = np.ones(3) / 3  # uniform start
            self.regret_sum = np.zeros(3)
            self.strategy_sum = np.zeros(3)
    
    def get_strategy(self):
        """
        Get current strategy using regret matching.
        Positive regrets become the strategy; normalize to probabilities.
        """
        if USE_TORCH:
            strat = torch.maximum(self.regret_sum, torch.zeros_like(self.regret_sum))
            total = strat.sum()
            if total > 0:
                strat = strat / total
            else:
                strat = torch.ones(3) / 3  # uniform if all regrets are zero
            self.strategy = strat
            self.strategy_sum += strat
            return strat.detach().numpy()
        else:
            strat = np.maximum(self.regret_sum, 0)
            total = strat.sum()
            if total > 0:
                strat = strat / total
            else:
                strat = np.ones(3) / 3  # uniform if all regrets are zero
            self.strategy = strat
            self.strategy_sum += strat
            return strat
    
    def update_regret(self, action_utilities):
        """
        Update cumulative regrets based on counterfactual utilities.
        
        Args:
            action_utilities: Array of utilities for each action
        """
        if USE_TORCH:
            if not isinstance(action_utilities, torch.Tensor):
                action_utilities = torch.tensor(action_utilities, dtype=torch.float32)
            # Regret = utility of action - utility of chosen action
            avg_utility = (action_utilities * self.strategy).sum()
            regrets = action_utilities - avg_utility
            self.regret_sum += regrets
        else:
            # Regret = utility of action - utility of chosen action
            avg_utility = np.dot(action_utilities, self.strategy)
            regrets = action_utilities - avg_utility
            self.regret_sum += regrets
    
    def get_average_strategy(self):
        """Get the average strategy over all iterations (Nash equilibrium approximation)"""
        if USE_TORCH:
            total = self.strategy_sum.sum()
            if total > 0:
                return (self.strategy_sum / total).detach().numpy()
            else:
                return np.ones(3) / 3
        else:
            total = self.strategy_sum.sum()
            if total > 0:
                return self.strategy_sum / total
            else:
                return np.ones(3) / 3


def simulate_game(p1, p2, hand1, hand2, bb=1, ante=0.1):
    """
    Simulate a simplified poker game between two players.
    
    Args:
        p1: Player 1 (acting player)
        p2: Player 2 (opponent)
        hand1: Player 1's hand (e.g., 'AKs')
        hand2: Player 2's hand (e.g., 'QQ')
        bb: Big blind size
        ante: Ante size
    
    Returns:
        (p1_payoff, p2_payoff): Tuple of payoffs for each player (zero-sum)
    """
    # Initial pot and investments
    pot = 2 * bb + 2 * ante
    p1_invested = bb + ante
    p2_invested = bb + ante
    
    # Player 1 acts
    strategy = p1.get_strategy()
    action = np.random.choice([FOLD, CALL, RAISE], p=strategy)
    
    # FOLD: P1 loses their investment, P2 wins the pot
    if action == FOLD:
        p1_profit = -p1_invested
        p2_profit = p1_invested
        return p1_profit, p2_profit
    
    # CALL: Go to showdown with current pot (no additional betting)
    if action == CALL:
        # No additional investment needed (P1 already posted BB)
        
        # Generate random board for showdown
        deck = Deck()
        board_cards = random.sample(deck.cards, 5)
        board_strs = [str(c) for c in board_cards]
        
        # Calculate equity
        try:
            equity_result = range_vs_range(hand1, hand2, board_strs, trials=1000)
            eq1 = equity_result['hand1_equity'] / 100.0
        except:
            # Fallback: random outcome
            eq1 = 0.5
        
        # Determine winner based on equity (probabilistic)
        if random.random() < eq1:
            # P1 wins the pot
            p1_profit = pot - p1_invested
            p2_profit = -p2_invested
        else:
            # P2 wins the pot
            p1_profit = -p1_invested
            p2_profit = pot - p2_invested
        
        return p1_profit, p2_profit
    
    # RAISE: P1 raises, assume P2 calls (simplified)
    if action == RAISE:
        raise_size = bb * 2.5
        p1_invested += raise_size
        pot += raise_size
        
        # P2 calls (simplified - in full CFR, P2 would also have a strategy)
        p2_invested += raise_size
        pot += raise_size
        
        # Generate random board for showdown
        deck = Deck()
        board_cards = random.sample(deck.cards, 5)
        board_strs = [str(c) for c in board_cards]
        
        # Calculate equity
        try:
            equity_result = range_vs_range(hand1, hand2, board_strs, trials=1000)
            eq1 = equity_result['hand1_equity'] / 100.0
        except:
            eq1 = 0.5
        
        # Determine winner
        if random.random() < eq1:
            # P1 wins the pot
            p1_profit = pot - p1_invested
            p2_profit = -p2_invested
        else:
            # P2 wins the pot
            p1_profit = -p1_invested
            p2_profit = pot - p2_invested
        
        return p1_profit, p2_profit
    
    return 0, 0


def calculate_action_utilities(p1, p2, hand1, hand2, bb=1, ante=0.1, simulations=10):
    """
    Calculate the expected utility for each action by simulation.
    
    Args:
        p1: Player 1
        p2: Player 2
        hand1: Player 1's hand
        hand2: Player 2's hand
        bb: Big blind size
        ante: Ante size
        simulations: Number of simulations per action
    
    Returns:
        Array of utilities for [FOLD, CALL, RAISE]
    """
    utilities = np.zeros(3)
    
    # For each action, simulate multiple times
    for action_idx in range(3):
        total_utility = 0
        for _ in range(simulations):
            # Temporarily force this action
            old_strategy = p1.strategy.copy()
            if USE_TORCH:
                p1.strategy = torch.zeros(3)
                p1.strategy[action_idx] = 1.0
            else:
                p1.strategy = np.zeros(3)
                p1.strategy[action_idx] = 1.0
            
            # Simulate game
            payoff, _ = simulate_game(p1, p2, hand1, hand2, bb, ante)
            total_utility += payoff
            
            # Restore strategy
            p1.strategy = old_strategy
        
        utilities[action_idx] = total_utility / simulations
    
    return utilities


def train(pop_size=10, iterations=1000, verbose=True):
    """
    Train a population of players using CFR.
    
    Args:
        pop_size: Number of players in the population
        iterations: Number of training iterations
        verbose: Whether to print progress
    
    Returns:
        List of trained players
    """
    # Initialize population
    players = [Player(i) for i in range(pop_size)]
    
    # Hand ranges for sampling
    hand_pool = ['AA', 'KK', 'QQ', 'JJ', 'TT', '99', 
                 'AKs', 'AKo', 'AQs', 'AQo', 
                 'JTs', '98s', 'T9s', '87s']
    
    for iteration in range(iterations):
        # Sample two players
        p1, p2 = random.sample(players, 2)
        
        # Sample hands
        h1 = random.choice(hand_pool)
        h2 = random.choice(hand_pool)
        
        # Calculate counterfactual utilities for each action
        action_utilities = calculate_action_utilities(p1, p2, h1, h2, simulations=5)
        
        # Update regrets
        p1.update_regret(action_utilities)
        
        # Optionally update p2 as well (symmetric game)
        action_utilities_p2 = calculate_action_utilities(p2, p1, h2, h1, simulations=5)
        p2.update_regret(action_utilities_p2)
        
        # Print progress
        if verbose and (iteration + 1) % 100 == 0:
            avg_strategy = players[0].get_average_strategy()
            print(f"Iteration {iteration + 1}/{iterations}")
            print(f"  Player 0 avg strategy: FOLD={avg_strategy[0]:.3f}, "
                  f"CALL={avg_strategy[1]:.3f}, RAISE={avg_strategy[2]:.3f}")
    
    return players


def evaluate_player(player, num_games=100):
    """
    Evaluate a player's strategy by playing against a random opponent.
    
    Args:
        player: The player to evaluate
        num_games: Number of games to play
    
    Returns:
        Average payoff per game
    """
    opponent = Player()
    total_payoff = 0
    
    hand_pool = ['AA', 'KK', 'QQ', 'AKs', 'JJ']
    
    for _ in range(num_games):
        h1 = random.choice(hand_pool)
        h2 = random.choice(hand_pool)
        payoff, _ = simulate_game(player, opponent, h1, h2)
        total_payoff += payoff
    
    return total_payoff / num_games


if __name__ == '__main__':
    print("=" * 60)
    print("Nash Equilibrium Trainer - CFR for Poker")
    print("=" * 60)
    print()
    
    # Train players
    print("Training players with CFR...")
    trained_players = train(pop_size=5, iterations=500, verbose=True)
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    
    # Show final strategies
    print("\nFinal Average Strategies (Nash Equilibrium Approximation):")
    for i, player in enumerate(trained_players):
        avg_strat = player.get_average_strategy()
        print(f"Player {i}: FOLD={avg_strat[0]:.3f}, "
              f"CALL={avg_strat[1]:.3f}, RAISE={avg_strat[2]:.3f}")
    
    # Evaluate
    print("\n" + "=" * 60)
    print("Evaluation (avg payoff vs random opponent):")
    for i, player in enumerate(trained_players[:3]):  # Just first 3
        avg_payoff = evaluate_player(player, num_games=50)
        print(f"Player {i}: {avg_payoff:.2f} BB per game")
