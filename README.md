# Poker Therapist 🎰

An AI-powered poker coaching application with advanced multimodal chatbot integration and voice capabilities.

## Features

### 🎙️ Rex - Voice-Enabled Poker Coach (ENHANCED!)
Meet Rex, your elite poker coach with advanced voice capabilities:

**Core Features:**
- **Voice Input (STR)** - Upload audio for transcription
- **Voice Output (TTS)** - Rex speaks with an authoritative voice
- **Rex Personality** - Direct, no-nonsense poker expert with decades of experience
- **CFR Analysis** - Advanced Counterfactual Regret Minimization
- **Psychological Coaching** - Mental game and wellness support
- **Multiple AI Models** - Choose from OpenAI ChatGPT, Anthropic Claude, Google Gemini, x.ai Grok, or Perplexity AI

**🆕 NEW Enhanced Voice Features:**
- 🔴 **Real-time Voice Streaming** - WebRTC streaming for instant interaction
- 🎤 **Voice-Activated Recording** - Automatic recording triggered by your voice
- 💬 **Conversation Mode** - Natural continuous dialogue with Rex
- 😊 **Emotion Analysis** - Rex detects and responds to your emotional state
- 🌍 **Multi-Language Support** - Rex speaks 8+ languages authentically
- 🎭 **Voice Cloning** - Create custom Rex voice profiles

👥 **Authorized VIP Users**: Full voice features enabled for:
- m.fanelli1@icloud.com
- johndawalka@icloud.com
- mauro.fanelli@ctstate.edu
- maurofanellijr@gmail.com
- cooljack87@icloud.com
- jdwalka@pm.me

See [VOICE_INTEGRATION.md](VOICE_INTEGRATION.md) for voice setup and [ENHANCED_VOICE_GUIDE.md](ENHANCED_VOICE_GUIDE.md) for new features guide.

### 🤖 AI Poker Coaching
Get expert poker strategy advice from multiple AI providers:
- **Perplexity AI** - Real-time, research-backed poker strategy
- **OpenAI GPT-4** - Advanced reasoning with image analysis
- **Anthropic Claude** - Deep analytical capabilities for complex situations
- **Google Gemini** - Fast multimodal hand analysis

### 💬 Streamlit Chatbot
A standalone Streamlit chatbot with persistent memory and multiple AI provider support:
- **Persistent Memory** - SQLite database stores conversation history
- **Multi-User Support** - Email-based user identification
- **Multiple AI Providers** - Choose from OpenAI ChatGPT, Anthropic Claude, Google Gemini, x.ai Grok, or Perplexity AI
- **Streaming Responses** - Real-time AI responses
- **Thinking Display** - See the AI's reasoning process (with supported providers)
- **Voice Mode** - Enable Rex's voice for immersive coaching

Quick start for Streamlit chatbot:
```bash
pip install streamlit openai sounddevice pydub scipy
# Set your preferred AI provider API key (at least one required)
export CHATBOT_PROVIDER=openai  # Options: openai, anthropic, google, xai, perplexity
export OPENAI_API_KEY=sk-your-openai-key-here
# Or use other providers:
# export ANTHROPIC_API_KEY=your-anthropic-key-here
# export GOOGLE_AI_API_KEY=your-google-key-here
# export XAI_API_KEY=xai-your-key-here
# export PERPLEXITY_API_KEY=your-perplexity-key-here
streamlit run chatbot_app.py
```

See [MULTI_PROVIDER_QUICKSTART.md](MULTI_PROVIDER_QUICKSTART.md) for detailed setup guide.

See [CHATBOT_QUICKSTART.md](CHATBOT_QUICKSTART.md) for details.

### 📊 Hand Analysis
- Interactive poker hand analysis dashboard
- Visual charts and tables
- Hand strength and rank calculations
- Winning probability assessment
- Suggested actions based on game theory

### 🖼️ Multimodal Support
- Upload hand screenshots for AI analysis
- Text + image combined analysis
- Real-time coaching feedback

### 🔄 n8n Workflow Automation (NEW!)
Automate your poker coaching workflows with n8n:
- **Automated Hand Analysis** - Batch analyze poker hands
- **Tilt Detection Alerts** - Real-time monitoring and notifications
- **Daily Coaching Reports** - Automated performance summaries
- **Multi-Platform Bots** - Discord, Slack, Telegram integration
- **Custom Workflows** - Create your own automation flows

