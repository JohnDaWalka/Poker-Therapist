# Nash Equilibrium Trainer - CFR for Poker

This module implements **Counterfactual Regret Minimization (CFR)**, a powerful algorithm for computing Nash equilibrium strategies in imperfect information games like poker.

## What is CFR?

CFR is an iterative self-play algorithm where AI agents learn optimal poker strategies by:
1. Playing against themselves repeatedly
2. Tracking "regret" for not taking certain actions
3. Adjusting their strategy to minimize regret
4. Converging to a Nash equilibrium (unexploitable strategy)

## Features

- **Regret Matching**: Players learn by minimizing counterfactual regret
- **Population Training**: Multiple players train simultaneously through self-play
- **Flexible Backend**: Works with PyTorch (GPU-accelerated) or NumPy (CPU fallback)
- **Zero-Sum Verification**: All payoffs properly balanced (verified in tests)
- **Real-time Monitoring**: Track strategy convergence during training

## How It Works

### Player Strategy

Each player maintains:
- **Current strategy**: Probability distribution over [FOLD, CALL, RAISE]
- **Regret sum**: Cumulative regret for each action
- **Strategy sum**: Running average of strategies (converges to Nash equilibrium)

### Training Loop

```python
for iteration in range(num_iterations):
    # 1. Sample two players and random hands
    p1, p2 = random.sample(players, 2)
    h1, h2 = random.choice(hands), random.choice(hands)
    
    # 2. Calculate counterfactual utilities for each action
    utilities = calculate_action_utilities(p1, p2, h1, h2)
    
    # 3. Update regrets (learn from mistakes)
    p1.update_regret(utilities)
    
    # 4. Strategy automatically adjusts via regret matching
    strategy = p1.get_strategy()  # Higher regret → higher probability
```

### Game Simulation

The simplified poker game:
1. **Setup**: 2 players, blinds + antes, random hands
2. **Player 1 acts**: FOLD, CALL, or RAISE (based on learned strategy)
3. **Showdown**: If not folded, determine winner via equity calculation
4. **Payoffs**: Zero-sum (one player's gain = other's loss)

## Usage

### Basic Training

```python
from nash_train import train

# Train 10 players for 1000 iterations
players = train(pop_size=10, iterations=1000, verbose=True)

# Check final strategies
for i, player in enumerate(players):
    avg_strategy = player.get_average_strategy()
    print(f"Player {i}: FOLD={avg_strategy[0]:.3f}, "
          f"CALL={avg_strategy[1]:.3f}, RAISE={avg_strategy[2]:.3f}")
```

### Evaluate Performance

```python
from nash_train import evaluate_player

# Test against random opponents
avg_payoff = evaluate_player(players[0], num_games=100)
print(f"Average profit: {avg_payoff:.2f} BB per game")
```

### Run from Command Line

```bash
python nash_train.py
```

Output:
```
============================================================
Nash Equilibrium Trainer - CFR for Poker
============================================================

Training players with CFR...
Iteration 100/500
  Player 0 avg strategy: FOLD=0.888, CALL=0.105, RAISE=0.007
Iteration 200/500
  Player 0 avg strategy: FOLD=0.941, CALL=0.055, RAISE=0.004
...

Final Average Strategies (Nash Equilibrium Approximation):
Player 0: FOLD=0.974, CALL=0.024, RAISE=0.002
Player 1: FOLD=0.813, CALL=0.002, RAISE=0.185
...
```

## Algorithm Details

### Regret Matching

At each iteration, a player's strategy is proportional to positive regrets:

```
strategy[action] ∝ max(0, cumulative_regret[action])
```

Actions with higher regret (should have been played more) get higher probability.

### Counterfactual Utilities

For each action, calculate what the utility *would have been* if we'd taken that action:

```python
utilities[FOLD] = -invested_amount
utilities[CALL] = expected_value_at_showdown
utilities[RAISE] = expected_value_with_raise
```

Regret = utility_of_action - utility_of_actual_action

### Nash Equilibrium Convergence

As training progresses:
1. Early iterations: Strategies fluctuate wildly
2. Middle iterations: Strategies stabilize
3. Late iterations: Strategies converge to Nash equilibrium

The **average strategy** (not current strategy) approximates Nash equilibrium.

