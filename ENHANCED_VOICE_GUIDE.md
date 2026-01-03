# Enhanced Voice Features - User Guide

This guide covers the newly implemented voice streaming features for Rex Poker Coach.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Feature Guide](#feature-guide)
  - [Real-time Voice Streaming](#real-time-voice-streaming)
  - [Voice-Activated Recording](#voice-activated-recording)
  - [Conversation Mode](#conversation-mode)
  - [Emotion Analysis](#emotion-analysis)
  - [Multi-Language Personalities](#multi-language-personalities)
  - [Voice Cloning](#voice-cloning)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Overview

Rex now includes six major voice enhancement features:

1. **Real-time Voice Streaming** - Stream your voice continuously with WebRTC
2. **Voice-Activated Recording** - Automatic recording triggered by your voice
3. **Conversation Mode** - Natural back-and-forth dialogue with Rex
4. **Emotion Analysis** - Rex detects and responds to your emotional state
5. **Multi-Language Support** - Rex speaks 8+ languages authentically
6. **Voice Cloning** - Create custom Rex voice profiles

## Installation

### Basic Installation

```bash
# Install core dependencies
pip install -r requirements.txt
```

### Optional Dependencies

For full functionality, install these optional packages:

```bash
# For real-time streaming
pip install streamlit-webrtc aiortc av

# For voice activity detection
pip install webrtcvad

# For emotion analysis
pip install librosa transformers torch

# For voice cloning
pip install coqui-tts
```

### Minimal Installation (Basic Features Only)

```bash
pip install streamlit openai numpy
```

## Feature Guide

### Real-time Voice Streaming

Stream your voice in real-time with minimal latency.

**How to Use:**
1. Enable voice mode in the sidebar
2. Click "🔴 Start" in the Live Streaming section
3. Speak naturally - Rex transcribes as you talk
4. Click "⏹️ Stop" when finished

**Benefits:**
- No need to record and upload files
- Instant transcription
- Hands-free interaction
- Lower latency

**Technical Details:**
- Uses WebRTC for peer-to-peer audio streaming
- Voice Activity Detection (VAD) filters silence
- Async processing for minimal delay

### Voice-Activated Recording

Automatic recording that starts when you speak and stops when you're done.

**How to Use:**
1. Enable voice mode
2. Select "Voice Activated" in Conversation Mode
3. Adjust sensitivity slider (0-3)
4. Just start speaking - recording begins automatically

**Benefits:**
- No manual start/stop needed
- Natural flow in conversation
- Reduces recorded silence

**Configuration:**
```bash
# In .env
ENABLE_VAD=true
VAD_SENSITIVITY=2  # 0=least sensitive, 3=most sensitive
```

### Conversation Mode

Choose how you want Rex to respond to your input.

**Modes:**

1. **Single Turn** (Default)
   - Traditional one question, one answer
   - Best for specific queries

2. **Continuous Chat**
   - Natural back-and-forth conversation
   - Auto-continue option for coaching sessions
   - Configurable turn timeout

3. **Voice Activated**
   - Completely hands-free
   - Automatic turn-taking
   - Ideal for poker coaching sessions

**How to Use:**
1. Select mode in the sidebar under "💬 Conversation Mode"
2. Configure mode-specific settings
3. Start chatting!

**Example Use Cases:**
- **Single Turn**: "What should I do with pocket aces in this situation?"
- **Continuous**: Full coaching session discussing multiple hands
- **Voice Activated**: Hands-free practice while playing

### Emotion Analysis

Rex detects your emotional state from voice and adapts his coaching style.

**Detected Emotions:**
- 😊 Happy / Confident
- 😢 Sad / Disappointed  
- 😠 Angry
- 😤 Frustrated
- 🤩 Excited
- 😎 Confident
- 😰 Anxious
- 😐 Neutral

**How It Works:**
1. Upload or stream audio
2. Rex analyzes voice characteristics:
   - Energy levels
   - Pitch variations
   - Speaking rate
3. Emotion displayed with confidence score
4. Rex adjusts coaching tone accordingly

**Example:**
- **Detected**: Frustrated (85% confidence)
- **Rex's Response**: More supportive and encouraging, focusing on mental game

**Configuration:**
```bash
# In .env
ENABLE_EMOTION_ANALYSIS=true
```

### Multi-Language Personalities

Rex speaks your language with authentic poker terminology.

**Supported Languages:**
- 🇬🇧 English (en)
- 🇪🇸 Spanish (es) - Español
- 🇫🇷 French (fr) - Français
- 🇩🇪 German (de) - Deutsch
- 🇮🇹 Italian (it) - Italiano
- 🇵🇹 Portuguese (pt) - Português
- 🇯🇵 Japanese (ja) - 日本語
- 🇨🇳 Chinese (zh) - 中文

**How to Use:**
1. Select language in "🌍 Rex Language" dropdown
2. Rex responds in chosen language
3. Voice model automatically adjusts

**Features:**
- Language-specific poker terminology
- Culturally appropriate coaching style
- Maintains Rex's authoritative personality across languages
- Optimized voice selection per language

**Example:**
```python
# English
"You're playing too tight pre-flop. Open up your range."

# Spanish
"Estás jugando demasiado cerrado pre-flop. Amplía tu rango."
```

### Voice Cloning

Create a custom Rex voice that sounds exactly how you want.

**Requirements:**
- 3-5 audio samples
- 10-15 seconds each
- Clear, noise-free recordings
- Consistent speaking style

**How to Create a Voice Profile:**

1. **Record Voice Samples**
   - Use clear audio environment
   - Speak naturally and clearly
   - Record poker-related content for best results

2. **Upload Samples**
   - Go to "🎙️ Custom Rex Voice" in sidebar
   - Upload 3-5 WAV/MP3 files
   - Wait for validation

3. **Create Profile**
   - System validates audio quality
   - Profile created automatically
   - Appears in "🎭 Voice Profiles" dropdown

4. **Use Custom Voice**
   - Select profile from dropdown
   - Rex now speaks with custom voice
   - Switch back to default anytime

**Quality Tips:**
- Record in quiet environment
- Use good quality microphone
- Speak at normal pace
- Include varied intonation
- Keep background noise minimal

**Example Workflow:**
```bash
# 1. Record samples
sample1.wav - "Let's analyze this poker hand."
sample2.wav - "Your position here is crucial."
sample3.wav - "Think about the pot odds."

# 2. Upload via UI
# 3. System creates profile
# 4. Select profile
# 5. Rex speaks with custom voice
```

## Configuration

### Environment Variables

Add to `.env` file:

```bash
# Core API Keys
XAI_API_KEY=xai-your-key
OPENAI_API_KEY=sk-your-key

# Voice Features
VOICE_ENABLED=true
ENABLE_VOICE_STREAMING=true
ENABLE_VAD=true
ENABLE_EMOTION_ANALYSIS=true
ENABLE_VOICE_CLONING=true

# Defaults
DEFAULT_REX_LANGUAGE=en
DEFAULT_CONVERSATION_MODE=single_turn
VAD_SENSITIVITY=2

# Authorized Users
AUTHORIZED_EMAILS=user1@example.com,user2@example.com
```

### Streamlit Secrets

Alternative to `.env` - create `.streamlit/secrets.toml`:

```toml
XAI_API_KEY = "xai-your-key"
OPENAI_API_KEY = "sk-your-key"
ENABLE_STREAMING = true
ENABLE_THINKING = true
```

## Troubleshooting

### Voice Streaming Not Working

**Issue**: Streaming button disabled or not responding

**Solutions**:
1. Check WebRTC dependencies installed:
   ```bash
   pip install streamlit-webrtc aiortc av
   ```
2. Verify browser supports WebRTC (Chrome, Firefox, Edge)
3. Check microphone permissions in browser
4. Try reloading the page

### Voice Activity Detection Issues

**Issue**: Recording doesn't stop automatically

**Solutions**:
1. Adjust VAD sensitivity slider (try different values)
2. Speak more clearly and at consistent volume
3. Reduce background noise
4. Check `ENABLE_VAD=true` in config

### Emotion Analysis Not Showing

**Issue**: Emotions not detected from voice

**Solutions**:
1. Install librosa: `pip install librosa`
2. Ensure audio is clear with minimal noise
3. Verify `ENABLE_EMOTION_ANALYSIS=true`
4. Try uploading file instead of streaming

### Language Not Changing

**Issue**: Rex still responds in English

**Solutions**:
1. Verify language selection in sidebar
2. Check that language code is valid (en, es, fr, etc.)
3. Reload page after changing language
4. Clear browser cache

### Voice Cloning Fails

**Issue**: Profile creation fails or voice sounds wrong

**Solutions**:
1. Check Coqui TTS installed: `pip install coqui-tts`
2. Verify audio samples:
   - At least 3 samples required
   - Each 10-15 seconds long
   - Clear speech, minimal background noise
3. Try different audio format (WAV recommended)
4. Record in quieter environment

### Performance Issues

**Issue**: Slow responses or high latency

**Solutions**:
1. Disable emotion analysis if not needed
2. Use single turn mode instead of continuous
3. Reduce audio sample quality/bitrate
4. Close other browser tabs
5. Check internet connection speed

### API Key Errors

**Issue**: "API key not found" or authentication errors

**Solutions**:
1. Verify keys in `.env` or `secrets.toml`
2. Check key format (XAI starts with `xai-`, OpenAI with `sk-`)
3. Ensure no extra spaces in key
4. Verify key has not expired
5. Check API usage limits not exceeded

## Advanced Usage

### Combining Features

You can use multiple features together:

**Example: Full-Featured Session**
1. Enable voice mode
2. Select Spanish language
3. Choose "Continuous Chat" mode
4. Use custom voice profile
5. Emotion analysis active
6. Stream audio in real-time

**Result**: Natural Spanish conversation with Rex using your custom voice, automatically detecting emotions and responding appropriately.

### Automation Scripts

Create automated coaching sessions:

```python
from python_src.services.voice_streaming_service import ConversationSession, ConversationMode
from python_src.services.rex_personality import RexPersonality, Language

# Create session
session = ConversationSession(mode=ConversationMode.CONTINUOUS)
await session.start_session()

# Set Spanish Rex
rex = RexPersonality(Language.SPANISH)
system_prompt = rex.get_system_prompt()

# Use in your workflow
session.add_message("user", "Necesito ayuda con mi juego")
# Process with xAI API...
```

## Best Practices

1. **For Live Coaching**: Use Continuous mode + Voice Activated
2. **For Quick Questions**: Use Single Turn mode
3. **For Privacy**: Use voice cloning with local Coqui TTS
4. **For Performance**: Disable emotion analysis if not needed
5. **For Learning**: Try different languages to expand poker vocabulary

## Support

- Documentation: [VOICE_INTEGRATION.md](VOICE_INTEGRATION.md)
- Issues: GitHub Issues
- Email: Contact repository maintainers

---

**Rex Poker Coach** - Enhanced with advanced voice features 🎰🎤
