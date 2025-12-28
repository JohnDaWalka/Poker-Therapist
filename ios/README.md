# Therapy Rex iOS App

SwiftUI-based iOS application for Therapy Rex poker mental game coaching.

## Requirements

- Xcode 15+
- iOS 16.0+
- Swift 5.9+
- CocoaPods

## Setup

1. Install dependencies:
```bash
cd ios
pod install
```

2. Open the workspace:
```bash
open TherapyRex.xcworkspace
```

3. Configure backend URL in `Services/APIClient.swift`

4. Build and run on simulator or device

## Features

- **Quick Triage**: Emergency tilt intervention
- **Deep Sessions**: 45-90 minute structured therapy
- **Voice Recording**: Record and analyze emotional rants
- **Profile Tracking**: Persistent tilt profile with CoreData
- **Guided Breathing**: Animated breathing exercises
- **Offline Support**: Gemini Nano on-device inference

## Architecture

```
TherapyRex/
├── App/                    # App entry point
├── Views/                  # SwiftUI views
├── ViewModels/             # MVVM view models
├── Models/                 # Data models & CoreData
├── Services/               # API client, recording, etc.
└── Resources/              # Assets, colors, etc.
```

## CoreData Schema

- `Session`: Therapy session records
- `TiltProfile`: User tilt characteristics
- `ActionItem`: Action plan items

## API Integration

The app communicates with the backend API at:
- Development: `http://localhost:8000`
- Production: Configure in build settings

## Testing

Run tests with:
```bash
xcodebuild test -workspace TherapyRex.xcworkspace -scheme TherapyRex -destination 'platform=iOS Simulator,name=iPhone 15'
```

## Deployment

1. Update version in Info.plist
2. Archive build
3. Submit to App Store Connect
