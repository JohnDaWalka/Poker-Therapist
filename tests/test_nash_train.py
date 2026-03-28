"""
Tests for Nash Equilibrium Trainer (nash_train.py)
"""

import sys
import numpy as np
from nash_train import Player, simulate_game, train, FOLD, CALL, RAISE


def test_player_initialization():
    """Test that a player initializes correctly"""
    print("Testing player initialization...")
    player = Player(0)
    
    # Check that strategy is uniform at start
    strategy = player.get_strategy()
    assert len(strategy) == 3, "Strategy should have 3 actions"
    assert abs(strategy.sum() - 1.0) < 0.01, "Strategy should sum to 1"
    
    print("✓ Player initialization test passed")


def test_regret_update():
    """Test that regret updates work"""
    print("\nTesting regret update...")
    player = Player(0)
    
    # Simulate some action utilities
    utilities = np.array([1.0, -0.5, 0.5])
    player.update_regret(utilities)
    
    # Check that regrets were updated
    assert player.regret_sum.sum() != 0, "Regret sum should be non-zero after update"
    
    print("✓ Regret update test passed")


def test_strategy_convergence():
    """Test that strategy changes based on regret"""
    print("\nTesting strategy convergence...")
    player = Player(0)
    
    # Repeatedly give high utility to RAISE action
    for _ in range(10):
        utilities = np.array([0.0, 0.5, 2.0])  # RAISE has highest utility
        player.update_regret(utilities)
        player.get_strategy()  # Update strategy
    
    # Check that RAISE action has high probability
    avg_strategy = player.get_average_strategy()
    assert avg_strategy[RAISE] > 0.4, f"RAISE should have high probability, got {avg_strategy[RAISE]}"
    
    print(f"  Final strategy: FOLD={avg_strategy[0]:.3f}, CALL={avg_strategy[1]:.3f}, RAISE={avg_strategy[2]:.3f}")
    print("✓ Strategy convergence test passed")


def test_simulate_game():
    """Test that simulate_game runs without errors"""
    print("\nTesting game simulation...")
    p1 = Player(0)
    p2 = Player(1)
    
    try:
        # Run a few simulations with different hand combinations
        test_hands = [
            ('AA', 'KK'),
            ('AKs', 'QQ'),
            ('JJ', 'TT')
        ]
        
        for h1, h2 in test_hands:
            payoff1, payoff2 = simulate_game(p1, p2, h1, h2)
            
            # Check that payoffs are opposite (zero-sum)
            assert abs(payoff1 + payoff2) < 0.01, f"Game should be zero-sum, got {payoff1} and {payoff2}"
        
        print("✓ Game simulation test passed")
    except Exception as e:
        print(f"✗ Game simulation test failed: {e}")
        raise


def test_short_training():
    """Test that training runs for a few iterations"""
    print("\nTesting short training run...")
    
    try:
        # Train for just 10 iterations to check it runs
        players = train(pop_size=2, iterations=10, verbose=False)
        
        assert len(players) == 2, "Should return 2 players"
        assert all(isinstance(p, Player) for p in players), "All should be Player objects"
        
        # Check that strategies have been updated
        for player in players:
            avg_strat = player.get_average_strategy()
            assert abs(avg_strat.sum() - 1.0) < 0.01, "Strategy should sum to 1"
        
        print("✓ Short training test passed")
    except Exception as e:
        print(f"✗ Training test failed: {e}")
        raise


def test_action_probabilities():
    """Test that action probabilities are valid"""
    print("\nTesting action probability validity...")
    player = Player(0)
    
    for _ in range(20):
        strategy = player.get_strategy()
        
        # Check validity
        assert len(strategy) == 3, "Should have 3 actions"
        assert all(strategy >= 0), "All probabilities should be non-negative"
        assert abs(strategy.sum() - 1.0) < 0.01, f"Probabilities should sum to 1, got {strategy.sum()}"
        
        # Update with random utilities
        utilities = np.random.randn(3)
        player.update_regret(utilities)
    
    print("✓ Action probability validity test passed")


def run_all_tests():
    """Run all test functions"""
    print("=" * 60)
    print("RUNNING NASH TRAINER TESTS")
    print("=" * 60)
    
    test_player_initialization()
    test_regret_update()
    test_strategy_convergence()
    test_simulate_game()
    test_short_training()
    test_action_probabilities()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)


if __name__ == '__main__':
    run_all_tests()
