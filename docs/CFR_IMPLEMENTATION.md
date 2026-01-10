# CFR (Counterfactual Regret Minimization) Implementation

## Overview

This implementation provides a complete CFR-based poker AI system that can compute Game Theory Optimal (GTO) strategies using the Counterfactual Regret Minimization algorithm.

## What is CFR?

Counterfactual Regret Minimization (CFR) is a powerful algorithm for solving imperfect-information games like poker. It works by:

1. **Self-Play**: The algorithm plays against itself repeatedly
2. **Regret Tracking**: It tracks "regret" for not taking each action
3. **Strategy Refinement**: Over many iterations, it adjusts strategies to minimize cumulative regret
4. **Nash Equilibrium**: Eventually converges to a Nash Equilibrium strategy

### Key Concepts

- **Information Set**: Represents all possible game states that look identical to a player (due to hidden information)
- **Regret**: The difference between the value of an action taken and the best action in hindsight
- **Counterfactual Regret**: Regret calculated assuming the player reached a specific information set
- **Nash Equilibrium**: A strategy profile where no player can improve by unilaterally changing their strategy

## Architecture

### Core Components

```
backend/agent/cfr/
├── __init__.py              # Module exports
├── game_state.py            # Game state representation
├── cfr_solver.py           # CFR and MCCFR solvers
└── poker_game.py           # Poker game implementations

backend/agent/
└── cfr_service.py          # High-level CFR service

backend/api/routes/
└── cfr.py                  # REST API endpoints
```

### Components Description

#### 1. Game State (`game_state.py`)

- **GameState**: Represents a poker game state with players, cards, bets, and history
- **InfoSet**: Represents an information set with regret tracking
- **PokerAction**: Enum of possible poker actions (fold, check, call, bet, raise)

#### 2. CFR Solvers (`cfr_solver.py`)

- **CFRSolver**: Vanilla CFR implementation that traverses the full game tree
- **MCCFRSolver**: Monte Carlo CFR with sampling for improved efficiency
  - External sampling: Samples opponent actions
  - Outcome sampling: Samples all players' actions

#### 3. Poker Games (`poker_game.py`)

- **KuhnPoker**: Simple 3-card poker (J, Q, K) for testing CFR
- **SimplifiedTexasHoldem**: Heads-up Hold'em with simplified deck and betting

#### 4. CFR Service (`cfr_service.py`)

High-level service providing:
- Model training and persistence
- Strategy queries
- Strategic advice
- Hand evaluation

## Usage

### Training CFR Models

Train models via API:

```bash
# Train Kuhn Poker
curl -X POST http://localhost:8000/api/cfr/train \
  -H "Content-Type: application/json" \
  -d '{"game": "kuhn_poker", "iterations": 10000}'

# Train Simplified Hold'em
curl -X POST http://localhost:8000/api/cfr/train \
  -H "Content-Type: application/json" \
  -d '{"game": "holdem", "iterations": 5000}'
```

Or programmatically:

```python
from backend.agent.cfr_service import CFRService

service = CFRService()

# Train Kuhn Poker
result = service.train_kuhn_poker(iterations=10000)
print(f"Trained with {result['info_sets']} information sets")

# Train Hold'em
result = service.train_holdem(iterations=5000)
```

### Getting Strategy Advice

#### Kuhn Poker

```bash
curl -X POST http://localhost:8000/api/cfr/strategy/kuhn \
  -H "Content-Type: application/json" \
  -d '{
    "player_card": "K",
    "history": ""
  }'
```

Response:
```json
{
  "success": true,
  "strategy": {
    "fold": 0.0,
    "check": 0.3,
    "bet": 0.7
  },
  "explanation": "Strategy based on CFR Nash equilibrium approximation"
}
```

#### Texas Hold'em

```bash
curl -X POST http://localhost:8000/api/cfr/strategy/holdem \
  -H "Content-Type: application/json" \
  -d '{
    "hand": ["As", "Kh"],
    "community_cards": ["Qd", "Jc", "Tc"],
    "pot": 100,
    "bets": [50, 50],
    "history": ""
  }'
```

Response:
```json
{
  "success": true,
  "advice": {
    "recommended_action": "bet",
    "action_probabilities": {
      "fold": 0.05,
      "call": 0.25,
      "bet": 0.70
    },
    "strategy_type": "GTO (Game Theory Optimal)",
    "exploitability": "Low - based on CFR Nash equilibrium approximation"
  }
}
```

#### Strategic Advice

```bash
curl -X POST http://localhost:8000/api/cfr/advice \
  -H "Content-Type: application/json" \
  -d '{
    "hand": ["As", "Kh"],
    "community_cards": ["Qd", "Jc", "Tc"],
    "pot": 100,
    "position": "BTN",
    "opponent_tendency": "aggressive"
  }'
```

Response includes:
- Hand strength evaluation
- Position advantage
- Pot odds analysis
- CFR insights
- Exploitative adjustments

### Python API

```python
from backend.agent.cfr import CFRSolver, KuhnPoker
from backend.agent.cfr_service import CFRService

# Low-level CFR usage
game = KuhnPoker()
solver = CFRSolver(game)
solver.train(iterations=10000)

state = game.get_initial_state()
strategy = solver.get_strategy(state, player=0)
print(f"Strategy: {strategy}")

# High-level service usage
service = CFRService()
advice = service.get_strategic_advice(
    hand=["As", "Kh"],
    community_cards=["Qd", "Jc", "Tc"],
    pot=100,
    position="BTN"
)
print(f"Advice: {advice}")
```

