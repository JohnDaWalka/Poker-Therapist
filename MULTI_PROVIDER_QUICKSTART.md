# Multi-Provider Chatbot Quick Start Guide

## Overview

The Poker Therapist chatbot now supports multiple AI providers! Choose from:
- **OpenAI ChatGPT** (GPT-4, GPT-3.5) - Default, recommended
- **Anthropic Claude** - Deep analytical capabilities
- **Google Gemini** - Fast multimodal processing
- **x.ai Grok** - Real-time information with thinking display
- **Perplexity AI** - Research-backed responses with citations

## Quick Setup (5 Minutes)

### 1. Install Dependencies

```bash
pip install streamlit openai
```

### 2. Configure Your AI Provider

Choose ONE of the following options based on your preferred AI provider:

#### Option A: OpenAI ChatGPT (Recommended)

```bash
# Copy environment file
cp .env.example .env.local

# Edit .env.local and set:
CHATBOT_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key-here
```

Get your API key: https://platform.openai.com/api-keys

#### Option B: Anthropic Claude

```bash
# Edit .env.local and set:
CHATBOT_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

Get your API key: https://console.anthropic.com/

#### Option C: Google Gemini

```bash
# Edit .env.local and set:
CHATBOT_PROVIDER=google
GOOGLE_AI_API_KEY=your-google-api-key-here
```

Get your API key: https://makersuite.google.com/app/apikey

#### Option D: x.ai Grok

```bash
# Edit .env.local and set:
CHATBOT_PROVIDER=xai
XAI_API_KEY=xai-your-api-key-here
```

Get your API key: https://x.ai/api

#### Option E: Perplexity AI

```bash
# Edit .env.local and set:
CHATBOT_PROVIDER=perplexity
PERPLEXITY_API_KEY=your-perplexity-api-key-here
```

Get your API key: https://www.perplexity.ai/settings/api

### 3. Run the Chatbot

```bash
streamlit run chatbot_app.py
```

The app will open at http://localhost:8501

## Using Streamlit Secrets (Alternative)

Instead of `.env.local`, you can use Streamlit secrets:

```bash
# Copy secrets template
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit .streamlit/secrets.toml
nano .streamlit/secrets.toml
```

Add your configuration:

```toml
# Choose your provider
CHATBOT_PROVIDER = "openai"  # or anthropic, google, xai, perplexity

# Add the corresponding API key
OPENAI_API_KEY = "sk-your-key-here"
# ANTHROPIC_API_KEY = "your-key-here"
# GOOGLE_AI_API_KEY = "your-key-here"
# XAI_API_KEY = "xai-your-key-here"
# PERPLEXITY_API_KEY = "your-key-here"
```

## Switching Providers

You can switch AI providers in two ways:

### Method 1: In the UI

1. Open the chatbot at http://localhost:8501
2. Look in the sidebar under "🤖 AI Model Settings"
3. Select your preferred provider from the dropdown
4. The chatbot will automatically use the new provider

### Method 2: Via Environment Variable

```bash
# Change the CHATBOT_PROVIDER in .env.local or secrets.toml
CHATBOT_PROVIDER=anthropic  # Change to your preferred provider

# Restart the app
streamlit run chatbot_app.py
```

## Configuring Multiple Providers

You can configure multiple API keys and switch between them:

```bash
# In .env.local, add all your API keys:
CHATBOT_PROVIDER=openai  # Default provider

OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_AI_API_KEY=your-google-key
XAI_API_KEY=xai-your-xai-key
PERPLEXITY_API_KEY=your-perplexity-key
```

Then switch providers using the dropdown in the UI!

## Provider Comparison

| Provider | Model | Best For | Thinking Display |
|----------|-------|----------|------------------|
| **OpenAI** | GPT-4 Turbo | General purpose, coding | ❌ |
| **Anthropic** | Claude 3.5 Sonnet | Deep analysis, long context | ❌ |
| **Google** | Gemini 1.5 Pro | Multimodal, speed | ❌ |
| **x.ai** | Grok Beta | Real-time info, reasoning | ✅ |
| **Perplexity** | Llama 3.1 Sonar | Research, citations | ✅ |

## Troubleshooting

### "API key not found" Error

Make sure you've:
1. Added the API key to `.env.local` or `.streamlit/secrets.toml`
2. Used the correct environment variable name
3. Restarted the Streamlit app after adding the key

### "No AI providers configured" Warning

This means no API keys were found. You need to configure at least one provider's API key.

### Provider Dropdown is Empty

Check that:
1. At least one API key is configured
2. The API key variable names match exactly (case-sensitive)
3. The `.env.local` file is in the project root

### Streaming Not Working

Some providers may have streaming issues. If you see errors:
1. Check your internet connection
2. Verify the API key is valid and has sufficient credits
3. Try setting `ENABLE_STREAMING = false` in secrets.toml

## Cost Information

Approximate costs per 1000 messages (varies by usage):

- **OpenAI GPT-4**: ~$3-5 (input/output costs)
- **Anthropic Claude**: ~$3-4
- **Google Gemini**: Free tier available, then ~$0.50
- **x.ai Grok**: Varies, check x.ai pricing
- **Perplexity**: ~$5-7 (includes research)

Always check the provider's official pricing page for current rates.

## Advanced Features

### Voice Integration

Voice features work with all providers but use OpenAI for TTS/STR:

```bash
# Enable voice features
VOICE_ENABLED=true
VOICE_PROVIDER=openai

# Add OpenAI key for voice
OPENAI_API_KEY=sk-your-openai-key
```

### Rex Personality (VIP Users)

Authorized users get access to Rex, the poker coach personality:

```bash
# Add your email to authorized list
AUTHORIZED_EMAILS=your-email@example.com
```

### Custom Configuration

You can customize streaming and thinking display:

```toml
# In secrets.toml
ENABLE_STREAMING = true
ENABLE_THINKING = true  # Only works with Grok and Perplexity
```

## Next Steps

- Read the full documentation: [docs/STREAMLIT_CHATBOT.md](docs/STREAMLIT_CHATBOT.md)
- Explore voice features: [VOICE_INTEGRATION.md](VOICE_INTEGRATION.md)
- Set up authentication: [AUTH_QUICKSTART.md](AUTH_QUICKSTART.md)
- Deploy to production: [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)

## Getting Help

- 📖 Documentation: See the docs/ directory
- 🐛 Issues: https://github.com/JohnDaWalka/Poker-Therapist/issues
- 💬 Discussions: GitHub Discussions tab

## Security Note

🔒 **Never commit your API keys to version control!**

The following files are automatically ignored by git:
- `.env.local`
- `.streamlit/secrets.toml`
- Any file with "secret" or "key" in the name

Keep your API keys secure and rotate them regularly.

---

Happy chatting! 🎰🤖
