# Poker Suite v2.0 - New Features Usage Guide

## Overview

This guide covers the new features added in version 2.0 of the Poker Training Suite:

1. Multi-way equity calculator (3+ players)
2. Additional poker variants (7-Card Stud, Razz)
3. Advanced training scenarios
4. Statistics tracking and progress reports
5. Multiplayer training sessions

## 1. Multi-Way Equity Calculator

### Command Line Usage

```python
from equity_sim import multi_way_equity

# Calculate 3-way preflop equity
result = multi_way_equity(['AA', 'KK', 'QQ'], trials=10000)
print(f"AA equity: {result['equities'][0]['equity']}%")
print(f"KK equity: {result['equities'][1]['equity']}%")
print(f"QQ equity: {result['equities'][2]['equity']}%")

# With a board (post-flop)
result = multi_way_equity(
    ['AKs', 'QQ', 'JJ'], 
    ['As', 'Kh', '7d'],
    trials=10000
)
```

### API Usage

```bash
curl -X POST http://localhost:5000/api/equity/multi-way \
  -H "Content-Type: application/json" \
  -d '{
    "ranges": ["AA", "KK", "QQ"],
    "board": [],
    "trials": 10000
  }'
```

### Response Format

```json
{
  "players": 3,
  "ranges": ["AA", "KK", "QQ"],
  "total_trials": 10000,
  "ties": 12,
  "equities": [
    {"player": 1, "range": "AA", "equity": 68.5, "wins": 6850},
    {"player": 2, "range": "KK", "equity": 17.2, "wins": 1720},
    {"player": 3, "range": "QQ", "equity": 14.3, "wins": 1430}
  ]
}
```

## 2. Poker Variants

### 7-Card Stud

Evaluate the best 5-card hand from 7 cards.

```python
from poker_engine import Card, PokerGame

# Create 7 cards
cards = [Card.from_string(c) for c in ['As', 'Kh', 'Qd', 'Jc', 'Ts', '9h', '8d']]
result = PokerGame.evaluate_stud_hand(cards)

print(f"Game: {result['game_type']}")
print(f"Hand: {result['hand_rank']}")
print(f"Best 5 cards: {result['best_hand']}")
```

**API Endpoint**:
```bash
curl -X POST http://localhost:5000/api/evaluate/stud \
  -H "Content-Type: application/json" \
  -d '{
    "hole_cards": ["As", "Kh", "Qd", "Jc", "Ts", "9h", "8d"]
  }'
```

### Razz (7-Card Lowball)

In Razz, the best low hand wins. Aces are low, and straights/flushes don't count.

```python
from poker_engine import Card, PokerGame

# The wheel (A-2-3-4-5) is the best hand in Razz
cards = [Card.from_string(c) for c in ['As', '2h', '3d', '4c', '5s', 'Kh', 'Qd']]
result = PokerGame.evaluate_razz_hand(cards)

print(f"Game: {result['game_type']}")
print(f"Hand: {result['hand_rank']}")  # "A-2-3-4-5 low"
```

**API Endpoint**:
```bash
curl -X POST http://localhost:5000/api/evaluate/razz \
  -H "Content-Type: application/json" \
  -d '{
    "hole_cards": ["As", "2h", "3d", "4c", "5s", "Kh", "Qd"]
  }'
```

## 3. Advanced Training Scenarios

Practice specific poker situations with realistic scenarios.

### Available Scenario Types

1. **squeeze_play** - 3-betting when facing a raise and call(s)
2. **3bet_pot** - Playing in 3-bet pots with position
3. **continuation_bet** - C-betting as the preflop aggressor
4. **check_raise** - Check-raising out of position
5. **flush_draw** - Playing flush draws optimally
6. **river_bluff** - Bluffing on the river
7. **set_mining** - Playing small pairs to hit sets
8. **straight_draw** - Playing straight draws
9. **overcards** - Playing overcards to the board
10. **multiway_pot** - Multi-way pot dynamics

### Command Line Usage

