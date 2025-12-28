# 🎰 Poker Therapist - Quick Start Guide

## Get Started in 3 Minutes!

### Step 1: Get Your API Keys (2 minutes)

You need at least **one** API key. Choose your preferred provider:

#### Option A: Perplexity AI (Recommended for starters)
1. Go to https://www.perplexity.ai/settings/api
2. Sign up or log in
3. Generate an API key
4. Copy the key

#### Option B: OpenAI GPT-4 (Best for image analysis)
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy the key

#### Option C: Anthropic Claude (Advanced reasoning)
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Get API key
4. Copy the key

#### Option D: Google Gemini (Fast & multimodal)
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Create API key
4. Copy the key

### Step 2: Configure the App (30 seconds)

```bash
# In the project directory
cp .env.example .env.local
```

Open `.env.local` and add your API key(s):

```env
# Add at least one:
VUE_APP_PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxx
VUE_APP_OPENAI_API_KEY=sk-xxxxxxxxxxxxx
VUE_APP_ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
VUE_APP_GEMINI_API_KEY=AIzaxxxxxxxxxxxxx
```

### Step 3: Run the App (30 seconds)

```bash
npm install
npm run serve
```

Open http://localhost:8080 in your browser.

## Using the AI Coach

### Basic Chat

1. Click the **"AI Coach"** tab
2. Type your question: 
   ```
   "I have pocket aces in early position. What should I do?"
   ```
3. Press Enter or click **Send**
4. Get expert advice!

### Image Analysis (Requires OpenAI, Claude, or Gemini)

1. Click the **📷 camera icon**
2. Upload a screenshot of your poker hand
3. Add optional description
4. Click **Send**
5. AI analyzes the image and provides advice!

### Quick Actions

Click pre-made buttons for instant help:
- **Analyze Hand** - Get detailed hand analysis
- **GTO Strategy** - Learn optimal play
- **Calculate Odds** - Get pot odds and equity

### Switch AI Providers

Use the dropdown menu to switch between:
- Perplexity AI
- OpenAI GPT-4
- Claude (Anthropic)
- Google Gemini

Each has different strengths!

## Example Questions

Try asking:

```
"Should I call or fold with a flush draw on the turn?"
```

```
"What's the GTO strategy for defending big blind vs button raise?"
```

```
"Analyze this hand: I had AK, raised pre-flop, got called..."
```

```
"What hands should I 3-bet from the small blind?"
```

## Tips

💡 **For best results:**
- Be specific about your position, stack sizes, and opponents
- Include the betting action
- Ask follow-up questions
- Try different AI providers for varied perspectives

💡 **Image analysis:**
- Take clear screenshots
- Ensure cards are visible
- Include board and bet sizes
- Works with OpenAI, Claude, and Gemini only

💡 **Save API costs:**
- Start with one provider
- Perplexity is usually most cost-effective
- Be mindful of usage limits

## Troubleshooting

### "Provider not available"
- Check API key is in `.env.local`
- Verify API key is valid
- Restart the dev server (`npm run serve`)

### "API Error"
- Check your API key
- Verify you have credits/quota
- Try a different provider

### Image upload not working
- Make sure you're using OpenAI, Claude, or Gemini
- Perplexity doesn't support images
- Check file size (keep under 5MB)

## Need More Help?

📚 **Full Documentation:**
- [Setup Guide](docs/CHATBOT_INTEGRATION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Implementation Details](docs/IMPLEMENTATION_SUMMARY.md)

🐛 **Found a bug?**
Open an issue on GitHub!

🎉 **Enjoy your AI poker coach!**