See [n8n-workflows/README.md](n8n-workflows/README.md) and [n8n-workflows/SETUP_GUIDE.md](n8n-workflows/SETUP_GUIDE.md) for setup instructions.

[![Sourcery](https://img.shields.io/badge/Sourcery-enabled-brightgreen)](https://sourcery.ai)
## Quick Start

### Vue.js Application

1. **Clone the repository**
   ```bash
   git clone https://github.com/JohnDaWalka/Poker-Therapist.git
   cd Poker-Therapist
   ```

2. **Configure API keys**
   ```bash
   cp .env.example .env.local
   # Add your API keys to .env.local
   ```

3. **Install and run**
   ```bash
   npm install
   npm run serve
   ```

4. **Navigate to the AI Coach tab** and start chatting!

For detailed setup and API key configuration, see [docs/CHATBOT_INTEGRATION.md](docs/CHATBOT_INTEGRATION.md)

### Streamlit Chatbot

1. **Install dependencies**
   ```bash
   pip install streamlit openai
   ```

2. **Configure AI Provider API key**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # Edit .streamlit/secrets.toml and add your API key(s)
   # Add at least one: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_AI_API_KEY, XAI_API_KEY, or PERPLEXITY_API_KEY
   # Optionally set CHATBOT_PROVIDER (defaults to openai)
   ```

3. **Run the chatbot**
   ```bash
   streamlit run chatbot_app.py
   ```

For detailed documentation, see [docs/STREAMLIT_CHATBOT.md](docs/STREAMLIT_CHATBOT.md)

### ☁️ Vercel Deployment

Deploy the FastAPI backend to Vercel for serverless hosting with full authentication support:

**Quick Deploy:**
1. **Connect your repository to Vercel**
   - Visit https://vercel.com/new
   - Import the `JohnDaWalka/Poker-Therapist` repository
   - Vercel will auto-detect the `vercel.json` configuration

2. **Configure environment variables in Vercel dashboard**
   
   **Essential Variables:**
   - `XAI_API_KEY` - xAI API key for Grok
   - `OPENAI_API_KEY` - OpenAI API key for ChatGPT
   - `JWT_SECRET_KEY` - Secure random secret (generate with: `openssl rand -base64 32`)
   - `AUTHORIZED_EMAILS` - Comma-separated list of authorized users
   
   **Microsoft Authentication (for institutional SSO like @ctstate.edu):**
   - `AZURE_TENANT_ID` - Azure AD tenant ID
   - `AZURE_CLIENT_ID` - Azure AD application ID
   - `AZURE_CLIENT_SECRET` - Azure AD client secret
   - `AZURE_AUTHORITY` - Authority URL (e.g., `https://login.microsoftonline.com/common`)
   - `INSTITUTIONAL_EMAIL_DOMAIN` - Your institution domain (e.g., `ctstate.edu`)
   
   **Google Cloud Platform (for OAuth & Cloud Storage):**
   - `GOOGLE_CLOUD_PROJECT_ID` - GCP project ID
   - `GOOGLE_CLIENT_ID` - OAuth 2.0 client ID
   - `GOOGLE_CLIENT_SECRET` - OAuth 2.0 client secret
   - `GOOGLE_STORAGE_BUCKET_NAME` - Cloud Storage bucket name
   - `GOOGLE_APPLICATION_CREDENTIALS` - Base64-encoded service account JSON
   
   **Apple Sign-In (optional, for iOS):**
   - `APPLE_TEAM_ID`, `APPLE_SERVICES_ID`, `APPLE_KEY_ID`, `APPLE_PRIVATE_KEY_PATH`
   
   **See [VERCEL_ENV_SETUP.md](VERCEL_ENV_SETUP.md) for detailed variable setup instructions**

3. **Deploy**
   - Click "Deploy" and your API will be live at `https://your-app.vercel.app`!

**Complete Documentation:**
- [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) - Comprehensive deployment guide with authentication setup
- [VERCEL_DEPLOYMENT_CHECKLIST.md](VERCEL_DEPLOYMENT_CHECKLIST.md) - Step-by-step deployment checklist
- [VERCEL_ENV_SETUP.md](VERCEL_ENV_SETUP.md) - Environment variables setup guide
- [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) - Complete authentication provider setup
- [AUTH_QUICKSTART.md](AUTH_QUICKSTART.md) - Quick authentication setup

**What's Supported:**
✅ Full FastAPI backend with all API routes  
✅ Microsoft Azure AD authentication (Windows accounts, institutional SSO)  
✅ Google OAuth 2.0 authentication  
✅ Apple Sign-In authentication (iOS/macOS/watchOS)  
✅ JWT token-based authorization  
✅ Google Cloud Storage integration  
✅ Serverless deployment (auto-scaling)  
✅ Automatic HTTPS  
✅ Environment-based configuration  

**Limitations:**
- Serverless functions have execution time limits (10s Hobby, 60s Pro)
- No persistent file system (use Cloud Storage instead)
- Cold start latency on first request (~2-3s)
- Not suitable for long-running processes or WebSockets

---

## Original Project: Autonomous Advent of Code

- Each day during advent of code this repo solves the latest puzzle and submits the solution - all without human intervention
- All code in this repo was written by `sourcery-ai[bot]`
- Everything was set up by manually writing [five issues](https://github.com/JohnDaWalka/test-aoc/labels/inception) and asking `sourcery-ai[bot]` to implement them
- Since then everything runs fully autonomously

## Original Advent of Code Process

There are two main processes that work together to solve the puzzles:

- Four GitHub actions workflows download the puzzles, create issues for `sourcery-ai[bot]` to solve the puzzles, merge PRs, and submit solutions. All actions they perform are carried out by @SourceryAI which is a GitHub account not associated with a real person
- `sourcery-ai[bot]` solves the puzzles and opens pull requests with the solutions and answers

## How does it work?

Here are the steps:

1. Twelve hours after each puzzle is published a GitHub actions workflow [^1]:
   - Download the puzzle and input
   - ROT13 encode the puzzle [^2]
   - Commit both to the puzzle directory and push to `main`
   - This triggers step 2
2. A GitHub action workflow is triggered when puzzles are pushed to main:
   - Create a GitHub issue to solve the part
   - Post an issue comment with content `@sourcery-ai develop`
   - This triggers step 3
3. `sourcery-ai[bot]` listens to the comment:
   - Runs a script to ROT13 decode the puzzle
   - Posts a plan to the issue to solve the puzzle
   - Opens a pull request to implement the solution and write the solution
   - This triggers step 4
4. A GitHub action workflow is triggered when pull requests are opened
   - It merges pull requests only if the author is `sourcery-ai[bot]`
   - This triggers step 5
5. A GitHub action workflow is triggered when answers are pushed to `main`
   - It submits the answer to advent of code
   - It updates the results below
   - If the answer is correct and it was for part 1, it downloads the second part of the puzzle and commits it
   - This triggers step 2

How `sourcery-ai[bot]` works:

- When a member of a repo comments on an issue with `@sourcery-ai develop` it will post a plan to the issue, open a pull request with the solution, and request a review from the commenter
- If any review comments are left on its pull request it will address them and push new commits

## Results

Here are the puzzles attempted and whether they were successfully solved or not.

<!-- begin-results: 2024 -->
<!-- end-results: 2024 -->

## Try out Sourcery

`sourcery-ai[bot]` is an GitHub app with two main functions:

- Issue agent
  - Comment an issue with `@sourcery-ai plan` to post a comment with a planned implementation
  - Comment and issue with `@sourcery-ai develop` to open a pull request to resolve the issue 👈 the functionality on display in this repo
- Pull request agent
  - Automatically reviews pull requests
  - Generates pull request titles / bodies
  - Generates review guides with diagrams explaining the changes

The functionality in this repo (`@sourcery-ai develop`) is currently in alpha testing and will be generally available in the new year. As well as the functionality shown here it will:

- Run in GitHub / GitLab - cloud and self-hosted
- Integrate with issue trackers - Linear, Jira
- Resolve errors in production - Sentry, etc.

It will be most useful for handling routine maintenance and clearing your backlog by:

- Fixing bugs
- Implementing smaller features
- Automatically fixing production issues
- Writing documentation

If you like the sound of this, [join our waitlist](https://getsourcery.netlify.app/) and tell us anything else you want it to do.

## Triggering the `merge-repos` Workflow

To trigger the `merge-repos` workflow, you need to dispatch a repository event with the event type `merge-repos`. You can do this using the GitHub API or the `gh` CLI tool.

### Example using `gh` CLI

```sh
gh api repos/:owner/:repo/dispatches --field event_type=merge-repos --field client_payload='{"source_repo": "source-repo-name", "target_repo": "target-repo-name"}'
```

Replace `:owner` with the repository owner, `:repo` with the repository name, `source-repo-name` with the name of the source repository, and `target-repo-name` with the name of the target repository.

### Example using GitHub API

```sh
curl -X POST -H "Accept: application/vnd.github.v3+json" -H "Authorization: token YOUR_GITHUB_TOKEN" https://api.github.com/repos/:owner/:repo/dispatches -d '{"event_type":"merge-repos","client_payload":{"source_repo":"source-repo-name","target_repo":"target-repo-name"}}'
```

Replace `YOUR_GITHUB_TOKEN` with your GitHub token, `:owner` with the repository owner, `:repo` with the repository name, `source-repo-name` with the name of the source repository, and `target-repo-name` with the name of the target repository.

## Rotating `GH_TOKEN` Regularly

To rotate the `GH_TOKEN` regularly, follow these steps:

1. Generate a new GitHub token with the required permissions.
2. Update the GitHub Secrets in your repository settings with the new token.
3. Update any local environment variables or configuration files that use the `GH_TOKEN`.
4. Monitor the usage of the new token to ensure it is working correctly.
5. Revoke the old token to minimize the risk of unauthorized access.

## Monitoring the Usage of `GH_TOKEN`

To monitor the usage of the `GH_TOKEN`, follow these best practices:

1. Enable GitHub's security features, such as security alerts and vulnerability scanning, to detect any suspicious activity.
2. Regularly review the audit logs in your GitHub repository to track the usage of the `GH_TOKEN`.
3. Set up notifications for any unusual activity or changes in the repository.
4. Use third-party tools or services to monitor the usage of the `GH_TOKEN` and detect any potential security issues.
5. Periodically review and update the permissions assigned to the `GH_TOKEN` to ensure they are still necessary and appropriate.
curl -X POST -H "Accept: application/vnd.github.v3+json" -H "Authorization: token YOUR_GITHUB_TOKEN" https://api.github.com/repos/:owner/:repo/dispatches -d '{"event_type":"merge-repos","client_payload":{"source_repo":"source-repo-name","target_repo":"target-repo-name"}}'
Poker Therapist 🎰
[](https://github.com/JohnDaWalka/Poker-Therapist/tree/copilot/implement-perplexity-ai-bots#poker-therapist-)
An AI-powered poker coaching application with advanced multimodal chatbot integration.
Features
[](https://github.com/JohnDaWalka/Poker-Therapist/tree/copilot/implement-perplexity-ai-bots#features)
🤖 AI Poker Coaching
[](https://github.com/JohnDaWalka/Poker-Therapist/tree/copilot/implement-perplexity-ai-bots#-ai-poker-coaching)
Get expert poker strategy advice from multiple AI providers:
Perplexity AI - Real-time, research-backed poker strategy
OpenAI GPT-4 - Advanced reasoning with image analysis
Anthropic Claude - Deep analytical capabilities for complex situations
Google Gemini - Fast multimodal hand analysis
📊 Hand Analysis
[](https://github.com/JohnDaWalka/Poker-Therapist/tree/copilot/implement-perplexity-ai-bots#-hand-analysis)
Interactive poker hand analysis dashboard
Visual charts and tables
Hand strength and rank calculations
Winning probability assessment
Suggested actions based on game theory
🖼️ Multimodal Support
[](https://github.com/JohnDaWalka/Poker-Therapist/tree/copilot/implement-perplexity-ai-bots#%EF%B8%8F-multimodal-support)
Upload hand screenshots for AI analysis
Text + image combined analysis
Real-time coaching feedback ---lets add some more personal features so that me as the sreator and test subject can have the most benfit\
