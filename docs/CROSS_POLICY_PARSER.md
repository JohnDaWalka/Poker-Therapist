# Cross-Policy Hand History Parser Workflow

## Overview

The cross-policy parser provides a unified interface for parsing hand histories from multiple poker platforms (ACR/WPN and CoinPoker) with consistent normalization and output formats. This enables seamless integration with AI analysis tools, database storage, and downstream processing.

## Architecture

### Components

1. **Base Parser** (`base_parser.py`)
   - Defines common data structures (`NormalizedHandHistory`, `NormalizedPlayerAction`, `BoardCards`)
   - Defines normalized action types (`NormalizedAction` enum)
   - Provides board variant detection (`BoardVariant` enum)
   - Utility functions for card normalization

2. **Cross-Policy Parser** (`cross_policy_parser.py`)
   - Platform detection (automatic or manual)
   - Conversion from platform-specific formats to normalized format
   - Unified parsing interface (`parse_hand_history()`)
   - Chroma stream generation for AI processing

3. **Platform-Specific Parsers**
   - `betacr_parser.py` - ACR/WPN (America's Card Room, Winning Poker Network)
   - `coinpoker_parser.py` - CoinPoker (blockchain-based poker platform)

## Features

### 1. Normalized Action Types

All player actions are mapped to standard `NormalizedAction` types:

| Action Type | Description | Example |
|-------------|-------------|---------|
| `FOLD` | Player folds their hand | "Player1: folds" |
| `CHECK` | Player checks | "Hero: checks" |
| `CALL` | Player calls a bet | "Hero: calls $5" |
| `RAISE` | Player raises | "Hero: raises $10 to $15" |
| `BET` | Player makes a bet | "Hero: bets $20" |
| `ALL_IN` | Player goes all-in | "Hero: calls $50 and is all-in" |
| `POST_SB` | Post small blind | "Hero: posts small blind $1" |
| `POST_BB` | Post big blind | "Hero: posts big blind $2" |
| `POST_ANTE` | Post ante | "Hero: posts ante $0.25" |
| `POST_STRADDLE` | Post straddle | "Hero: posts straddle $4" |
| `COLLECTED` | Collect pot | "Hero collected $30.00 from pot" |

### 2. Board Variant Detection

The parser automatically detects board textures for strategic analysis:

| Variant | Description | Example |
|---------|-------------|---------|
| `MONOTONE` | All cards same suit | Ah Kh Qh |
| `RAINBOW` | All different suits | Ah Kd Qs |
| `TWO_TONE` | Two suits represented | Ah Kh Qs |
| `PAIRED` | Contains a pair | Ah Ad Ks |
| `TRIPS` | Three of a kind | Ah Ad As |

### 3. Card Encoding

Cards are encoded in a standardized 2-character format:
- First character: Rank (2-9, T, J, Q, K, A)
- Second character: Suit (c, d, h, s)

Examples: `Ah` (Ace of hearts), `Kd` (King of diamonds), `9s` (Nine of spades)

### 4. Special Cases Handling

#### Straddles
```python
hand = parse_hand_history(text)[0]
if hand.has_straddle:
    print("Hand included a straddle")
```

#### Dead Cards
Dead cards are tracked in the `dead_cards` field (if present in hand history):
```python
if hand.dead_cards:
    print(f"Dead cards: {', '.join(hand.dead_cards)}")
```

#### Board Variants
```python
if hand.board and hand.board.variant:
    print(f"Board variant: {hand.board.variant}")
    if hand.board.variant == BoardVariant.MONOTONE:
        print("Flush possible!")
```

## Usage

### Basic Usage

```python
from backend.blockchain.cross_policy_parser import parse_hand_history

# Parse with automatic platform detection
text = """
Poker Hand #12345: Hold'em No Limit ($0.50/$1.00) - 2026-01-15 10:00:00 UTC
Dealt to Hero [Ah Kh]
*** FLOP *** [Qh Jh Th]
Hero collected $20.00 from pot
"""

hands = parse_hand_history(text)
hand = hands[0]

print(f"Platform: {hand.platform}")
print(f"Hand ID: {hand.hand_id}")
print(f"Hero cards: {hand.hole_cards}")
print(f"Board: {hand.board.full_board}")
print(f"Board variant: {hand.board.variant}")
print(f"Won: ${hand.won_amount}")
```

### Platform-Specific Parsing

```python
# Force parsing as ACR
hands = parse_hand_history(text, platform="ACR")

# Force parsing as CoinPoker
hands = parse_hand_history(text, platform="CoinPoker")
```

### Multiple Hands

```python
# Parse multiple hands in one text block
text_with_multiple_hands = """
Poker Hand #H1: ...
...

Poker Hand #H2: ...
...
"""

hands = parse_hand_history(text_with_multiple_hands)
for hand in hands:
    print(f"{hand.hand_id}: {hand.hole_cards} -> {hand.won_amount}")
```

### Chroma Stream Output

The chroma stream format is optimized for AI processing and vector embeddings:

```python
from backend.blockchain.cross_policy_parser import parse_many_to_chroma_stream

streams = parse_many_to_chroma_stream(text)
for stream in streams:
    print(stream)
    # {
    #   "platform": "ACR",
    #   "hand_id": "12345",
    #   "timestamp": "2026-01-15T10:00:00",
    #   "hero_cards": "AhKh",
    #   "board": "QhJhTh",
    #   "board_variant": "MONOTONE",
    #   "actions": [...],
    #   "won_amount": 20.00,
    #   ...
    # }
```

### Analyzing Actions

```python
hand = parse_hand_history(text)[0]

# Find all raises
raises = [a for a in hand.actions if a.action == NormalizedAction.RAISE]
for raise_action in raises:
    print(f"{raise_action.player_name} raised to ${raise_action.amount}")

# Check if hero went all-in
hero_all_in = any(
    a.action == NormalizedAction.ALL_IN and a.player_name == hand.hero_name
    for a in hand.actions
)
```

## Cross-Platform Mappings

### Action Normalization

Both platforms use slightly different formats for the same actions. The parser normalizes these:

| ACR Format | CoinPoker Format | Normalized |
|------------|------------------|------------|
| "Hero: folds" | "Hero: folds" | `FOLD` |
| "Hero: raises $10 to $15" | "Hero: raises 10 to 15" | `RAISE` |
| "Hero: calls $50 and is all-in" | "Hero: calls 50 and is all-in" | `ALL_IN` |
| "Hero: posts small blind $1" | "Hero: posts small blind 1" | `POST_SB` |

### Stakes Format

Stakes are normalized to a consistent format:

- ACR: `"$0.50/$1.00"` → Normalized: `"$0.50/$1.00"`
- CoinPoker: `"$0.50/$1.00"` → Normalized: `"$0.50/$1.00"`
- CoinPoker (tournament): `"160/320 ante 40"` → Normalized: `"160/320 ante 40"`

### Board Format

Board cards are stored in a structured format:

```python
board = hand.board
# board.flop: "QhJhTh" (3 cards)
# board.turn: "9h" (1 card)
# board.river: "8h" (1 card)
# board.full_board: "QhJhTh 9h 8h" (space-separated)
# board.cards_list: ["Qh", "Jh", "Th", "9h", "8h"]
```

## Test Scenarios

The test suite covers various strategic scenarios:

### 1. Premium Pairs (AA, KK, QQ)
Tests parsing hands with premium pocket pairs, including preflop aggression and postflop play.

### 2. Suited Connectors (JTs, 98s)
Tests parsing hands with suited connectors, including draw scenarios and semi-bluff spots.

### 3. Blocker Scenarios
Tests hands where hero holds blockers to opponent's potential strong hands (e.g., Ace blocker on flush board).

### 4. Multi-Board Runouts
Tests complete hand histories with flop, turn, and river cards.

### 5. Straddle Scenarios
Tests hands with straddles posted before the flop.

### 6. Tournament Hands
Tests tournament hands with antes and blinds.

### 7. All-In Scenarios
Tests hands with all-in situations and side pots.

## Platform-Specific Features

### ACR/WPN Specific
- Tournament info extraction (`tournament_id`, `buyin`)
- Game type detection (Cash Game, Tournament, SNG, MTT)
- Multiple currency support ($, €, ₮)

### CoinPoker Specific
- Blockchain transaction hash (`tx_hash`)
- RNG verification data (`rng_phrase`, `rng_combined_seed_hash`)
- Provably fair gaming support

These platform-specific fields are preserved in the `platform_specific` dictionary:

```python
hand = parse_hand_history(coinpoker_text)[0]
if hand.platform == "CoinPoker":
    tx_hash = hand.platform_specific.get("tx_hash")
    rng_phrase = hand.platform_specific.get("rng_phrase")
```

## Future Extensions

To add support for a new platform:

1. Create a new parser module (e.g., `pokerstars_parser.py`)
2. Add platform detection pattern in `cross_policy_parser.py`
3. Implement conversion function (e.g., `pokerstars_to_normalized()`)
4. Add test cases in `test_cross_policy_parser.py`
5. Update this documentation

## Error Handling

```python
from backend.blockchain.cross_policy_parser import parse_hand_history

try:
    hands = parse_hand_history(text)
except ValueError as e:
    print(f"Parsing error: {e}")
    # Could not detect platform or invalid format
```

## Performance Considerations

- Platform detection is fast (regex-based)
- Parsing is optimized for batch processing
- Large hand history files can be processed efficiently
- Memory usage scales linearly with number of hands

## Integration with Existing Code

The cross-policy parser integrates seamlessly with existing API routes:

```python
# In backend/api/routes/analyze.py
from backend.blockchain.cross_policy_parser import parse_hand_history

# Parse uploaded hand history
hands = parse_hand_history(uploaded_text)
for hand in hands:
    # Store in database
    model = HandHistory(
        hand_id=hand.hand_id,
        platform=hand.platform,
        hole_cards=hand.hole_cards,
        board=hand.board.full_board if hand.board else None,
        # ...
    )
    db.add(model)
```

## Summary

The cross-policy parser provides:
- ✅ Unified interface for ACR and CoinPoker
- ✅ Normalized action types for consistent analysis
- ✅ Board variant detection for strategic insights
- ✅ Chroma stream output for AI processing
- ✅ Comprehensive test coverage
- ✅ Easy extension for new platforms
- ✅ Preservation of platform-specific features

This enables the Poker Therapist application to handle hand histories from multiple sources with consistent quality and analysis capabilities.
