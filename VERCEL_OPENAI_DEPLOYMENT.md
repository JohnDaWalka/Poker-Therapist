# Vercel Deployment with OpenAI API Key

## Overview

The Poker Therapist application has been updated to support flexible API key configuration, allowing deployment with just the `OPENAI_API_KEY` configured. The application will automatically use available API providers and provide clear error messages when required keys are missing.

## Minimum Deployment Requirements

### Required for Basic Functionality
- **OPENAI_API_KEY**: Required for triage and hand analysis features

### Optional API Keys
- **XAI_API_KEY**: Preferred for quick triage (Grok is faster), falls back to OpenAI
- **PERPLEXITY_API_KEY**: Additional analysis for hand analysis and session review
- **ANTHROPIC_API_KEY**: Required for deep therapy sessions and voice/video analysis
- **GOOGLE_AI_API_KEY**: Required for voice rants and video session analysis

## Deployment Steps

### 1. Set Environment Variables in Vercel

```bash
# Required
vercel env add OPENAI_API_KEY production

# Optional (add as needed)
vercel env add XAI_API_KEY production
vercel env add PERPLEXITY_API_KEY production
vercel env add ANTHROPIC_API_KEY production
vercel env add GOOGLE_AI_API_KEY production
```

### 2. Deploy

```bash
vercel deploy --prod
```

## Feature Availability by API Key

| Feature | Required Keys | Fallback Behavior |
|---------|---------------|-------------------|
| Quick Triage | XAI_API_KEY OR OPENAI_API_KEY | Prefers Grok, falls back to OpenAI |
| Hand Analysis | PERPLEXITY_API_KEY OR OPENAI_API_KEY | Works with either or both |
| Session Review | PERPLEXITY_API_KEY OR OPENAI_API_KEY | Works with either or both |
| Deep Therapy | ANTHROPIC_API_KEY | No fallback, requires Claude |
| Voice Rant | GOOGLE_AI_API_KEY + ANTHROPIC_API_KEY | No fallback, requires both |
| Session Video | GOOGLE_AI_API_KEY + ANTHROPIC_API_KEY | No fallback, requires both |

## Architecture Changes

### Before
- All AI clients initialized at startup
- Application crashed if any API key was missing
- No fallback mechanisms

### After
- AI clients initialize without API keys
- Availability checked at runtime
- Intelligent fallbacks for triage and analysis
- Clear error messages for unavailable features

## Error Messages

Users will receive clear error messages when trying to use features without required API keys:

- **Triage without keys**: "No triage client available. Configure XAI_API_KEY or OPENAI_API_KEY."
- **Hand analysis without keys**: "Hand analysis requires Perplexity or OpenAI. Configure PERPLEXITY_API_KEY or OPENAI_API_KEY."
- **Deep therapy without Claude**: "Deep therapy requires Claude. Configure ANTHROPIC_API_KEY."
- **Voice features without Gemini**: "Voice rant requires Gemini for transcription. Configure GOOGLE_AI_API_KEY."

## Testing Deployment

After deploying, test the available features:

```bash
# Test health endpoint
curl https://your-app.vercel.app/health

# Test triage endpoint (should work with OPENAI_API_KEY)
curl -X POST https://your-app.vercel.app/api/triage \
  -H "Content-Type: application/json" \
  -d '{
    "situation": "Lost a big pot",
    "emotion": "frustrated",
    "intensity": 7,
    "body_sensation": "tight chest",
    "still_playing": true,
    "user_id": "test-user"
  }'
```

## Cost Optimization

Deploy with only the API keys you need to minimize costs:

- **Budget deployment**: Only OPENAI_API_KEY (triage + hand analysis)
- **Standard deployment**: OPENAI_API_KEY + XAI_API_KEY (faster triage)
- **Full deployment**: All keys (all features available)

## Security Notes

- Never commit API keys to source control
- Use Vercel's environment variable management
- Rotate keys regularly
- Monitor API usage in provider dashboards
- Set up usage alerts to prevent unexpected charges

## Troubleshooting

### Application won't start
- Ensure at least OPENAI_API_KEY is configured
- Check Vercel logs: `vercel logs`
- Verify API key format is correct

### Feature unavailable
- Check error message for required API keys
- Verify keys are set in Vercel environment
- Test keys locally first

### Slow response times
- Add XAI_API_KEY for faster triage
- Consider upgrading API tier for higher rate limits
- Monitor API provider status pages

## Support

For issues or questions:
1. Check error messages for missing API keys
2. Verify environment variables in Vercel dashboard
3. Test with minimal configuration first (OPENAI_API_KEY only)
4. Gradually add optional keys as needed