```python
from training_scenarios import ScenarioGenerator, ScenarioType

# Generate a specific scenario
scenario = ScenarioGenerator.generate_squeeze_play()

print(f"Scenario: {scenario.scenario_type.value}")
print(f"Description: {scenario.description}")
print(f"Your hand: {scenario.setup['hole_cards']}")
print(f"Action: {scenario.setup['action']}")

# Show questions
for i, question in enumerate(scenario.questions):
    print(f"\nQ{i+1}: {question['question']}")
    for j, option in enumerate(question['options']):
        print(f"  {j+1}. {option}")

# Generate random scenario
random_scenario = ScenarioGenerator.generate_scenario()
```

### API Usage

**List available scenarios**:
```bash
curl http://localhost:5000/api/scenarios/list
```

**Generate a scenario**:
```bash
curl -X POST http://localhost:5000/api/scenarios/generate \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_type": "flush_draw"
  }'
```

**Check an answer**:
```bash
curl -X POST http://localhost:5000/api/scenarios/check-answer \
  -H "Content-Type: application/json" \
  -d '{
    "question_index": 0,
    "answer": 2,
    "correct_answer": 2,
    "user_id": "john_doe"
  }'
```

## 4. Statistics Tracking

Track your training progress and performance over time.

### Command Line Usage

```python
from statistics_tracker import StatisticsTracker

tracker = StatisticsTracker()

# Record a training session
tracker.record_training_session('john_doe', {
    'game_type': 'holdem',
    'correct': True,
    'hand_type': 'straight',
    'duration': 45
})

# Record equity calculation
tracker.record_equity_calculation('john_doe', 'holdem', 2)

# Record GTO decision
tracker.record_gto_decision('john_doe', 'BTN_vs_BB_15bb', True)

# Get progress report
report = tracker.get_user_report('john_doe')
print(f"Accuracy: {report['summary']['overall_accuracy']}%")
print(f"Sessions: {report['summary']['total_training_sessions']}")
```

### API Usage

**Get user statistics**:
```bash
curl http://localhost:5000/api/stats/user/john_doe
```

**Response**:
```json
{
  "user_id": "john_doe",
  "summary": {
    "total_training_sessions": 45,
    "overall_accuracy": 87.5,
    "total_hands_evaluated": 120,
    "correct_evaluations": 105,
    "equity_calculations": 23
  },
  "gto_training": {
    "scenarios_practiced": 8,
    "total_decisions": 62,
    "correct_decisions": 51,
    "accuracy": 82.3
  },
  "performance_by_hand_type": {
    "flush": {"total": 15, "correct": 14, "accuracy": 93.3},
    "straight": {"total": 12, "correct": 11, "accuracy": 91.7}
  },
  "recent_sessions": [...]
}
```

**Record a session**:
```bash
curl -X POST http://localhost:5000/api/stats/record-session \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "john_doe",
    "game_type": "holdem",
    "correct": true,
    "hand_type": "flush",
    "duration": 30
  }'
```

**Get global statistics**:
```bash
curl http://localhost:5000/api/stats/global
```

## 5. Multiplayer Training Sessions

Train with friends or other players in collaborative sessions.

### Command Line Usage

```python
from statistics_tracker import MultiplayerSessionManager

manager = MultiplayerSessionManager()

# Player 1 creates a session
session_id = manager.create_session('player1', 'equity', max_players=3)
print(f"Created session: {session_id}")

# Player 2 joins
result = manager.join_session(session_id, 'player2')
print(f"Joined: {result['success']}")

# Player 3 joins
manager.join_session(session_id, 'player3')

# Start the session
manager.start_session(session_id)

# Get session details
session = manager.get_session(session_id)
print(f"Players: {session['players']}")
print(f"Status: {session['status']}")

# Record results
manager.record_result(session_id, 'player1', {'score': 95, 'time': 120})
manager.record_result(session_id, 'player2', {'score': 88, 'time': 135})

# End session
results = manager.end_session(session_id)
print(f"Final results: {results}")
```

