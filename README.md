# Poker Therapist

A comprehensive poker training, analysis, and coaching platform. This unified repository combines multiple poker-focused projects into a single integrated suite.

## 🎯 Overview

Poker Therapist brings together poker engine logic, training tools, AI coaching, statistical analysis, and post-quantum cryptographic security into one platform. It includes:

- **Poker Engine** — Hand evaluation for Texas Hold'em, Omaha, 7-Card Stud, and Razz
- **Training Suite** — Interactive training with GTO strategies, equity calculators, and scenario practice
- **Nash Equilibrium Trainer** — CFR-based AI self-play to learn unexploitable strategies
- **Player Analysis** — HUD overlay, opponent classification (LAG/TAG/LP/TP), and statistics tracking
- **Excel Tracker** — Session and bankroll tracking via Excel exports
- **Gemini Poker Coach** — TypeScript frontend powered by Google Gemini AI
- **Cross-Platform Support** — Windows, macOS, and Linux
- **Post-Quantum Security** — ML-KEM-1024 + ML-DSA-87 cryptographic protection
- **Vercel Deployment** — Serverless FastAPI backend

## 📁 Project Structure

```
├── api/                    # FastAPI serverless handler (Vercel)
├── docs/                   # Documentation
│   ├── COMPATIBILITY.md    # Platform compatibility guide
│   ├── FEATURES.md         # Detailed feature list
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── NASH_TRAINER.md     # Nash equilibrium trainer docs
│   ├── USAGE_GUIDE.md      # User guide
│   ├── WINDOWS_IMPLEMENTATION.md
│   └── WINDOWS_SETUP.md
├── examples/               # Example scripts
├── frontend/               # Gemini Poker Coach (TypeScript/Vite)
│   ├── index.tsx           # Main React app
│   ├── lib/pqc.ts          # PQC TypeScript implementation
│   ├── package.json
│   └── vite.config.ts
├── scripts/                # Setup scripts (Windows batch/PowerShell)
├── security/               # PQC public keys
├── src/                    # Platform utilities
├── static/                 # CSS/JS assets for web UI
├── templates/              # HTML templates for Flask web UI
├── tests/                  # Test suite
│   ├── test_nash_train.py
│   ├── test_new_features.py
│   └── test_poker_engine.py
├── advanced_tools.py       # GTO trainer, range visualizer, hand history parser
├── equity_sim.py           # Monte Carlo equity simulator
├── excel_tracker.py        # Excel session/bankroll tracker
├── hud.py                  # HUD overlay display
├── nash_train.py           # Nash equilibrium CFR trainer
├── player_classifier.py    # Opponent style classifier
├── player_stats_cache.py   # SQLite stats cache
├── poker_engine.py         # Core poker hand evaluator
├── poker_server.py         # Flask web server (main UI)
├── pqc.py                  # Post-quantum cryptography core
├── pqc_api.py              # PQC API utilities
├── pqc_files.py            # PQC file encryption
├── statistics_tracker.py   # Statistics and progress tracking
├── training_scenarios.py   # Scenario-based training
├── web_ui.py               # Simplified equity calculator UI
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel deployment config
└── start.sh                # Quick start script
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for the Gemini frontend)

### Installation

```bash
# Clone the repository
git clone https://github.com/JohnDaWalka/Poker-Therapist.git
cd Poker-Therapist

# Install Python dependencies
pip install -r requirements.txt
```

### Running the Main Training Server

```bash
python poker_server.py
# Open http://localhost:5000
```

### Running the Equity Calculator UI

```bash
python web_ui.py
# Open http://localhost:5001
```

### Running the Nash Equilibrium Trainer

```bash
python nash_train.py
```

### Running the Gemini Poker Coach Frontend

```bash
cd frontend
npm install
npm run dev
```

### Quick Start Script

```bash
chmod +x start.sh
./start.sh
```

## 🃏 Features

### Hand Evaluation
- Texas Hold'em (2 hole cards)
- Omaha (4 hole cards, must use exactly 2)
- 7-Card Stud
- Razz (lowball)

### Training Tools
- **Hand Range Visualizer** — Interactive 13×13 matrix
- **Equity Calculator** — Monte Carlo simulation (10,000 trials)
- **GTO Trainer** — Game Theory Optimal preflop strategies
- **Hand History Parser** — PokerStars and GGPoker format support
- **Training Scenarios** — Squeeze play, 3-bet pots, continuation bets, and more

### AI & Analysis
- **Nash Equilibrium** — CFR algorithm for unexploitable strategies
- **Opponent Classification** — LAG, TAG, Loose Passive, Tight Passive
- **HUD Overlay** — VPIP, PFR, 3-Bet stats in a draggable widget
- **Statistics Tracking** — Per-session and aggregate performance

### Security
- **ML-KEM-1024** (FIPS 203) — Key encapsulation
- **ML-DSA-87** (FIPS 204) — Digital signatures
- **AES-256-GCM** — Symmetric encryption

See [PQC_SECURITY.md](PQC_SECURITY.md) for details.

## 🖥️ Platform Support

- ✅ Windows 10/11 and Windows Server 2016+
- ✅ Linux (Ubuntu, Debian, RHEL, and others)
- ✅ macOS 10.15+

See [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) for Windows-specific instructions.

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/deck` | Get all cards in a standard deck |
| GET | `/api/random-cards?count=X` | Get X random cards |
| POST | `/api/evaluate` | Evaluate a poker hand |
| POST | `/api/compare-boards` | Compare multiple boards |
| POST | `/api/equity/multi-way` | Multi-way equity calculation |
| POST | `/api/evaluate/stud` | 7-Card Stud evaluation |
| POST | `/api/evaluate/razz` | Razz evaluation |
| POST | `/api/scenarios/generate` | Generate training scenario |
| GET | `/api/stats/user/{id}` | User progress report |
| POST | `/api/multiplayer/create` | Create multiplayer session |

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test suites
python -m pytest tests/test_poker_engine.py
python -m pytest tests/test_nash_train.py
python -m pytest tests/test_new_features.py
```

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is open source and available under the MIT License. See [LICENSE](LICENSE) for details.

## 🔗 Merged Repositories

This project consolidates the following repositories:

| Repository | Description |
|------------|-------------|
| [Poker-Therapist](https://github.com/JohnDaWalka/Poker-Therapist) | Core platform — API, player analysis, PQC security |
| [Poker-Suite](https://github.com/JohnDaWalka/Poker-Suite) | Poker engine, training tools, web UI, Nash trainer |
| [Shark](https://github.com/JohnDaWalka/Shark) | Cross-platform support, Windows compatibility |
| [Gemi](https://github.com/JohnDaWalka/Gemi) | Gemini Poker Coach TypeScript frontend |
| [Poker-Guru](https://github.com/JohnDaWalka/Poker-Guru) | GTO solver and poker guru |
