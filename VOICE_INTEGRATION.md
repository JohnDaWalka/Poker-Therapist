# Rex Voice Integration Guide 🎰🎤

## Overview

Rex is your elite poker coach with voice capabilities, powered by multiple AI models (OpenAI ChatGPT, Anthropic Claude, Google Gemini, x.ai Grok, or Perplexity AI) with OpenAI for TTS/STR features.

## Features

### 🎤 Voice Input (Speech-to-Text)
- Upload audio files (WAV, MP3, M4A, OGG)
- Real-time transcription
- Multi-language support

### 🔊 Voice Output (Text-to-Speech)
- Rex's authoritative voice (Onyx - deep, commanding)
- Auto-play responses
- Multiple voice options available
- Natural, conversational tone

### 🎰 Rex Personality
- Elite poker coach with decades of experience
- CFR (Counterfactual Regret Minimization) analysis
- Psychological wellness coaching
- Direct, no-nonsense communication
- Sharp wit with professional empathy

## Authorized Users

VIP users with full voice features enabled:
- m.fanelli1@icloud.com
- johndawalka@icloud.com
- mauro.fanelli@ctstate.edu
- maurofanellijr@gmail.com
- cooljack87@icloud.com
- jdwalka@pm.me

## Setup

### 1. Environment Variables

Create a `.env` file or set environment variables:

```bash
# Primary API - x.ai for Grok chat
XAI_API_KEY=xai-your-api-key-here

# Optional - OpenAI for voice features fallback
OPENAI_API_KEY=sk-your-openai-key-here

# Voice configuration
VOICE_ENABLED=true
VOICE_PROVIDER=xai
```

### 2. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using the project dependencies
pip install streamlit>=1.40.0 openai>=1.58.1 sounddevice>=0.4.6 pydub>=0.25.1 scipy>=1.11.0
```

### 3. Run the Application

```bash
streamlit run chatbot_app.py
```

## Usage

### Text Mode
1. Enter your email in the sidebar
2. Type your poker questions or scenarios
3. Receive Rex's expert analysis

### Voice Mode
1. Enable voice mode in the sidebar (🎙️ Voice Mode toggle)
2. Configure voice settings:
   - Select Rex's voice (Onyx recommended)
   - Enable/disable auto-play
   - Choose language for speech recognition
3. **Input**: Upload an audio file for transcription
4. **Output**: Rex responds with text and voice

### Quick Actions
Use preset poker coaching queries:
- 🎯 Strategy Tips
- 🧘 Tilt Help
- 📊 Hand Analysis
- 💪 Mental Game

## Voice Settings

### Available Voices
- **Onyx** (Default) - Deep, authoritative, perfect for Rex
- Alloy - Neutral, balanced
- Echo - Clear, professional
- Fable - Expressive, storytelling
- Nova - Bright, energetic
- Shimmer - Warm, friendly

### Language Support
- English (en) - Default
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- And more...

## API Configuration

### x.ai API (Primary)
- Used for Grok chat responses
- Attempts voice features first
- OpenAI-compatible endpoint: `https://api.x.ai/v1`

### OpenAI API (Fallback)
- Used for TTS (Text-to-Speech) if x.ai doesn't support it
- Used for STT (Speech-to-Text / Whisper)
- Automatic fallback if x.ai voice not available

## Technical Details

### Architecture
```
chatbot_app.py (Main Streamlit App)
├── python_src/services/voice_service.py (TTS/STR abstraction)
├── python_src/ui/voice_chatbot.py (Voice UI components)
└── python_src/ui/chat_components.py (Chat UI components)
```

### Voice Service
- **TTS Model**: `tts-1` (OpenAI)
- **STT Model**: `whisper-1` (OpenAI Whisper)
- **Default Voice**: Onyx (deep, authoritative)
- **Latency Target**: < 2 seconds

### Database
- SQLite for persistent conversations
- Per-user message history
- Multi-user support

## Troubleshooting

### Voice Features Not Working
1. Check API keys are set correctly
2. Ensure `OPENAI_API_KEY` is set (required for voice fallback)
3. Try disabling voice mode and using text-only
4. Check browser console for errors

### Audio Upload Issues
1. Supported formats: WAV, MP3, M4A, OGG
2. Maximum file size: 200MB (configurable in `.streamlit/config.toml`)
3. Ensure audio contains clear speech

### TTS Not Playing
1. Check browser audio permissions
2. Ensure auto-play is enabled (may be blocked by browser)
3. Click audio controls manually if needed

## Development

### Adding New Voice Features
1. Extend `VoiceService` in `python_src/services/voice_service.py`
2. Add UI components in `python_src/ui/voice_chatbot.py`
3. Update `chatbot_app.py` to integrate new features

### Testing Voice Services
```python
from python_src.services.voice_service import VoiceService

# Initialize service
voice = VoiceService()

# Test TTS
audio = voice.text_to_speech("Hello from Rex!")

# Test STT
with open("audio.wav", "rb") as f:
    text = voice.speech_to_text(f.read())
```

## Security

- API keys stored in environment variables or Streamlit secrets
- Email-based authentication for VIP features
- No voice data stored permanently
- Audio processed in memory only

## Support

For issues or questions:
- Check the main README.md
- Review `.env.example` for configuration
- Contact repository maintainers

## Future Enhancements

✅ **Recently Implemented:**
- [x] Real-time voice streaming (WebRTC) - Voice streaming service with async support
- [x] Voice-activated recording - Voice Activity Detection (VAD) with webrtcvad
- [x] Conversation mode (continuous voice chat) - Session management with multiple modes
- [x] Voice emotion analysis - Librosa-based emotion detection from voice
- [x] Multi-language Rex personalities - 8+ languages with authentic poker terminology
- [x] Voice cloning for custom Rex voice - Coqui TTS integration for custom voices

## New Features Documentation

### 🔴 Real-time Voice Streaming
Stream your voice in real-time with WebRTC support for instant responses:
- Async audio streaming with minimal latency
- Voice Activity Detection (VAD) to filter silence
- Continuous transcription as you speak
- No need to upload files - just speak naturally

### 🎤 Voice-Activated Recording
Automatic recording that starts when you speak:
- Smart voice detection with adjustable sensitivity
- Automatically starts recording when voice is detected
- Stops recording during silence
- No manual start/stop needed

### 💬 Conversation Mode
Choose how you want to interact with Rex:
- **Single Turn**: One question, one answer (traditional)
- **Continuous Chat**: Natural back-and-forth conversation flow
- **Voice Activated**: Hands-free mode with automatic turn-taking

### 😊 Emotion Analysis
Rex understands your emotional state:
- Detects emotions: happy, sad, frustrated, anxious, confident, excited
- Adjusts coaching style based on your mood
- Visual emotion indicators in the UI
- Energy and tone analysis from voice

### 🌍 Multi-Language Rex Personalities
Rex speaks your language authentically:
- English, Spanish, French, German, Italian, Portuguese
- Japanese, Chinese, Korean, and more
- Native poker terminology in each language
- Language-specific voice preferences
- Maintains Rex's authoritative coaching style

### 🎭 Voice Cloning
Create your perfect Rex voice:
- Upload 3-5 voice samples (10-15 seconds each)
- Train custom voice profiles
- Rex speaks with your chosen voice
- Multiple profiles supported
- Quality validation for uploaded samples

---

**Rex Poker Coach** - Your AI poker therapist with voice 🎰🎤