### API Usage

**Create session**:
```bash
curl -X POST http://localhost:5000/api/multiplayer/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "player1",
    "session_type": "equity",
    "max_players": 3
  }'
```

**List available sessions**:
```bash
curl http://localhost:5000/api/multiplayer/list
```

**Join session**:
```bash
curl -X POST http://localhost:5000/api/multiplayer/join \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "mp_1234",
    "user_id": "player2"
  }'
```

**Start session**:
```bash
curl -X POST http://localhost:5000/api/multiplayer/start/mp_1234
```

**Get session details**:
```bash
curl http://localhost:5000/api/multiplayer/session/mp_1234
```

**Record result**:
```bash
curl -X POST http://localhost:5000/api/multiplayer/record-result \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "mp_1234",
    "user_id": "player1",
    "result": {"score": 95, "time": 120}
  }'
```

**End session**:
```bash
curl -X POST http://localhost:5000/api/multiplayer/end/mp_1234
```

## Complete Example: Training Session Workflow

Here's a complete example of a training workflow using all new features:

```python
from equity_sim import multi_way_equity
from training_scenarios import ScenarioGenerator
from statistics_tracker import stats_tracker, multiplayer_manager

# 1. Calculate multi-way equity
print("=== Multi-Way Equity ===")
equity = multi_way_equity(['AA', 'KK', 'QQ'], trials=5000)
for player_equity in equity['equities']:
    print(f"{player_equity['range']}: {player_equity['equity']}%")

# Record it
stats_tracker.record_equity_calculation('user1', 'holdem', 3)

# 2. Practice a scenario
print("\n=== Training Scenario ===")
scenario = ScenarioGenerator.generate_flush_draw()
print(f"Scenario: {scenario.description}")
print(f"Your cards: {scenario.setup['hole_cards']}")
print(f"Board: {scenario.setup['board']}")

# User answers questions...
correct = True  # Assume correct answer
stats_tracker.record_training_session('user1', {
    'game_type': 'holdem',
    'correct': correct,
    'hand_type': 'flush_draw',
    'duration': 60
})

# 3. Check progress
print("\n=== Progress Report ===")
report = stats_tracker.get_user_report('user1')
print(f"Overall accuracy: {report['summary']['overall_accuracy']}%")
print(f"Total sessions: {report['summary']['total_training_sessions']}")

# 4. Start multiplayer session
print("\n=== Multiplayer Session ===")
session_id = multiplayer_manager.create_session('user1', 'equity')
multiplayer_manager.join_session(session_id, 'user2')
multiplayer_manager.start_session(session_id)
print(f"Started multiplayer session: {session_id}")
```

## Running the Server

Start the server with all new features enabled:

```bash
python poker_server.py
```

The server will be available at `http://localhost:5000` with all endpoints active.

## Testing

Run the comprehensive test suite:

```bash
python test_new_features.py
```

This tests all new features including:
- Multi-way equity calculations
- Stud and Razz evaluations
- Scenario generation
- Statistics tracking
- Multiplayer sessions

## Tips and Best Practices

1. **Multi-way equity**: Use at least 5000 trials for accurate results
2. **Training scenarios**: Practice multiple scenarios per session for better learning
3. **Statistics**: Review your progress report weekly to identify weak areas
4. **Multiplayer**: Coordinate with friends for regular training sessions
5. **Variants**: Master Hold'em before moving to Stud and Razz

## Troubleshooting

**Stats not saving?**
- Check that the application has write permissions
- Verify `stats_data.json` is being created in the app directory

**Multiplayer session full?**
- Default max is 4 players; increase when creating session

**Slow equity calculations?**
- Reduce `trials` parameter (minimum 1000 recommended)
- Consider using fewer players or ranges

## Next Steps

- Explore the web interface at `http://localhost:5000`
- Try different training scenarios
- Track your progress over time
- Challenge friends to multiplayer sessions
- Master different poker variants

Happy training! 🃏
