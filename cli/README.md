# Therapy Rex CLI

Command-line interface for Therapy Rex poker mental game coaching.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Quick Triage
Get immediate help for tilt situations:
```bash
python therapy_rex_cli.py triage
```

### Deep Therapy Session
45-90 minute structured therapy session:
```bash
python therapy_rex_cli.py deep
```

### Analysis Commands
```bash
# Analyze voice recording
python therapy_rex_cli.py analyze --voice rant.mp3

# Analyze HUD screenshot
python therapy_rex_cli.py analyze --image hud.png

# Analyze hand history
python therapy_rex_cli.py analyze --hand "PokerStars Hand #12345..."
```

### Profile & Stats
```bash
# View tilt profile
python therapy_rex_cli.py profile

# View mental game stats
python therapy_rex_cli.py stats

# View playbook
python therapy_rex_cli.py playbook
```

## Configuration

Set your backend API URL:
```bash
export THERAPY_REX_API_URL=http://localhost:8000
```

## Features

- 🎨 Beautiful terminal UI with Rich library
- 🧘 Guided breathing exercises
- 📊 Severity color coding (green/orange/red/purple)
- ⚡ Real-time API integration
- 🔒 Secure local storage
