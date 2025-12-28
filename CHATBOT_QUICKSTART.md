# Streamlit Chatbot - Quick Start Guide

## Installation

1. **Install dependencies**:
   ```bash
   pip install streamlit openai
   ```

2. **Configure your xAI API key**:

   Create `.streamlit/secrets.toml`:
   ```toml
   XAI_API_KEY = "xai-your-api-key-here"
   ENABLE_STREAMING = true
   ENABLE_THINKING = true
   ```

   Or set environment variable:
   ```bash
   export XAI_API_KEY="xai-your-api-key-here"
   ```

3. **Run the application**:
   ```bash
   streamlit run chatbot_app.py
   ```

## Usage

1. Open the app in your browser (usually http://localhost:8501)
2. Enter your email in the sidebar to log in
3. Start chatting!

## Features

- 🧠 **Persistent Memory**: All conversations saved to SQLite database
- 👥 **Multi-User**: Each user has their own conversation history
- 🔄 **Streaming**: Real-time response streaming
- 💭 **AI Thinking**: View the AI's reasoning process
- 🔐 **Secure**: API keys in secrets or environment variables

## Configuration

### `.streamlit/secrets.toml` (Recommended)
```toml
XAI_API_KEY = "xai-your-key"
ENABLE_STREAMING = true
ENABLE_THINKING = true
```

### Environment Variables
```bash
export XAI_API_KEY="xai-your-key"
```

## Documentation

For detailed documentation, see [docs/STREAMLIT_CHATBOT.md](docs/STREAMLIT_CHATBOT.md)

## Testing

```bash
# Run tests
pytest tests/test_chatbot_app.py -v

# With coverage
pytest tests/test_chatbot_app.py --cov=chatbot_app
```

## Database

The chatbot uses SQLite (`chatbot_history.db`) to store:
- User accounts (email-based)
- Message history per user
- Timestamps for all messages

To clear history:
- Use the "🗑️ Clear Chat History" button in the app
- Or delete `chatbot_history.db` file

## Troubleshooting

### API Key Not Found
- Check `.streamlit/secrets.toml` exists with correct key
- Or verify `XAI_API_KEY` environment variable is set
- Restart the app after setting the key

### Database Locked
- Close other instances of the app
- Delete `chatbot_history.db` if corrupted

### No Streaming
- Check internet connection
- Verify API key is valid
- Set `ENABLE_STREAMING = false` in secrets.toml

## Get xAI API Key

1. Visit https://x.ai/api
2. Sign up or log in
3. Generate API key
4. Copy to configuration

## Support

For issues, see [docs/STREAMLIT_CHATBOT.md](docs/STREAMLIT_CHATBOT.md) or open an issue on GitHub.