## API Endpoints

### POST /api/cfr/train
Train a CFR model.

**Request:**
```json
{
  "game": "kuhn_poker" | "holdem",
  "iterations": 10000
}
```

### POST /api/cfr/strategy/kuhn
Get Kuhn Poker strategy.

**Request:**
```json
{
  "player_card": "J" | "Q" | "K",
  "history": "action_history_string"
}
```

### POST /api/cfr/strategy/holdem
Get Hold'em strategy advice.

**Request:**
```json
{
  "hand": ["As", "Kh"],
  "community_cards": ["Qd", "Jc", "Tc"],
  "pot": 100,
  "bets": [50, 50],
  "history": ""
}
```

### POST /api/cfr/advice
Get strategic advice.

**Request:**
```json
{
  "hand": ["As", "Kh"],
  "community_cards": ["Qd", "Jc", "Tc"],
  "pot": 100,
  "position": "BTN",
  "opponent_tendency": "aggressive"
}
```

### GET /api/cfr/status
Get CFR model status.

### GET /api/cfr/info
Get CFR implementation information.

## Technical Details

### CFR Algorithm

The vanilla CFR algorithm works as follows:

1. Start from root of game tree
2. For each information set:
   - Compute counterfactual values for each action
   - Update regrets based on action values vs node value
   - Use regret matching to compute next strategy
3. Repeat for many iterations
4. Average strategy converges to Nash Equilibrium

### Monte Carlo CFR (MCCFR)

MCCFR improves efficiency by sampling:

- **External Sampling**: Only sample opponent actions, traverse all own actions
- **Outcome Sampling**: Sample one action for all players
- **Chance Sampling**: Sample chance events (card deals)

This reduces computational cost per iteration while maintaining convergence properties.

### Information Set Abstraction

For large games like Texas Hold'em, we use:

1. **Card Abstraction**: Group similar hands together
2. **Action Abstraction**: Limit bet sizes
3. **Bucketing**: Cluster similar game states

The simplified Hold'em implementation uses a reduced deck size for tractability.

## Performance

### Kuhn Poker
- **Convergence**: ~10,000 iterations
- **Training Time**: ~10 seconds
- **Information Sets**: ~12 (small game)
- **Nash Equilibrium**: Provably converges

### Simplified Texas Hold'em
- **Convergence**: ~50,000 iterations (depends on abstraction)
- **Training Time**: ~5 minutes (MCCFR with external sampling)
- **Information Sets**: Hundreds to thousands (depends on deck size)
- **Approximation**: Close to GTO for simplified game

## Testing

Run CFR tests:

```bash
pytest tests/test_cfr.py -v
```

Test coverage includes:
- Game state representation
- Information set management
- CFR solver training
- MCCFR sampling strategies
- Strategy convergence
- API endpoints

## Integration with Rex

The CFR implementation integrates with Rex (the poker coach) to provide:

1. **GTO Strategy Recommendations**: Based on CFR-computed equilibrium strategies
2. **Hand Analysis**: Evaluate hand strength and optimal actions
3. **Exploitability Analysis**: Assess how exploitable a strategy is
4. **Strategic Insights**: Explain CFR principles in coaching sessions

### Example Integration

```python
# In chatbot or API handler
from backend.agent.cfr_service import CFRService

service = CFRService()

# User asks about their hand
user_hand = ["As", "Kh"]
community = ["Qd", "Jc", "Tc"]

advice = service.get_strategic_advice(
    hand=user_hand,
    community_cards=community,
    pot=100,
    position="BTN",
    opponent_tendency="tight-passive"
)

# Rex can now provide CFR-based coaching
response = f"""
Based on CFR analysis:
- Hand Strength: {advice['hand_strength']}
- Position: {advice['position_advantage']}
- Recommended: {advice.get('exploitative_adjustments', [])}
"""
```

## Future Enhancements

Potential improvements:

1. **Full Texas Hold'em**: Implement complete Hold'em with full deck
2. **Better Abstraction**: More sophisticated card and action abstraction
3. **CFR+**: Implement CFR+ variant for faster convergence
4. **Linear CFR**: Implement Linear CFR for better performance
5. **Multi-way Pots**: Extend to 3+ player scenarios
6. **Real-time Advice**: Optimize for low-latency strategy queries
7. **Strategy Visualization**: Visualize equilibrium strategies
8. **Opponent Modeling**: Combine CFR with exploitative adjustments

## References

- [Zinkevich et al. (2007): "Regret Minimization in Games with Incomplete Information"](http://poker.cs.ualberta.ca/publications/NIPS07-cfr.pdf)
- [Lanctot et al. (2009): "Monte Carlo Sampling for Regret Minimization in Extensive Games"](http://mlanctot.info/files/papers/nips09mccfr.pdf)
- [Bowling et al. (2015): "Heads-up Limit Hold'em Poker is Solved"](http://science.sciencemag.org/content/347/6218/145)

## License

Part of the Poker Therapist project. See LICENSE for details.
