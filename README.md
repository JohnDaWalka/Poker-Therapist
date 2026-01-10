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
- **Google Gemini 2.0 Powered** - Latest Gemini 2.0 Flash for intelligent responses

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
- **Google Gemini 2.0** - Fast multimodal hand analysis with latest AI capabilities

### 💬 Streamlit Chatbot
A standalone Streamlit chatbot with persistent memory:
- **Persistent Memory** - SQLite database stores conversation history
- **Multi-User Support** - Email-based user identification
- **Google Gemini 2.0 Integration** - Powered by latest Gemini 2.0 Flash model
- **Streaming Responses** - Real-time AI responses
- **Thinking Display** - See the AI's reasoning process
- **Voice Mode** - Enable Rex's voice for immersive coaching

Quick start for Streamlit chatbot:
```bash
pip install streamlit openai sounddevice pydub scipy google-generativeai
# Set your API keys
export GOOGLE_API_KEY=your-google-api-key-here
export OPENAI_API_KEY=sk-your-openai-key-here  # For voice features
streamlit run chatbot_app.py
```

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
   pip install streamlit openai google-generativeai
   ```

2. **Configure Google API key**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # Edit .streamlit/secrets.toml and add your Google API key
   ```

3. **Run the chatbot**
   ```bash
   streamlit run chatbot_app.py
   ```

For detailed documentation, see [docs/STREAMLIT_CHATBOT.md](docs/STREAMLIT_CHATBOT.md)

### ☁️ Vercel Deployment

Deploy the FastAPI backend to Vercel for serverless hosting:

1. **Connect your repository to Vercel**
   - Visit https://vercel.com/new
   - Import the repository
   - Vercel will auto-detect the `vercel.json` configuration

2. **Configure environment variables in Vercel dashboard**
   - `GOOGLE_API_KEY` (required for Gemini 2.0)
   - `OPENAI_API_KEY` (optional, for voice features)
   - `ANTHROPIC_API_KEY` (optional)
   - `XAI_API_KEY`
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY` (optional)
   - `GOOGLE_API_KEY` (optional)
   - `AUTHORIZED_EMAILS`

3. **Deploy**
   - Click "Deploy" and your API will be live!

For detailed deployment instructions, see [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)

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
