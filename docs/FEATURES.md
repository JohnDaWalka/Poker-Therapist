# Poker Training Suite - Complete Feature Guide

## 🎯 Overview

The Poker Training Suite is a comprehensive web-based poker training platform with professional-grade tools for Texas Hold'em and Omaha poker. From basic hand evaluation to advanced GTO strategies and equity calculations, this suite has everything you need to improve your game.

## 📚 Table of Contents

1. [Basic Training Tools](#basic-training-tools)
2. [Advanced Features](#advanced-features)
3. [API Endpoints](#api-endpoints)
4. [Usage Examples](#usage-examples)
5. [Tips and Tricks](#tips-and-tricks)

---

## Basic Training Tools

### 🃏 Hand Evaluator

**Purpose**: Evaluate the strength of poker hands in real-time

**Features**:
- Support for both Texas Hold'em (2 hole cards) and Omaha (4 hole cards)
- Displays best 5-card hand and its ranking
- Random card generator for quick practice
- All 10 standard poker hand rankings supported

**How to Use**:
1. Select game type (Hold'em or Omaha)
2. Enter your hole cards (e.g., "As Kh")
3. Enter the board cards (e.g., "Ah Kd Qc Jh Ts")
4. Click "Evaluate Hand"

**Example**:
```
Hole Cards: As Ks
Board: Ah Kd Qc Jh Ts
Result: Straight (Broadway)
```

### 🔄 Board Comparison

**Purpose**: Compare how the same hand performs on different board textures

**Features**:
- Compare unlimited number of boards side-by-side
- Automatic ranking from best to worst
- Perfect for understanding board texture impact
- Works for both game types

**How to Use**:
1. Enter your hole cards
2. Add multiple boards to compare
3. Click "Compare Boards"
4. Results shown ranked by hand strength

**Example Use Cases**:
- Compare pocket aces on different flops
- Analyze how drawing hands change on different runouts
- Study board texture effects on equity

### 🎓 Training Mode

**Purpose**: Interactive quiz mode to practice hand reading

**Features**:
- Randomly generated scenarios
- Immediate feedback on your answers
- All 10 hand rankings as answer options
- Tracks correct/incorrect answers

**How to Use**:
1. Select game type
2. Click "Start New Training Session"
3. Look at your cards and the board
4. Select what you think your hand is
5. Get instant feedback

---

## Advanced Features

### 📊 Hand Range Visualizer

**Purpose**: Visual poker hand range selection and analysis

**Features**:
- Interactive 13x13 matrix representing all starting hands
- Visual distinction:
  - **Diagonal** = Pocket pairs (AA, KK, QQ, etc.)
  - **Upper triangle** = Suited hands (AKs, KQs, etc.)
  - **Lower triangle** = Offsuit hands (AKo, KQo, etc.)
- Preset ranges:
  - All pairs
  - Premium pairs (JJ+)
  - Broadway hands
  - Suited connectors
  - Ace-anything (suited/offsuit)
- Real-time combo counting

**How to Use**:
1. Navigate to Advanced Tools → Range Visualizer
2. Click on hands to add/remove from range
3. Or use preset buttons for common ranges
4. See selected range summary and combo count

**Pro Tip**: Use this to build opening ranges for different positions

### 💰 Equity Calculator

**Purpose**: Calculate win probability using Monte Carlo simulation

**Features**:
- **10,000 trial simulations** for accurate results
- Range vs range equity calculation
- Support for all betting streets (preflop, flop, turn, river)
- Fast computation (< 2 seconds)

**Equity Examples**:
| Hand 1 | Hand 2 | Equity (Preflop) |
|--------|--------|------------------|
| AA     | KK     | 82% vs 18%       |
| AKs    | QQ     | 45% vs 55%       |
| JJ     | AKo    | 55% vs 45%       |
| 77     | AK     | 53% vs 47%       |

**How to Use**:
1. Navigate to Advanced Tools → Equity Calculator
2. Enter Range 1 (e.g., "AKs" or "QQ+")
3. Enter Range 2 (e.g., "TT" or "AQo")
4. Optionally add board cards
5. Click "Calculate Equity"

**Range Notation**:
- Specific: `AA`, `KK`, `AKs`, `AKo`
- Ranges: `QQ+` (QQ and better), `77-99` (77 through 99)
- Multiple: `AA, KK, AKs, AQs` (comma-separated)

**Use Cases**:
- Preflop all-in situations
- Analyzing continuation bet spots
- Planning river bluffs
- Tournament push/fold decisions

### 🎓 GTO Trainer

**Purpose**: Learn and practice Game Theory Optimal strategies

**Available Scenarios**:
1. **Button vs Big Blind (15bb)**
   - Open size: 2.5bb
   - Frequency: 48%
   - ~90 hand combinations

2. **Button vs Big Blind (30bb)**
   - Open size: 2.5bb
   - Frequency: 45%
   - ~85 hand combinations

3. **Cutoff vs Button (100bb)**
   - Open size: 2.5bb
   - Frequency: 35%
   - ~70 hand combinations

**How to Use**:
1. Navigate to Advanced Tools → GTO Trainer
2. Select a scenario from dropdown
3. View the optimal opening range
4. Test yourself: enter a hand and check if it's in range

**Example**:
```
Scenario: Button vs BB (15bb)
Hand: 76s
Should open? YES ✓
Action: Open to 2.5bb
```

### 📈 Hand History Parser

**Purpose**: Parse and analyze poker hand histories

**Supported Sites**:
- PokerStars
- GGPoker (coming soon)

**Statistics Calculated**:
- **VPIP** (Voluntarily Put money In Pot): % of hands played
- **PFR** (Pre-Flop Raise): % of hands raised preflop
- **3-Bet %**: % of times 3-betting
- **Fold to 3-Bet**: % of times folding to a 3-bet

**How to Use**:
1. Copy hand history from your poker client
2. Navigate to Advanced Tools → Hand History
3. Paste into text area
4. Click "Parse Hand"
5. View extracted information and stats

**Example Stats**:
- **Tight Player**: VPIP 15%, PFR 12%, 3-Bet 5%
- **Aggressive Player**: VPIP 25%, PFR 20%, 3-Bet 10%
- **Loose Player**: VPIP 35%, PFR 8%, 3-Bet 3%

### 🎮 Quick HUD Overlay

**Purpose**: Lightweight heads-up display for live play

**Displayed Stats**:
- Stack size (in big blinds)
- VPIP %
- 3-Bet %

**Features**:
- Minimal, unobtrusive design
- Draggable position (left or right side)
- Auto-refresh every 5 seconds
- Color-coded stats:
  - 🟢 Green = Normal/Tight
  - 🟡 Orange = Medium/Balanced
  - 🔴 Red = Loose/Aggressive

**How to Use**:
1. Navigate to http://localhost:5000/hud
2. Position the overlay where you want it
3. Click "Move" to switch sides
4. Click "Refresh" to update stats manually

**Pro Tip**: Open in a separate browser window and keep on top of your poker table

---

## API Endpoints

All API endpoints return JSON responses.

### Basic Endpoints

#### `POST /api/evaluate`
Evaluate a poker hand

**Request**:
```json
{
  "game_type": "holdem",
  "hole_cards": ["As", "Ks"],
  "board": ["Ah", "Kd", "Qc", "Jh", "Ts"]
}
```

**Response**:
```json
{
  "game_type": "Texas Hold'em",
  "hand_rank": "Straight",
  "rank_value": 5,
  "best_hand": ["As", "Ks", "Qc", "Jh", "Ts"]
}
```

#### `POST /api/compare-boards`
Compare multiple boards

**Request**:
```json
{
  "game_type": "holdem",
  "hole_cards": ["As", "Ks"],
  "boards": [
    ["Ah", "Kh", "Qh", "Jh", "Th"],
    ["2h", "3d", "4c", "5s", "7s"]
  ]
}
```

### Advanced Endpoints

#### `POST /api/equity/range-vs-range`
Calculate equity between ranges

**Request**:
```json
{
  "range1": "AKs",
  "range2": "QQ",
  "board": ["As", "Kh", "7d"],
  "trials": 10000
}
```

**Response**:
```json
{
  "hand1_equity": 90.7,
  "hand2_equity": 9.3,
  "hand1_wins": 9070,
  "hand2_wins": 930,
  "ties": 0,
  "total_trials": 10000
}
```

#### `GET /api/gto/scenarios`
List available GTO scenarios

#### `GET /api/gto/scenario/<name>`
Get details for a specific GTO scenario

#### `POST /api/gto/check-hand`
Check if a hand should be opened in a scenario

#### `POST /api/handhistory/parse`
Parse a hand history file

#### `GET /api/range/matrix`
Get empty hand range matrix

#### `POST /api/range/preset`
Add preset range

---

## Usage Examples

### Example 1: Analyzing a Tournament Spot

**Situation**: You're on the button with 15bb, holding K♠Q♠

**Steps**:
1. Use **GTO Trainer** to check if K♠Q♠ should open in BTN vs BB (15bb)
2. If yes, use **Equity Calculator** to see your equity vs typical BB defending range
3. Calculate: `KQs` vs `77+, A9s+, ATo+, KTs+, QTs+`

**Result**: Understanding your equity helps make optimal decisions

### Example 2: Post-Flop Analysis

**Situation**: You have A♥K♥, flop comes A♠7♦3♣

**Steps**:
1. Use **Hand Evaluator** to confirm you have top pair, top kicker
2. Use **Board Comparison** to compare this flop vs A♠7♦7♣ and A♠K♠Q♠
3. See how your hand strength changes on different boards

### Example 3: Preflop Push/Fold

**Situation**: Short stack, need to know push/fold ranges

**Steps**:
1. Open **Range Visualizer**
2. Click preset "Premium Pairs"
3. Manually add strong broadways (AK, AQ)
4. Use **Equity Calculator** to test your range vs calling ranges
5. Adjust until you find optimal push range

---

## Tips and Tricks

### General Tips

1. **Start with basics**: Master the Hand Evaluator before moving to advanced tools
2. **Use random cards**: Great for drilling hand recognition
3. **Compare boards**: Understanding board texture is crucial for poker success
4. **Track stats**: Use the HUD to monitor opponent tendencies

### Equity Calculator Tips

1. **Be specific**: More precise ranges give more accurate results
2. **Use board cards**: Add known cards for post-flop equity
3. **10k trials**: Default is accurate enough; more trials = slower but more precise
4. **Save common matchups**: Write down equity for hands you frequently play

### GTO Trainer Tips

1. **Learn one position at a time**: Master button before moving to other positions
2. **Adjust for opponents**: GTO is baseline; exploit weak players
3. **Stack sizes matter**: 15bb strategy ≠ 100bb strategy
4. **Quiz yourself**: Hide the range and try to reconstruct it

### Range Visualizer Tips

1. **Build from presets**: Start with preset then customize
2. **Understand matrix**: Diagonal = pairs, above = suited, below = offsuit
3. **Count combos**: More combos = more balanced but wider range
4. **Save ranges**: Screenshot your ranges for later reference

### Hand History Tips

1. **Parse multiple hands**: More hands = more accurate stats
2. **Look for patterns**: VPIP/PFR relationship tells you player type
3. **Adjust strategy**: High 3-bet% = give them more credit
4. **Track over time**: Stats change as players adjust

---

## Performance Notes

- **Equity calculations**: ~1-2 seconds for 10,000 trials
- **Hand evaluation**: Instant (< 100ms)
- **Range visualization**: Real-time updates
- **Maximum simulations**: 100,000 (not recommended, very slow)
- **Optimal simulations**: 10,000 (good balance of speed/accuracy)

---

## Future Enhancements

Planned features:
- [ ] Multi-way equity calculator (3+ players)
- [ ] Range vs range visualization on matrix
- [ ] Export/import custom ranges
- [ ] More GTO scenarios (SB vs BB, 3-bet pots, etc.)
- [ ] GGPoker hand history support
- [ ] Advanced statistics (Agg%, WTSD%, W$SD%)
- [ ] Mobile-responsive design
- [ ] Dark mode toggle
- [ ] Hand history database
- [ ] Session tracking and progress charts

---

## Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check the README.md for basic troubleshooting
- Review this guide for detailed feature explanations

**Happy Training! 🃏**
