# Chroma Poker

A Vue.js poker hand analysis frontend with Vuex state management and a Python tooling layer. Originally from [JohnDaWalka/Chroma_Poker](https://github.com/JohnDaWalka/Chroma_Poker).

## Overview

Chroma Poker provides a visual poker hand analysis interface built with Vue 2 + Vuex. It fetches hand strength, rank, winning probability, suggested actions, opponent analysis, and historical data from a configurable REST API.

## Structure

```
chroma-poker/
├── src/
│   ├── App.vue                        # Root Vue component
│   ├── api/
│   │   └── pokerHandAnalysis.js       # Axios API layer
│   ├── components/
│   │   └── PokerHandAnalysis.vue      # Main analysis component
│   └── store/
│       └── index.js                   # Vuex store
├── tests/
│   ├── test_advent_of_code.py         # Python CLI tests
│   └── unit/
│       ├── PokerHandAnalysis.spec.js  # Component tests (Jest/Vue Test Utils)
│       ├── api/
│       │   └── pokerHandAnalysis.spec.js  # API layer tests
│       └── store/
│           └── pokerHandAnalysis.spec.js  # Vuex store tests
└── pyproject.toml                     # Python project config (ruff, mypy, pytest)
```

## Features

- **Hand Analysis Dashboard** — filterable table of hands with strength, rank, and win probability
- **Chart Integration** — plug-in chart component for visual data representation
- **Sortable Table** — click column headers to sort ascending/descending
- **Vuex State Management** — centralised store for all poker hand data
- **Axios API Layer** — typed async functions for each data endpoint

## API Endpoints (configured in `src/api/pokerHandAnalysis.js`)

| Function | Endpoint |
|---|---|
| `getHandDetails` | `GET /hand-details` |
| `getHandStrength` | `GET /hand-strength` |
| `getHandRank` | `GET /hand-rank` |
| `getWinningProbability` | `GET /winning-probability` |
| `getSuggestedActions` | `GET /suggested-actions` |
| `getOpponentAnalysis` | `GET /opponent-analysis` |
| `getHistoricalData` | `GET /historical-data` |
| `getVisualElements` | `GET /visual-elements` |

## Running the Frontend

```bash
cd chroma-poker
npm install
npm run serve
```

## Running Python Tests

```bash
cd chroma-poker
pip install -e ".[dev]"
pytest
```
