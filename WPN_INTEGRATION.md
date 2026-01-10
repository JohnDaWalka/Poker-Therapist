# WPN / America's Cardroom Integration

## Overview

Poker Therapist now supports cross-interoperability with **Winning Poker Network (WPN)** sites, including:
- **America's Cardroom (ACR)** - via BEtAcr.exe client
- **BlackChip Poker**
- **YaPoker**
- Other WPN network sites

This integration allows you to import hand histories from these sites for AI-powered poker coaching and therapy sessions with Rex.

## Features

- ✅ **Hand History Parsing** - Parse WPN hand history text files
- ✅ **Session Import** - Import entire poker sessions
- ✅ **AI-Powered Review** - Get strategic and psychological reviews from Rex
- ✅ **Session Management** - Track and review multiple sessions
- ✅ **Multi-format Support** - Supports both cash game and tournament formats

## How to Use

### 1. Export Hand Histories from WPN

From your poker client (e.g., BEtAcr.exe):

1. Go to **Game Info** → **View Hand History**
2. Select the hands you want to export
3. Save them to a text file

### 2. Import Hand Histories

#### Via API (JSON)

```bash
curl -X POST "http://localhost:8000/api/wpn/import-text" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your_user_id",
    "session_id": "optional_session_id",
    "hand_history_text": "***** Hand History for Game 1234567890 *****..."
  }'
```

#### Via API (File Upload)

```bash
curl -X POST "http://localhost:8000/api/wpn/import-file" \
  -F "file=@hand_history.txt" \
  -F "user_id=your_user_id"
```

### 3. Review Your Session

```bash
curl -X POST "http://localhost:8000/api/wpn/session-review" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your_user_id",
    "session_id": "your_session_id",
    "max_hands": 50
  }'
```

### 4. List Your Sessions

```bash
curl -X GET "http://localhost:8000/api/wpn/sessions/your_user_id"
```

## API Endpoints

### Import Endpoints

- `POST /api/wpn/import-text` - Import hand history as JSON text
- `POST /api/wpn/import-file` - Import hand history from uploaded file

### Review Endpoints

- `POST /api/wpn/session-review` - Get AI review of a session
- `GET /api/wpn/sessions/{user_id}` - List all sessions for a user
- `GET /api/wpn/session/{user_id}/{session_id}` - Get hands from a specific session

## Supported Hand History Format

WPN hand histories typically look like this:

```
***** Hand History for Game 1234567890 *****
$0.02/$0.05 NL Texas Hold'em - Thursday, January 10, 2026, 14:50:00
Table ACR - 6 Max (Real Money)
Seat 1: Player1 ($5.23)
Seat 2: Player2 ($4.91)
Seat 3: Player3 ($3.45)
Seat 4: Hero ($6.75)
Player1 posts small blind [$0.02]
Player2 posts big blind [$0.05]
** Dealing down cards **
Dealt to Hero [Ah Kh]
Player3 folds
Hero raises [$0.15]
Player1 calls [$0.13]
Player2 folds
** Dealing Flop ** [5h 2c Qd]
Player1 checks
Hero bets [$0.25]
Player1 folds
Hero wins $0.40
*** Summary ***
Total pot $0.40
Hero collected $0.40
```

## What Gets Parsed

The parser extracts the following information from each hand:

- **Hand ID** - Unique identifier for the hand
- **Date/Time** - When the hand was played
- **Stakes** - Blind levels (e.g., "0.02/0.05")
- **Table Name** - Name of the table
- **Player Name** - Your screen name (hero)
- **Seat Number** - Your seat position
- **Hole Cards** - Your pocket cards
- **Board Cards** - Flop, turn, and river
- **Actions** - All betting actions in the hand
- **Won Amount** - Amount won (if applicable)
- **Pot Size** - Total pot size
- **Raw Text** - Complete original hand history

## Differences from CoinPoker Integration

Unlike CoinPoker, WPN does not provide:
- ❌ On-chain verification (no blockchain integration)
- ❌ Provably-fair RNG proofs
- ❌ Transaction hashes

However, the core coaching and analysis features work identically.

## Testing

The integration includes comprehensive test coverage:

```bash
pytest tests/test_wpn_parser.py -v
```

Tests cover:
- Basic hand parsing
- Multiple hand splitting
- Board card extraction
- Tournament format support
- Date/time parsing (multiple formats)
- Edge cases (preflop folds, empty files, etc.)

## Technical Details

### Parser Implementation

- **Location**: `backend/blockchain/wpn_parser.py`
- **Main Functions**:
  - `parse_hand(text: str) -> ParsedWpnHand` - Parse a single hand
  - `parse_many(text: str) -> list[ParsedWpnHand]` - Parse multiple hands
  - `split_hands(text: str) -> list[str]` - Split text into individual hands

### API Routes

- **Location**: `backend/api/routes/wpn.py`
- **Router**: FastAPI router with 5 endpoints
- **Database**: Uses SQLAlchemy with HandHistory model

### Data Models

- **Location**: `backend/api/models.py`
- **Models**:
  - `WpnImportTextRequest` / `WpnImportResponse`
  - `WpnSessionReviewRequest` / `WpnSessionReviewResponse`
  - `WpnSessionSummary` / `WpnSessionListResponse`
  - `WpnSessionHandsResponse`

## Troubleshooting

### Hand histories not parsing correctly?

1. Check that your hand history file starts with `***** Hand History for Game`
2. Ensure the file is in English (WPN supports multiple languages)
3. Verify the format matches the example above

### Missing information in parsed hands?

The parser is designed to be robust and handle variations in WPN export formats. If some fields are missing, that's okay - the parser extracts what it can find.

### Need help?

Open an issue on GitHub with:
- A sample hand history (with personal info redacted)
- The error message or unexpected behavior
- Your WPN site (ACR, BlackChip, etc.)

## Future Enhancements

Potential future features:
- Support for Omaha and other game variants
- Real-time hand import during play (with HUD integration)
- Enhanced tournament analysis
- Player profiling and tracking
- Integration with poker tracking software (PT4, HM3)

## Related Files

- Parser: `backend/blockchain/wpn_parser.py`
- Routes: `backend/api/routes/wpn.py`
- Models: `backend/api/models.py` (WPN models section)
- Tests: `tests/test_wpn_parser.py`
- Main API: `backend/api/main.py` (routes registered here)

## Credits

This integration enables Poker Therapist to work with the largest US-facing poker network, making Rex accessible to thousands of additional players.
