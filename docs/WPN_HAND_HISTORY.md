# WinningPokerNetwork (WPN) Hand History Support

This document describes the WPN hand history tracking architecture for Poker Therapist.

## Supported Sites

The WPN parser supports hand histories from all Winning Poker Network sites, including:

- **BetACR**
- **Americas Cardroom (ACR)**
- **Black Chip Poker**
- **True Poker**

## Features

### Hand History Parsing

The WPN parser (`backend/blockchain/wpn_parser.py`) extracts:

- Hand ID (Game No)
- Date/time played
- Stakes (cash game) or tournament info
- Game variant (Hold'em, Omaha, etc.)
- Hero's cards and position
- Board cards (flop, turn, river)
- Action sequences
- Pot size and winnings
- Player stacks and positions

### API Endpoints

#### Import Hand Histories

**POST** `/api/wpn/import-text`

Import hand history text directly.

Request body:
```json
{
  "user_id": "string",
  "session_id": "string (optional)",
  "hand_history_text": "string"
}
```

Response:
```json
{
  "session_id": "string",
  "imported_hands": 0,
  "skipped_hands": 0
}
```

**POST** `/api/wpn/import-file`

Import hand history from uploaded file.

Form data:
- `file`: Text file with hand histories
- `user_id`: User identifier
- `session_id`: Optional session identifier

#### Session Review

**POST** `/api/wpn/session-review`

Request AI analysis of a poker session.

Request body:
```json
{
  "user_id": "string",
  "session_id": "string",
  "max_hands": 50
}
```

Response:
```json
{
  "strategy_review": "string",
  "therapy_review": "string",
  "citations": [],
  "models": ["perplexity", "openai"]
}
```

#### List Sessions

**GET** `/api/wpn/sessions/{user_id}`

Get all sessions for a user.

Response:
```json
{
  "user_id": "string",
  "sessions": [
    {
      "session_id": "string",
      "hands": 0,
      "last_played": "2024-01-01T00:00:00"
    }
  ]
}
```

#### Get Session Hands

**GET** `/api/wpn/session/{user_id}/{session_id}?limit=200`

Retrieve all hands from a specific session.

Response:
```json
{
  "user_id": "string",
  "session_id": "string",
  "hands": [
    {
      "hand_id": "string",
      "date_played": "2024-01-01T00:00:00",
      "stakes": "$0.50/$1",
      "game_variant": "Holdem (No Limit)",
      "hole_cards": "AsKh",
      "board": "7c4hQs Ac 2d",
      "won_amount": 36.50,
      "pot_size": 36.50,
      "raw_text": "..."
    }
  ]
}
```

## Usage Examples

### Exporting Hand Histories from ACR/BetACR

1. Open the poker client
2. Go to **Game Info** > **View Hand History** > **Settings**
3. Check **"Save hand history"**
4. Hand histories are saved to:
   - Windows: `C:\AmericasCardroom\handHistory`
   - Mac: `~/Library/Application Support/AmericasCardroom/handHistory`

### Importing to Poker Therapist

#### Using Python

```python
import requests

# Read hand history file
with open("hand_history.txt", "r") as f:
    hand_text = f.read()

# Import to Poker Therapist
response = requests.post(
    "https://api.poker-therapist.com/api/wpn/import-text",
    json={
        "user_id": "my_user_id",
        "hand_history_text": hand_text
    }
)

session_id = response.json()["session_id"]
print(f"Imported {response.json()['imported_hands']} hands")
print(f"Session ID: {session_id}")
```

#### Using cURL

```bash
# Import hand history file
curl -X POST "https://api.poker-therapist.com/api/wpn/import-file" \
  -F "file=@hand_history.txt" \
  -F "user_id=my_user_id"

# Request session review
curl -X POST "https://api.poker-therapist.com/api/wpn/session-review" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "my_user_id",
    "session_id": "session_123",
    "max_hands": 50
  }'
```

### Integration with Therapy Rex

After importing hand histories, Rex (the AI poker coach) can:

1. **Analyze Your Session**: Get strategic and mental game feedback
2. **Identify Patterns**: Detect tilt triggers and decision-making patterns
3. **Track Progress**: Monitor improvements over multiple sessions
4. **Provide Coaching**: Receive personalized advice based on your play

## Hand History Format

WPN sites use a standardized text format:

```
#Game No : 123456789
***** Holdem(No Limit) - $0.50/$1 *****
Table: ACR Table 10 (Real Money)
2024/01/01 20:30:00 UTC

Seat 1: PlayerOne ($100)
Seat 2: PlayerTwo ($100)
Seat 3: Hero ($100)

PlayerOne posts small blind $0.50
PlayerTwo posts big blind $1

*** HOLE CARDS ***
Dealt to Hero [Ks Ah]
Hero raises to $3
PlayerOne calls $3
PlayerTwo folds

*** FLOP *** [7c 4h Qs]
PlayerOne checks
Hero bets $5
PlayerOne calls $5

*** TURN *** [7c 4h Qs] [Ac]
PlayerOne checks
Hero bets $14
PlayerOne calls $14

*** RIVER *** [7c 4h Qs Ac] [2d]
PlayerOne checks
Hero bets $30
PlayerOne folds

Hero wins $36.50

*** SUMMARY ***
Total pot $36.50
```

## Database Schema

WPN hands are stored in the `hand_histories` table with the following fields:

- `site`: "WinningPokerNetwork"
- `source`: "wpn_export"
- `hand_id`: Game number
- `date_played`: Timestamp from hand history
- `game_variant`: e.g., "Holdem (No Limit)"
- `stakes`: e.g., "$0.50/$1"
- `player_name`: Hero's username
- `position`: Seat number
- `hole_cards`: Hero's cards (e.g., "AsKh")
- `board`: Community cards (e.g., "7c4hQs Ac 2d")
- `actions`: Sequence of betting actions
- `won_amount`: Amount won (if applicable)
- `pot_size`: Total pot size
- `raw_text`: Original hand history text

## Testing

Run the test suite:

```bash
cd /home/runner/work/Poker-Therapist/Poker-Therapist
python -m pytest tests/test_wpn_parser.py -v
```

Expected output:
```
tests/test_wpn_parser.py::test_wpn_parse_single_hand_basic PASSED
tests/test_wpn_parser.py::test_wpn_parse_multiple_hands PASSED
tests/test_wpn_parser.py::test_wpn_parse_tournament_hand PASSED
tests/test_wpn_parser.py::test_wpn_parse_showdown_hand PASSED
tests/test_wpn_parser.py::test_wpn_parse_hand_no_showdown PASSED
tests/test_wpn_parser.py::test_wpn_split_hands PASSED
tests/test_wpn_parser.py::test_wpn_parse_omaha_hand PASSED

7 passed
```

## Comparison with CoinPoker Support

| Feature | WPN | CoinPoker |
|---------|-----|-----------|
| Hand parsing | ✅ | ✅ |
| Session tracking | ✅ | ✅ |
| AI review | ✅ | ✅ |
| On-chain verification | ❌ | ✅ |
| RNG proof verification | ❌ | ✅ |
| Multi-game support | ✅ | ✅ |

## Future Enhancements

Potential future additions:

- [ ] Player note integration
- [ ] HUD stat extraction
- [ ] Tournament result tracking
- [ ] Multi-table session analysis
- [ ] Real-time import via poker tracker integration
- [ ] Export to other analysis tools

## Support

For issues or questions:

1. Check existing issues: https://github.com/JohnDaWalka/Poker-Therapist/issues
2. Create new issue with "WPN" label
3. Include sample hand history (with sensitive info redacted)
