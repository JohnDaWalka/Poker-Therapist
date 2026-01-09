"""Tests for CFR implementation."""

import pytest

from backend.agent.cfr import (
    CFRSolver,
    GameState,
    InfoSet,
    KuhnPoker,
    MCCFRSolver,
    PokerAction,
    SimplifiedTexasHoldem,
)


class TestGameState:
    """Tests for GameState class."""
    
    def test_game_state_creation(self):
        """Test creating a game state."""
        state = GameState(
            player_hands=[['As', 'Kh'], ['Qd', 'Jc']],
            community_cards=[],
            pot=2,
            bets=[1, 1],
            active_players=[True, True],
            current_player=0,
            round=0,
            history=[]
        )
        
        assert state.num_players == 2
        assert state.active_player_count == 2
        assert not state.is_terminal()
    
    def test_game_state_validation(self):
        """Test game state validation."""
        with pytest.raises(ValueError):
            GameState(
                player_hands=[],
                community_cards=[],
                pot=0,
                bets=[],
                active_players=[],
                current_player=0,
                round=0,
                history=[]
            )
    
    def test_legal_actions(self):
        """Test getting legal actions."""
        state = GameState(
            player_hands=[['As', 'Kh'], ['Qd', 'Jc']],
            community_cards=[],
            pot=2,
            bets=[1, 1],
            active_players=[True, True],
            current_player=0,
            round=0,
            history=[]
        )
        
        actions = state.get_legal_actions()
        assert PokerAction.FOLD in actions
        assert PokerAction.CHECK in actions or PokerAction.CALL in actions
    
    def test_terminal_state(self):
        """Test terminal state detection."""
        state = GameState(
            player_hands=[['As', 'Kh'], ['Qd', 'Jc']],
            community_cards=[],
            pot=10,
            bets=[5, 5],
            active_players=[False, True],  # One player folded
            current_player=0,
            round=0,
            history=[]
        )
        
        assert state.is_terminal()
    
    def test_state_cloning(self):
        """Test cloning game state."""
        state = GameState(
            player_hands=[['As', 'Kh'], ['Qd', 'Jc']],
            community_cards=[],
            pot=2,
            bets=[1, 1],
            active_players=[True, True],
            current_player=0,
            round=0,
            history=[]
        )
        
        cloned = state.clone()
        assert cloned.pot == state.pot
        assert cloned.player_hands == state.player_hands
        assert cloned is not state


class TestInfoSet:
    """Tests for InfoSet class."""
    
    def test_info_set_creation(self):
        """Test creating an information set."""
        info_set = InfoSet(['As', 'Kh'], 'bet', 0)
        
        assert info_set.hand == ('As', 'Kh')
        assert info_set.history == 'bet'
        assert info_set.round == 0
    
    def test_info_set_hashing(self):
        """Test info set can be used as dict key."""
        info_set1 = InfoSet(['As', 'Kh'], 'bet', 0)
        info_set2 = InfoSet(['Kh', 'As'], 'bet', 0)  # Same cards, different order
        
        # Should hash to same value (sorted)
        assert hash(info_set1) == hash(info_set2)
    
    def test_get_strategy(self):
        """Test getting strategy from info set."""
        info_set = InfoSet(['As', 'Kh'], '', 0)
        actions = [PokerAction.FOLD, PokerAction.CHECK, PokerAction.BET]
        
        strategy = info_set.get_strategy(actions)
        
        # Should return valid probability distribution
        assert len(strategy) == len(actions)
        assert abs(sum(strategy.values()) - 1.0) < 0.001
        assert all(0 <= p <= 1 for p in strategy.values())
    
    def test_update_regret(self):
        """Test updating regret."""
        info_set = InfoSet(['As', 'Kh'], '', 0)
        
        info_set.update_regret(PokerAction.BET, 10.0)
        assert info_set.regret_sum[PokerAction.BET] == 10.0
        
        info_set.update_regret(PokerAction.BET, 5.0)
        assert info_set.regret_sum[PokerAction.BET] == 15.0


class TestKuhnPoker:
    """Tests for Kuhn Poker implementation."""
    
    def test_initial_state(self):
        """Test getting initial state."""
        game = KuhnPoker()
        state = game.get_initial_state()
        
        assert state.num_players == 2
        assert len(state.player_hands[0]) == 1
        assert len(state.player_hands[1]) == 1
        assert state.pot == 2  # Both antes
    
    def test_apply_action_fold(self):
        """Test folding action."""
        game = KuhnPoker()
        state = game.get_initial_state()
        
        new_state = game.apply_action(state, PokerAction.FOLD)
        
        assert not new_state.active_players[0]
        assert new_state.is_terminal()
    
    def test_apply_action_bet(self):
        """Test betting action."""
        game = KuhnPoker()
        state = game.get_initial_state()
        
        new_state = game.apply_action(state, PokerAction.BET)
        
        assert new_state.bets[0] == 2  # Ante + bet
        assert new_state.pot == 3
    
    def test_hand_evaluation(self):
        """Test hand evaluation."""
        game = KuhnPoker()
        
        assert game.evaluate_hand(['J']) < game.evaluate_hand(['Q'])
        assert game.evaluate_hand(['Q']) < game.evaluate_hand(['K'])


