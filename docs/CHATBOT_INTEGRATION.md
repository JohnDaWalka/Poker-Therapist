# Poker Therapist - AI Chatbot Integration

This document describes the Perplexity AI and multimodal chatbot implementation for the Poker Therapist application.

## Overview

The Poker Therapist now includes a sophisticated AI coaching system that leverages multiple AI providers to offer expert poker strategy advice. The system supports:

- **Text-based coaching** for strategy questions and hand analysis
- **Multimodal analysis** (text + images) for analyzing hand screenshots
- **Multiple AI providers** with easy switching between them
- **Conversation history** for context-aware responses

## Supported AI Providers

### 1. Perplexity AI
- **Model**: llama-3.1-sonar-large-128k-online
- **Strengths**: Real-time, research-backed advice with access to latest poker theory
- **Best for**: Strategy questions, hand analysis, current meta insights

### 2. OpenAI GPT-4
- **Model**: gpt-4o (multimodal)
- **Strengths**: Advanced reasoning, image analysis, comprehensive explanations
- **Best for**: Multimodal analysis, detailed strategy breakdowns, hand screenshots

### 3. Anthropic Claude
- **Model**: claude-3-5-sonnet-20241022
- **Strengths**: Deep analytical capabilities, nuanced reasoning
- **Best for**: Complex hand histories, tournament strategy, GTO analysis

### 4. Google Gemini
- **Model**: gemini-1.5-pro
- **Strengths**: Multimodal understanding, fast responses
- **Best for**: Quick analysis, image-based hand reading, real-time coaching

## Setup

### Configure API Keys

Copy the example environment file:

```bash
cp .env.example .env.local
```

Add your API keys to `.env.local`:

```env
VUE_APP_PERPLEXITY_API_KEY=your_perplexity_api_key_here
VUE_APP_OPENAI_API_KEY=your_openai_api_key_here
VUE_APP_ANTHROPIC_API_KEY=your_anthropic_api_key_here
VUE_APP_GEMINI_API_KEY=your_gemini_api_key_here
```

### Obtain API Keys

- **Perplexity AI**: https://www.perplexity.ai/settings/api
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Google Gemini**: https://makersuite.google.com/app/apikey

Note: You don't need all API keys - configure only the providers you want to use. At least one provider must be configured.

## Usage

Navigate to the "AI Coach" tab and start chatting with the poker coach AI!

For more details, see the full documentation.
