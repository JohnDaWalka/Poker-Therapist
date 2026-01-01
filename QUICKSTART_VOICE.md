# Quick Start Guide - Rex Voice Integration 🎰🎤

Get up and running with Rex, your voice-enabled poker coach, in 5 minutes!

## Prerequisites

- Python 3.12 or higher
- Git
- API Keys:
  - xAI API key (required for Grok chat)
  - OpenAI API key (required for voice features)

## Quick Setup (Automated)

### Linux/Mac

```bash
# Clone the repository
git clone https://github.com/JohnDaWalka/Poker-Therapist.git
cd Poker-Therapist

# Run setup script
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Set API keys
export XAI_API_KEY='xai-your-key-here'
export OPENAI_API_KEY='sk-your-key-here'

# Start the app
streamlit run chatbot_app.py
```

### Windows

```cmd
# Clone the repository
git clone https://github.com/JohnDaWalka/Poker-Therapist.git
cd Poker-Therapist

# Run setup script
setup.bat

# Activate virtual environment
venv\Scripts\activate.bat

# Set API keys
set XAI_API_KEY=xai-your-key-here
set OPENAI_API_KEY=sk-your-key-here

# Start the app
streamlit run chatbot_app.py
```

## Manual Setup

If you prefer manual installation:

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate.bat  # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

**Option A: Environment Variables**
```bash
export XAI_API_KEY='xai-your-key-here'
export OPENAI_API_KEY='sk-your-key-here'
```

**Option B: .env file**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

**Option C: Streamlit Secrets**
```bash
mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
XAI_API_KEY = "xai-your-key-here"
OPENAI_API_KEY = "sk-your-key-here"
EOF
```

### 4. Run the Application

```bash
streamlit run chatbot_app.py
```

## Getting API Keys

### xAI API Key (Required)
1. Visit https://x.ai
2. Sign up or log in
3. Navigate to API settings
4. Generate API key
5. Copy key starting with `xai-`

### OpenAI API Key (Required for Voice)
1. Visit https://platform.openai.com
2. Sign up or log in
3. Go to API Keys section
4. Create new secret key
5. Copy key starting with `sk-`

## First Time Usage

### 1. Open the Application
- Browser will open automatically at `http://localhost:8501`
- You should see the Rex welcome screen

### 2. Login
- Select an authorized email from the dropdown, OR
- Enter your custom email
- Authorized users get VIP voice features

### 3. Enable Voice Mode
- In the sidebar, toggle "🎙️ Enable Voice"
- Configure voice settings:
  - **Rex Voice**: Onyx (recommended for authoritative tone)
  - **Auto-play responses**: Enabled
  - **Speech Language**: English (en)

### 4. Start Chatting
- **Text Input**: Type your poker question in the chat box
- **Voice Input**: Click "🎤 Voice Input" and upload an audio file
- Rex will respond with text and voice!

## Testing Voice Features

### Test Text-to-Speech (TTS)
```
Type: "Tell me about pocket aces"
Expected: Rex responds with text AND plays voice
```

### Test Speech-to-Text (STT)
```
1. Record yourself asking: "What's the best starting hand?"
2. Save as .mp3, .wav, .m4a, or .ogg
3. Upload via Voice Input expander
4. Rex transcribes and responds
```

## Troubleshooting

### "No module named 'openai'"
```bash
pip install -r requirements.txt
```

### "API key not found"
- Check your API keys are set correctly
- Verify no extra spaces in keys
- Try restarting the application

### Voice not working
- Ensure OPENAI_API_KEY is set (required for voice)
- Check browser audio permissions
- Try manually playing audio (click play button)

### Audio upload issues
- Supported formats: WAV, MP3, M4A, OGG
- Max file size: 200MB
- Ensure audio contains clear speech

## Advanced Configuration

### Custom Authorized Emails
```bash
export AUTHORIZED_EMAILS="email1@example.com,email2@example.com"
```

### Voice Provider Settings
Edit `.streamlit/config.toml`:
```toml
[voice]
enable_tts = true
enable_stt = true
voice_provider = "xai"
default_voice = "onyx"
```

### Database Location
Default: `RexVoice.db` in project root
To change, edit `chatbot_app.py`:
```python
DB_PATH = Path("/custom/path/RexVoice.db")
```

## Quick Actions

Once logged in, use quick action buttons for common queries:

- **🎯 Strategy Tips**: Get advanced poker strategy advice
- **🧘 Tilt Help**: Mental wellness and tilt management
- **📊 Hand Analysis**: Analyze specific poker hands
- **💪 Mental Game**: Improve focus and mental game

## Example Conversations

### Strategy Query
```
You: "How should I play AK from UTG?"
Rex: "AK under the gun is premium but tricky. 
      Raise 3BB to build pot while limiting field..."
      [Voice plays automatically]
```

### Hand Analysis
```
You: [Upload audio] "I had pocket tens, flop came Q-7-2..."
Rex: [Transcribes, then responds]
     "With pocket tens on a Q-high board, you're behind 
     overpairs but ahead of draws. Position matters here..."
```

## Next Steps

1. **Read Full Documentation**
   - `VOICE_INTEGRATION.md` - Complete voice setup guide
   - `README.md` - Project overview
   - `IMPLEMENTATION_COMPLETE.md` - Technical details

2. **Explore Features**
   - Try different Rex voices
   - Use quick action buttons
   - Upload audio files
   - Enable/disable thinking display

3. **Customize**
   - Add your email to authorized list
   - Adjust voice settings
   - Configure auto-play preferences

## Support

- **Issues**: https://github.com/JohnDaWalka/Poker-Therapist/issues
- **Documentation**: See `/docs` directory
- **Tests**: Run `pytest tests/test_voice_integration.py`

## Authorized VIP Users

Full voice features enabled for:
- m.fanelli1@icloud.com
- johndawalka@icloud.com
- mauro.fanelli@ctstate.edu
- maurofanellijr@gmail.com
- cooljack87@icloud.com
- jdwalka@pm.me

To add yourself, set `AUTHORIZED_EMAILS` environment variable.

---

**Welcome to Rex! 🎰 Your elite poker coach awaits.**

Need help? Check `VOICE_INTEGRATION.md` for detailed documentation.