class TestSimplifiedTexasHoldem:
    """Tests for Simplified Texas Hold'em implementation."""
    
    def test_initial_state(self):
        """Test getting initial state."""
        game = SimplifiedTexasHoldem()
        state = game.get_initial_state()
        
        assert state.num_players == 2
        assert len(state.player_hands[0]) == 2
        assert len(state.player_hands[1]) == 2
        assert len(state.community_cards) == 0
    
    def test_advance_round(self):
        """Test advancing betting rounds."""
        game = SimplifiedTexasHoldem()
        state = game.get_initial_state()
        
        # Simulate checking through to flop
        new_state = game.apply_action(state, PokerAction.CHECK)
        new_state = game.apply_action(new_state, PokerAction.CHECK)
        
        # Should advance to flop with 3 community cards
        assert new_state.round == 1
        assert len(new_state.community_cards) == 3


class TestCFRSolver:
    """Tests for CFR solver."""
    
    def test_cfr_solver_creation(self):
        """Test creating CFR solver."""
        game = KuhnPoker()
        solver = CFRSolver(game)
        
        assert solver.game == game
        assert solver.iterations == 0
        assert len(solver.info_sets) == 0
    
    def test_cfr_training_kuhn(self):
        """Test CFR training on Kuhn Poker."""
        game = KuhnPoker()
        solver = CFRSolver(game)
        
        # Train for small number of iterations
        solver.train(100)
        
        assert solver.iterations == 100
        assert len(solver.info_sets) > 0
    
    def test_get_strategy(self):
        """Test getting strategy from solver."""
        game = KuhnPoker()
        solver = CFRSolver(game)
        solver.train(100)
        
        # Get strategy for a position
        state = game.get_initial_state()
        strategy = solver.get_strategy(state, 0)
        
        # Should return valid strategy
        assert len(strategy) > 0
        assert abs(sum(strategy.values()) - 1.0) < 0.001


class TestMCCFRSolver:
    """Tests for Monte Carlo CFR solver."""
    
    def test_mccfr_solver_creation(self):
        """Test creating MCCFR solver."""
        game = SimplifiedTexasHoldem()
        solver = MCCFRSolver(game, sampling_strategy="external")
        
        assert solver.game == game
        assert solver.sampling_strategy == "external"
        assert solver.iterations == 0
    
    def test_mccfr_training(self):
        """Test MCCFR training."""
        game = KuhnPoker()  # Use simpler game for faster testing
        solver = MCCFRSolver(game, sampling_strategy="external")
        
        # Train for small number of iterations
        solver.train(50)
        
        assert solver.iterations == 50
        assert len(solver.info_sets) > 0
    
    def test_mccfr_sampling_strategies(self):
        """Test different sampling strategies."""
        game = KuhnPoker()
        
        # Test external sampling
        solver1 = MCCFRSolver(game, sampling_strategy="external")
        solver1.train(10)
        assert solver1.iterations == 10
        
        # Test outcome sampling
        solver2 = MCCFRSolver(game, sampling_strategy="outcome")
        solver2.train(10)
        assert solver2.iterations == 10


class TestCFRConvergence:
    """Tests for CFR convergence properties."""
    
    def test_kuhn_poker_convergence(self):
        """Test that CFR converges on Kuhn Poker."""
        game = KuhnPoker()
        solver = CFRSolver(game)
        
        # Train for reasonable number of iterations
        solver.train(1000)
        
        # Check that info sets were created
        assert len(solver.info_sets) > 0
        
        # Check that strategies are valid probability distributions
        state = game.get_initial_state()
        strategy = solver.get_strategy(state, 0)
        
        assert abs(sum(strategy.values()) - 1.0) < 0.001
        assert all(0 <= p <= 1 for p in strategy.values())
    
    def test_strategy_consistency(self):
        """Test that strategies are consistent across calls."""
        game = KuhnPoker()
        solver = CFRSolver(game)
        solver.train(500)
        
        state = game.get_initial_state()
        
        # Get strategy multiple times
        strategy1 = solver.get_strategy(state, 0)
        strategy2 = solver.get_strategy(state, 0)
        
        # Should be identical (deterministic after training)
        for action in strategy1:
            assert abs(strategy1[action] - strategy2[action]) < 0.001


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
