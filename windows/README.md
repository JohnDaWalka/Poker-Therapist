# Therapy Rex Windows App

Electron + Vue.js desktop application for Windows.

## Requirements

- Node.js 18+
- npm or yarn

## Setup

1. Install dependencies:
```bash
cd windows
npm install
```

2. Configure backend URL in `src/services/api.js`

3. Run in development mode:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

### Local path mapping (Windows)
- Project root (local): `C:\Users\mfane\Poker-Coach---`
- Optional chroma integration clone: `C:\Users\mfane\chroma-poker`

With hash-based routing enabled in the Windows build, ensure the packaged Electron app loads from the generated `dist` output and that any assets or shared modules referenced from the paths above are available.

## Features

- **Triage View**: Quick tilt intervention
- **Deep Session**: Structured therapy
- **Hand Analysis**: Import from PokerTracker 4 / Hold'em Manager 3
- **Screen Capture**: HUD screenshot analysis
- **Overlay Mode**: Always-on-top mini window
- **System Tray**: Background mode with quick access

## Project Structure

```
windows/
├── electron/           # Electron main process
├── src/
│   ├── views/         # Vue views
│   ├── components/    # Vue components
│   ├── services/      # API client, tracker integration
│   ├── store/         # Vuex store
│   └── router/        # Vue Router
└── public/            # Static assets
```

## Build & Deploy

```bash
# Development
npm run dev

# Production build
npm run build

# Package for Windows
npm run package
```

## Tracker Integration

Supports auto-import from:
- PokerTracker 4
- Hold'em Manager 3

Configure in Settings > Tracker Integration.
