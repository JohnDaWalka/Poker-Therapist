# GitHub Copilot Instructions

> GITHUB COPILOT | WEB3 MASTER PROMPT v4.0 – OPEN SOURCE & TLD INTEGRATION
> Owner: Mauro Mark Nazareno Fanelli (@MauroMarkNaz)
> Scope: Full-Stack Web3 • Legacy → Future Chains • AI Agents • Auto-Tool Fetch
> NEW: Open-Source & TLD Heuristic Engine

## 9. TOOL & EXTENSION HEURISTIC (NEW)

Auto-detects need → scans top-level domains (TLDs) & open-source repos for tools

### Tool Engine Configuration

```python
TOOL_ENGINE = {
   "ENABLED": True,
   "DOMAINS": [
       "github.com", "npmjs.com", "crates.io", "pyyaml.org", "solana.fm",
       "anchor-lang.com", "openzeppelin.com/contracts", "wormhole.com/docs",
       "jup.ag", "birdeye.so", "helius.xyz", "quicknode.com",
       "unpkg.com", "jsdelivr.com", "gitlab.com", "bitbucket.org",
       "sourceforge.net", "codeberg.org", "gitea.io"
   ],
   "LICENSES": ["MIT", "Apache-2.0", "MPL-2.0", "GPL-3.0", "Unlicense"],
   "AUTO_FETCH": "always — no paid/closed libs unless audited"
}
```

### Heuristic Logic Block

```python
def suggest_tool(self, context: str) -> str:
   """Run on every suggestion — finds best open-source match from global TLDs"""
   keywords = context.lower().split()
   if "anchor" in keywords:
       return "Use Anchor CLI: `npm i -g @coral-xyz/anchor` → MIT, github.com/coral-xyz/anchor"
   if "solana" in keywords and "token" in keywords:
       return "SPL Token: `spl-token` CLI via github.com/solana-labs/solana-program-library"
   if "wormhole" in keywords:
       return "Wormhole SDK: npmjs.com/package/@certusone/wormhole-sdk → Apache-2.0"
   if "ethereum" in keywords and "proxy" in keywords:
       return "OpenZeppelin Upgrades: github.com/OpenZeppelin/openzeppelin-contracts-upgradeable"
   if "rpc" in keywords:
       return "Helius or QuickNode free tiers: helius.xyz | quicknode.com → open API docs"
   if "ai" in keywords or "agent" in keywords:
       return "Auto-use LangChain + HuggingFace: huggingface.co (MIT), langchain.js (MIT)"
   if "testing" in keywords and "fuzz" in keywords:
       return "Echidna (EVM) or QuickCheck (Rust): github.com/crytic/echidna | docs.rs/quickcheck"
   # Fallback
   return f"Search TLDs for: {' '.join(keywords)} MIT/Apache – no proprietary"
```

### Enforce in all responses

```
FORCE_OPEN_SOURCE = "Always prefer open tools. Paid? Flag as risk unless enterprise-audited."
```

## 10. EXTENSION & DEPENDENCY RESOLVER

### Dependency Hub

```python
DEPENDENCY_HUB = {
   "python": {
       "solana-py": "github.com/michaelhly/solana-py",
       "requests": "pypi.org/project/requests",
       "web3": "github.com/ethereum/web3.py"
   },
   "js": {
       "@solana/web3.js": "npmjs.com/package/@solana/web3.js",
       "@coral-xyz/anchor": "github.com/coral-xyz/anchor",
       "ethers": "npmjs.com/package/ethers"
   },
   "rust": {
       "anchor-lang": "crates.io/crates/anchor-lang",
       "spl-token": "github.com/solana-labs/solana-program-library"
   },
   "go": {
       "go-ethereum": "github.com/ethereum/go-ethereum"
   }
}
```

### Auto-inject in package files

```
INJECT_DEP = "On any new project: scan DEPENDENCY_HUB + suggest latest open version"
```

## 11. FINAL DIRECTIVE (UPDATED)

```
EXECUTE = """
Apply all rules.
- Prioritize open-source from TLDs.
- Flag proprietary, paid, or closed code.
- If unsure → 'Verify latest at [source]'
"""
```

---

## Repository-Specific Guidelines

### Poker Therapist Application

This repository contains an AI-powered poker coaching application with:
- Multi-provider AI support (OpenAI, Anthropic, Google Gemini, x.ai Grok, Perplexity AI)
- Voice capabilities with Rex personality
- Streamlit chatbot with persistent memory
- Python-based backend with Streamlit UI
- FastAPI endpoints for API functionality
- Vercel deployment support
- Authentication support (Microsoft, Google, Apple)

### Key Technologies

- **Frontend**: Streamlit (primary UI), Vue.js components
- **Backend**: Python, FastAPI
- **AI Providers**: OpenAI, Anthropic, Google, x.ai, Perplexity
- **Database**: SQLite (for chat history)
- **Deployment**: Vercel (serverless)
- **Voice**: STT/TTS capabilities
- **Automation**: n8n workflows

### Development Practices

1. **Always use open-source tools first** - Prefer MIT, Apache-2.0, or other permissive licenses
2. **Multi-provider support** - When adding AI features, consider multiple provider options
3. **Security** - Never commit API keys or secrets to source control
4. **Testing** - Validate changes before committing
5. **Documentation** - Update relevant markdown files when making significant changes

### Code Style

- Python: Follow PEP 8 conventions
- JavaScript: ES6+ syntax
- Comments: Minimal, only when necessary for complex logic
- Environment variables: Use `.env` files for local development, never commit them

### Authentication

The application supports multiple authentication providers:
- Microsoft/Windows accounts (Azure AD)
- Google OAuth 2.0
- Apple Sign-In

When working with authentication:
- Never store credentials in code
- Use environment variables or secrets management
- Follow OAuth 2.0 / OpenID Connect best practices
- Reference existing auth documentation files

### Deployment

- Vercel is used for serverless deployment
- Configure environment variables in Vercel dashboard
- Test in development before deploying to production
- Follow the deployment checklists in repository documentation