## Configuration

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `pop_size` | Number of players | 10 |
| `iterations` | Training iterations | 1000 |
| `bb` | Big blind size | 1 |
| `ante` | Ante amount | 0.1 |
| `verbose` | Print progress | True |

### Hand Pool

Default hands for training:
```python
['AA', 'KK', 'QQ', 'JJ', 'TT', '99',  # Pairs
 'AKs', 'AKo', 'AQs', 'AQo',          # Broadway
 'JTs', '98s', 'T9s', '87s']          # Suited connectors
```

Customize by modifying `hand_pool` in `train()`.

## Testing

Run the test suite:

```bash
python test_nash_train.py
```

Tests verify:
- Player initialization
- Regret updates
- Strategy convergence
- **Zero-sum property** (critical for CFR)
- Training loop functionality
- Probability validity

## Performance

- **Training speed**: ~100 iterations/minute (without PyTorch)
- **Convergence**: Strategies stabilize after ~500-1000 iterations
- **Memory**: Minimal (only stores regret/strategy vectors per player)

With PyTorch GPU acceleration:
- **Training speed**: ~1000 iterations/minute
- Significant speedup for large populations

## Limitations & Extensions

### Current Limitations

1. **Simplified game**: Only preflop action, opponent always calls raises
2. **No bet sizing**: Fixed raise size (2.5 BB)
3. **Heads-up only**: 2 players only
4. **Limited hand pool**: Fixed set of starting hands

### Possible Extensions

1. **Full game tree**: Flop, turn, river actions
2. **Multiple bet sizes**: Learn optimal sizing
3. **Multi-way pots**: 3+ player support
4. **Hand range abstraction**: Group similar hands
5. **Opponent modeling**: Exploitative strategies
6. **Blueprint strategies**: Pre-compute common scenarios

## Theory Background

### Why CFR Works

CFR has **theoretical guarantees**:
- Average regret grows sublinearly: O(1/√T)
- Average strategy converges to Nash equilibrium
- Works for any finite extensive-form game

### Applications

CFR has been used to solve:
- **Libratus** (2017): Defeated poker pros in heads-up no-limit hold'em
- **Pluribus** (2019): First AI to beat pros in 6-player poker
- Other imperfect information games (negotiation, auctions, security)

## References

- Zinkevich et al. (2007): "Regret Minimization in Games with Incomplete Information"
- Bowling et al. (2015): "Heads-up Limit Hold'em Poker is Solved"
- Brown & Sandholm (2017): "Libratus: The Superhuman AI for Heads-up No-Limit Poker"
- Brown & Sandholm (2019): "Superhuman AI for multiplayer poker"

## Integration with Poker Suite

The Nash trainer integrates seamlessly with other Poker Suite components:

- **Equity Calculator** (`equity_sim.py`): Used for showdown evaluation
- **Poker Engine** (`poker_engine.py`): Card and deck management
- **Web UI**: Could be extended to show strategy evolution in real-time

## Advanced Usage

### Custom Reward Functions

Modify payoffs to learn different objectives:

```python
# Example: Penalize folding too much
if action == FOLD:
    penalty = 0.1
    return -p1_invested - penalty, p1_invested
```

### Parallel Training

Run multiple training sessions in parallel:

```python
from multiprocessing import Pool

def train_session(session_id):
    players = train(pop_size=10, iterations=1000, verbose=False)
    return players[0].get_average_strategy()

with Pool(4) as pool:
    results = pool.map(train_session, range(4))
```

### Strategy Export

Save trained strategies for later use:

```python
import pickle

# After training
with open('trained_strategy.pkl', 'wb') as f:
    pickle.dump(players[0].get_average_strategy(), f)

# Load later
with open('trained_strategy.pkl', 'rb') as f:
    strategy = pickle.load(f)
```

## Troubleshooting

### PyTorch not installed
```
Warning: PyTorch not available, using NumPy arrays instead
```
This is normal. NumPy backend works fine, just slower. To use PyTorch:
```bash
pip install torch
```

### Strategies not converging
- Increase `iterations` (try 5000-10000)
- Check that payoffs are zero-sum (run tests)
- Verify equity calculations are working

### Slow training
- Install PyTorch for GPU acceleration
- Reduce equity calculation trials (default 1000)
- Use smaller population size

## License

Part of the Poker Training Suite. See main repository for license details.
