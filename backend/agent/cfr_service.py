"""CFR service for providing poker strategy advice."""

import json
import os
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from backend.agent.cfr import (
    CFRSolver,
    GameState,
    KuhnPoker,
    MCCFRSolver,
    PokerAction,
    SimplifiedTexasHoldem,
)


class CFRService:
    """Service for CFR-based poker strategy advice."""
    
    def __init__(self, model_dir: str = "models/cfr"):
        """Initialize CFR service.
        
        Args:
            model_dir: Directory to store trained models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.kuhn_solver: Optional[CFRSolver] = None
        self.holdem_solver: Optional[MCCFRSolver] = None
        
        # Load pre-trained models if available
        self._load_models()
    
    def _load_models(self) -> None:
        """Load pre-trained CFR models."""
        kuhn_path = self.model_dir / "kuhn_poker.pkl"
        holdem_path = self.model_dir / "holdem.pkl"
        
        try:
            if kuhn_path.exists():
                with open(kuhn_path, 'rb') as f:
                    self.kuhn_solver = pickle.load(f)
                print(f"Loaded Kuhn Poker model ({self.kuhn_solver.iterations} iterations)")
        except Exception as e:
            print(f"Failed to load Kuhn Poker model: {e}")
        
        try:
            if holdem_path.exists():
                with open(holdem_path, 'rb') as f:
                    self.holdem_solver = pickle.load(f)
                print(f"Loaded Hold'em model ({self.holdem_solver.iterations} iterations)")
        except Exception as e:
            print(f"Failed to load Hold'em model: {e}")
    
    def _save_models(self) -> None:
        """Save trained CFR models."""
        if self.kuhn_solver:
            kuhn_path = self.model_dir / "kuhn_poker.pkl"
            with open(kuhn_path, 'wb') as f:
                pickle.dump(self.kuhn_solver, f)
            print(f"Saved Kuhn Poker model")
        
        if self.holdem_solver:
            holdem_path = self.model_dir / "holdem.pkl"
            with open(holdem_path, 'wb') as f:
                pickle.dump(self.holdem_solver, f)
            print(f"Saved Hold'em model")
    
    def train_kuhn_poker(self, iterations: int = 10000) -> Dict[str, any]:
        """Train CFR on Kuhn Poker.
        
        Args:
            iterations: Number of training iterations
            
        Returns:
            Training results dict
        """
        print(f"Training Kuhn Poker CFR for {iterations} iterations...")
        
        game = KuhnPoker()
        self.kuhn_solver = CFRSolver(game)
        self.kuhn_solver.train(iterations)
        
        # Save trained model
        self._save_models()
        
        return {
            "game": "kuhn_poker",
            "iterations": iterations,
            "info_sets": len(self.kuhn_solver.info_sets),
            "exploitability": self.kuhn_solver.get_exploitability()
        }
    
    def train_holdem(self, iterations: int = 5000) -> Dict[str, any]:
        """Train MCCFR on simplified Texas Hold'em.
        
        Args:
            iterations: Number of training iterations
            
        Returns:
            Training results dict
        """
        print(f"Training Hold'em MCCFR for {iterations} iterations...")
        
        game = SimplifiedTexasHoldem()
        self.holdem_solver = MCCFRSolver(game, sampling_strategy="external")
        self.holdem_solver.train(iterations)
        
        # Save trained model
        self._save_models()
        
        return {
            "game": "simplified_holdem",
            "iterations": iterations,
            "info_sets": len(self.holdem_solver.info_sets),
            "exploitability": self.holdem_solver.get_exploitability()
        }
    
    def get_kuhn_strategy(
        self,
        player_card: str,
        history: str
    ) -> Dict[str, float]:
        """Get strategy for Kuhn Poker position.
        
        Args:
            player_card: Player's card (J, Q, or K)
            history: Action history string
            
        Returns:
            Strategy dict with action probabilities
        """
        if not self.kuhn_solver:
            return {"error": "Kuhn Poker model not trained"}
        
        # Create game state
        game = KuhnPoker()
        state = GameState(
            player_hands=[[player_card], ['?']],  # Opponent card unknown
            community_cards=[],
            pot=2,  # Both players ante'd
            bets=[1, 1],
            active_players=[True, True],
            current_player=0,
            round=0,
            history=self._parse_history(history)
        )
        
        strategy = self.kuhn_solver.get_strategy(state, 0)
        
        # Convert to readable format
        return {
            action.value: prob
            for action, prob in strategy.items()
        }
    
    def get_holdem_advice(
        self,
        hand: List[str],
        community_cards: List[str],
        pot: int,
        bets: List[int],
        history: str
    ) -> Dict[str, any]:
        """Get strategy advice for Hold'em position.
        
        Args:
            hand: Player's hole cards
            community_cards: Community cards
            pot: Current pot size
            bets: Current bets for each player
            history: Action history
            
        Returns:
            Strategy advice dict
        """
        if not self.holdem_solver:
            return {"error": "Hold'em model not trained"}
        
        # Determine betting round
        round_num = 0
        if len(community_cards) >= 3:
            round_num = 1  # Flop
        if len(community_cards) >= 4:
            round_num = 2  # Turn
        if len(community_cards) >= 5:
            round_num = 3  # River
        
        # Create game state
        state = GameState(
            player_hands=[hand, ['?', '?']],  # Opponent cards unknown
            community_cards=community_cards,
            pot=pot,
            bets=bets,
            active_players=[True, True],
            current_player=0,
            round=round_num,
            history=self._parse_history(history)
        )
        
        strategy = self.holdem_solver.get_strategy(state, 0)
        
        # Convert to readable format with recommendations
        action_probs = {
            action.value: prob
            for action, prob in strategy.items()
        }
        
        # Find recommended action
        recommended_action = max(strategy.items(), key=lambda x: x[1])[0]
        
        return {
            "recommended_action": recommended_action.value,
            "action_probabilities": action_probs,
            "strategy_type": "GTO (Game Theory Optimal)",
            "exploitability": "Low - based on CFR Nash equilibrium approximation"
        }
    
    def get_strategic_advice(
        self,
        hand: List[str],
        community_cards: List[str],
        pot: int,
        position: str,
        opponent_tendency: Optional[str] = None
    ) -> Dict[str, any]:
        """Get high-level strategic advice using CFR principles.
        
        Args:
            hand: Player's hole cards
            community_cards: Community cards
            pot: Current pot size
            position: Position (BTN, SB, BB, etc.)
            opponent_tendency: Optional opponent tendency info
            
        Returns:
            Strategic advice dict
        """
        advice = {
            "hand_strength": self._evaluate_hand_strength(hand, community_cards),
            "position_advantage": self._evaluate_position(position),
            "pot_odds_analysis": self._calculate_pot_odds(pot),
            "cfr_insights": []
        }
        
        # Add CFR-based insights
        if self.holdem_solver:
            advice["cfr_insights"].append(
                "Strategy based on CFR Nash equilibrium approximation"
            )
            advice["cfr_insights"].append(
                f"Model trained with {self.holdem_solver.iterations} iterations"
            )
        
        # Add exploitative adjustments if opponent tendency provided
        if opponent_tendency:
            advice["exploitative_adjustments"] = self._get_exploitative_adjustments(
                opponent_tendency
            )
        
        return advice
    
    def _parse_history(self, history: str) -> List[Tuple[int, PokerAction, Optional[int]]]:
        """Parse action history string.
        
        Args:
            history: History string (e.g., "0b1c" = player 0 bet, player 1 call)
            
        Returns:
            List of (player, action, amount) tuples
        """
        actions = []
        action_map = {
            'f': PokerAction.FOLD,
            'c': PokerAction.CHECK,
            'k': PokerAction.CALL,
            'b': PokerAction.BET,
            'r': PokerAction.RAISE
        }
        
        i = 0
        while i < len(history):
            if history[i].isdigit():
                player = int(history[i])
                if i + 1 < len(history):
                    action_char = history[i + 1].lower()
                    action = action_map.get(action_char, PokerAction.CHECK)
                    actions.append((player, action, None))
                    i += 2
                else:
                    i += 1
            else:
                i += 1
        
        return actions
    
    def _evaluate_hand_strength(self, hand: List[str], community: List[str]) -> str:
        """Evaluate hand strength category.
        
        Args:
            hand: Player's cards
            community: Community cards
            
        Returns:
            Strength description
        """
        # Simplified hand strength evaluation
        rank_values = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
            '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
        }
        
        hand_ranks = [rank_values.get(card[0], 0) for card in hand]
        avg_rank = sum(hand_ranks) / len(hand_ranks)
        
        if avg_rank >= 12:
            return "Premium (AA, KK, QQ, AK)"
        elif avg_rank >= 10:
            return "Strong (JJ, AQ, KQ)"
        elif avg_rank >= 8:
            return "Medium (99, AJ, KJ)"
        else:
            return "Weak (speculative)"
    
    def _evaluate_position(self, position: str) -> str:
        """Evaluate position advantage.
        
        Args:
            position: Position string
            
        Returns:
            Position evaluation
        """
        if position.upper() in ['BTN', 'BUTTON']:
            return "Excellent - act last post-flop"
        elif position.upper() in ['CO', 'CUTOFF']:
            return "Good - late position"
        elif position.upper() in ['MP', 'MIDDLE']:
            return "Neutral - middle position"
        else:
            return "Disadvantaged - early position"
    
    def _calculate_pot_odds(self, pot: int) -> Dict[str, float]:
        """Calculate pot odds information.
        
        Args:
            pot: Current pot size
            
        Returns:
            Pot odds dict
        """
        return {
            "pot_size": pot,
            "pot_odds_ratio": "2:1",  # Simplified
            "required_equity": 0.33  # Simplified
        }
    
    def _get_exploitative_adjustments(self, tendency: str) -> List[str]:
        """Get exploitative adjustments based on opponent tendency.
        
        Args:
            tendency: Opponent tendency description
            
        Returns:
            List of adjustment recommendations
        """
        adjustments = []
        
        if "aggressive" in tendency.lower():
            adjustments.append("Consider calling down lighter against aggressive opponents")
            adjustments.append("Value bet thinner as they pay off more")
        
        if "passive" in tendency.lower():
            adjustments.append("Bluff more frequently against passive opponents")
            adjustments.append("Size your value bets larger")
        
        if "tight" in tendency.lower():
            adjustments.append("Steal blinds more frequently")
            adjustments.append("Fold to aggression without strong hands")
        
        if "loose" in tendency.lower():
            adjustments.append("Tighten your range")
            adjustments.append("Value bet more hands")
        
        return adjustments or ["Play GTO strategy - no clear tendency identified"]
