# Streamlit Chatbot Application

## Overview

This is a Streamlit-based chatbot application with the following features:

- **Persistent Memory**: Uses SQLite database to store conversation history
- **Multi-User Support**: Identifies users by email address
- **xAI Integration**: Powered by xAI's Grok model with streaming support
- **Thinking Display**: Shows AI's reasoning process in expandable sections
- **Secure Configuration**: API keys stored in Streamlit secrets or environment variables

## Features

### 🧠 Persistent Memory
- All conversations are stored in a local SQLite database (`chatbot_history.db`)
- Each user's conversation history is preserved across sessions
- Users can resume conversations from where they left off

### 👥 Multi-User Support
- Users identify themselves via email address
- Each user has isolated conversation history
- Simple user authentication without complex password systems

### 🔄 Streaming Responses
- Real-time streaming of AI responses
- See the AI's answer as it's being generated
- Configurable via `ENABLE_STREAMING` in secrets.toml

### 💭 Thinking Display
- AI's reasoning process is captured from `<thinking>` tags
- Displayed in an expandable section for transparency
- Configurable via `ENABLE_THINKING` in secrets.toml

### 🔐 Secure Configuration
- API keys stored in `.streamlit/secrets.toml` or environment variables
- Keys never exposed in code or version control
- Fallback from secrets to environment variables

## Installation

### Prerequisites
- Python 3.12 or higher
- pip or uv package manager

### Setup Steps

1. **Install dependencies**:
   ```bash
   # Using pip
   pip install streamlit openai

   # Using uv (recommended)
   uv pip install streamlit openai
   ```

2. **Configure API key**:

   Option A: Using Streamlit Secrets (Recommended)
   ```bash
   # Copy the example secrets file
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml

   # Edit .streamlit/secrets.toml and add your xAI API key
   # XAI_API_KEY = "xai-your-actual-api-key-here"
   ```

   Option B: Using Environment Variables
   ```bash
   # Set environment variable
   export XAI_API_KEY="xai-your-actual-api-key-here"

   # Or add to .env file and source it
   echo 'XAI_API_KEY=xai-your-actual-api-key-here' >> .env
   source .env
   ```

3. **Get your xAI API key**:
   - Visit https://x.ai/api
   - Sign up or log in
   - Generate a new API key
   - Copy the key to your configuration

## Usage

### Running the Application

```bash
# From the repository root
streamlit run chatbot_app.py

# Or with explicit port
streamlit run chatbot_app.py --server.port 8501
```

The application will open in your default web browser at `http://localhost:8501`.

### Using the Chatbot

1. **Enter Your Email**:
   - In the sidebar, enter your email address
   - This identifies you and loads your conversation history
   - Click outside the text box or press Enter to log in

2. **Start Chatting**:
   - Type your message in the chat input at the bottom
   - Press Enter to send
   - Watch the response stream in real-time

3. **View AI Thinking** (Optional):
   - If enabled, you'll see "💭 AI Thinking Process" expanders
   - Click to expand and see the AI's reasoning

4. **Clear History**:
   - Click "🗑️ Clear Chat History" in the sidebar
   - This removes all your messages from the database
   - Cannot be undone!

## Configuration

### Streamlit Secrets (.streamlit/secrets.toml)

```toml
# xAI API Key (Required)
XAI_API_KEY = "xai-your-api-key-here"

# Enable streaming responses (Optional, default: true)
ENABLE_STREAMING = true

# Enable thinking display (Optional, default: true)
ENABLE_THINKING = true
```

### Environment Variables

Alternatively, set these environment variables:

- `XAI_API_KEY`: Your xAI API key (required)

### Model Configuration

The application uses the `grok-beta` model from xAI. This model:
- Supports conversational interactions
- Can explain its reasoning using `<thinking>` tags
- Provides streaming responses
- Has a large context window

## Database Schema

The SQLite database (`chatbot_history.db`) has two tables:

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

## Architecture

### Components

1. **Database Layer** (`init_database`, `get_or_create_user`, `save_message`, `load_messages`):
   - Manages SQLite database operations
   - Handles user creation and retrieval
   - Stores and loads conversation history

2. **API Client** (`get_xai_client`):
   - Creates OpenAI-compatible client for xAI
   - Retrieves API key from secrets or environment
   - Configures base URL for xAI API

3. **Streaming Handler** (`ThinksCallback`):
   - Processes streaming response chunks
   - Extracts thinking content from `<thinking>` tags
   - Updates UI in real-time

4. **Main Application** (`main`):
   - Streamlit UI and interaction logic
   - User authentication and session management
   - Message display and handling

### Data Flow

```
User Input
    ↓
Save to Database (user message)
    ↓
Send to xAI API (with conversation history)
    ↓
Stream Response (via ThinksCallback)
    ↓
Display in UI (with thinking if enabled)
    ↓
Save to Database (assistant message)
```

## Security Considerations

1. **API Key Storage**:
   - Never commit `.streamlit/secrets.toml` to version control
   - Use `.gitignore` to exclude sensitive files
   - Prefer Streamlit secrets over environment variables in production

2. **Database Security**:
   - SQLite database is local only
   - No network exposure by default
   - Consider encryption for sensitive data

3. **User Privacy**:
   - Email addresses stored in plaintext
   - Consider hashing if handling sensitive information
   - Provide clear data deletion mechanism

4. **Input Validation**:
   - Email format validation recommended
   - SQL injection prevented by parameterized queries
   - Rate limiting may be needed for production

## Troubleshooting

### "xAI API key not found" Error
- Ensure you've configured `XAI_API_KEY` in `.streamlit/secrets.toml` or as environment variable
- Check for typos in the key name
- Restart the Streamlit app after adding the key

### Database Locked Error
- Only one Streamlit instance should access the database
- Close any other running instances
- Delete `chatbot_history.db` and restart (will lose history)

### Streaming Not Working
- Check your internet connection
- Verify API key is valid
- Set `ENABLE_STREAMING = false` in secrets.toml to use non-streaming mode

### Thinking Tags Not Displayed
- Verify `ENABLE_THINKING = true` in secrets.toml
- The model may not always use thinking tags
- Check if `<thinking>` tags are in the raw response

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/test_chatbot_app.py -v

# With coverage
pytest tests/test_chatbot_app.py --cov=chatbot_app --cov-report=html
```

### Code Quality
```bash
# Format code
ruff format chatbot_app.py

# Lint code
ruff check chatbot_app.py

# Type check
mypy chatbot_app.py
```

## Deployment

### Local Deployment
```bash
streamlit run chatbot_app.py
```

### Streamlit Cloud
1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Deploy from your repository
4. Add secrets in Streamlit Cloud dashboard

### Docker Deployment
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY chatbot_app.py .
COPY .streamlit .streamlit

EXPOSE 8501
CMD ["streamlit", "run", "chatbot_app.py"]
```

## Future Enhancements

- [ ] Export conversation history to file
- [ ] Support for multiple AI models
- [ ] User profile management
- [ ] Message search and filtering
- [ ] Conversation branching
- [ ] Voice input/output
- [ ] File upload support
- [ ] Multi-language support
- [ ] Admin dashboard for user management
- [ ] Rate limiting and quota management

## License

See LICENSE file in the repository root.

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review xAI API documentation: https://docs.x.ai/

## Credits

Built with:
- [Streamlit](https://streamlit.io/) - Web application framework
- [xAI](https://x.ai/) - AI model provider
- [OpenAI Python Client](https://github.com/openai/openai-python) - API client library
- [SQLite](https://www.sqlite.org/) - Database engine
