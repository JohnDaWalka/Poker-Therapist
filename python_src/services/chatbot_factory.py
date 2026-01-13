"""Unified chatbot client factory for multiple AI providers."""

import os
from typing import Any, Dict, List, Optional, Union

from openai import OpenAI


class ChatbotProvider:
    """Supported chatbot providers."""
    
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    XAI = "xai"
    PERPLEXITY = "perplexity"


class UnifiedChatbotClient:
    """Unified interface for different chatbot providers."""
    
    def __init__(self, provider: str = "openai"):
        """Initialize chatbot client with specified provider.
        
        Args:
            provider: Provider name (openai, anthropic, google, xai, perplexity)
        """
        self.provider = provider.lower()
        self.client = None
        self.model = None
        self._anthropic_client = None  # For Anthropic native API
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the appropriate client based on provider."""
        if self.provider == ChatbotProvider.OPENAI:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "OPENAI_API_KEY not found. "
                    "Please configure in secrets.toml or environment."
                )
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-4-turbo-preview"
            
        elif self.provider == ChatbotProvider.ANTHROPIC:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "ANTHROPIC_API_KEY not found. "
                    "Please configure in secrets.toml or environment."
                )
            # Anthropic uses its own client, wrap it for unified interface
            try:
                import anthropic
                self._anthropic_client = anthropic.Anthropic(api_key=api_key)
                self.client = None  # We'll handle this differently
                self.model = "claude-3-5-sonnet-20241022"
            except ImportError:
                raise RuntimeError(
                    "Anthropic package not installed. "
                    "Install with: pip install anthropic"
                )
            
        elif self.provider == ChatbotProvider.GOOGLE:
            api_key = os.getenv("GOOGLE_AI_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "GOOGLE_AI_API_KEY not found. "
                    "Please configure in secrets.toml or environment."
                )
            # Use OpenAI-compatible interface
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            self.model = "gemini-1.5-pro-latest"
            
        elif self.provider == ChatbotProvider.XAI:
            api_key = os.getenv("XAI_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "XAI_API_KEY not found. "
                    "Please configure in secrets.toml or environment."
                )
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.x.ai/v1"
            )
            self.model = "grok-beta"
            
        elif self.provider == ChatbotProvider.PERPLEXITY:
            api_key = os.getenv("PERPLEXITY_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "PERPLEXITY_API_KEY not found. "
                    "Please configure in secrets.toml or environment."
                )
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.perplexity.ai"
            )
            self.model = "llama-3.1-sonar-large-128k-online"
            
        else:
            raise ValueError(
                f"Unknown provider: {self.provider}. "
                f"Supported providers: {', '.join([ChatbotProvider.OPENAI, ChatbotProvider.ANTHROPIC, ChatbotProvider.GOOGLE, ChatbotProvider.XAI, ChatbotProvider.PERPLEXITY])}"
            )
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Any:
        """Create chat completion with unified interface.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            stream: Whether to stream responses
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            Completion response (streaming or non-streaming)
        """
        # Special handling for Anthropic which uses different API
        if self.provider == ChatbotProvider.ANTHROPIC:
            # Separate system messages from conversation
            system_message = None
            conversation_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    conversation_messages.append(msg)
            
            # Use Anthropic's native API
            kwargs = {
                "model": self.model,
                "messages": conversation_messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4096,
                "stream": stream,
            }
            
            if system_message:
                kwargs["system"] = system_message
            
            response = self._anthropic_client.messages.create(**kwargs)
            
            # Convert Anthropic response to OpenAI-compatible format
            if not stream:
                # Convert non-streaming response
                class AnthropicResponse:
                    def __init__(self, anthropic_resp):
                        self.choices = [type('obj', (), {
                            'message': type('obj', (), {
                                'content': anthropic_resp.content[0].text
                            })()
                        })()]
                
                return AnthropicResponse(response)
            else:
                # For streaming, we'll need to convert each chunk
                def anthropic_stream_wrapper():
                    for chunk in response:
                        if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                            # Convert to OpenAI-compatible format
                            yield type('obj', (), {
                                'choices': [type('obj', (), {
                                    'delta': type('obj', (), {
                                        'content': chunk.delta.text
                                    })()
                                })()]
                            })()
                
                return anthropic_stream_wrapper()
        
        # For other providers, use OpenAI-compatible interface
        kwargs = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": temperature,
        }
        
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        
        return self.client.chat.completions.create(**kwargs)
    
    def get_provider_info(self) -> Dict[str, str]:
        """Get information about current provider.
        
        Returns:
            Dict with provider, model, and display name
        """
        display_names = {
            ChatbotProvider.OPENAI: "OpenAI ChatGPT",
            ChatbotProvider.ANTHROPIC: "Anthropic Claude",
            ChatbotProvider.GOOGLE: "Google Gemini",
            ChatbotProvider.XAI: "x.ai Grok",
            ChatbotProvider.PERPLEXITY: "Perplexity AI"
        }
        
        return {
            "provider": self.provider,
            "model": self.model,
            "display_name": display_names.get(self.provider, self.provider)
        }


def get_chatbot_client(provider: Optional[str] = None) -> UnifiedChatbotClient:
    """Factory function to get chatbot client.
    
    Args:
        provider: Provider name. If None, uses CHATBOT_PROVIDER env var or defaults to openai
        
    Returns:
        Initialized UnifiedChatbotClient
    """
    if provider is None:
        provider = os.getenv("CHATBOT_PROVIDER", "openai")
    
    return UnifiedChatbotClient(provider)


def get_available_providers() -> List[Dict[str, str]]:
    """Get list of available providers based on configured API keys.
    
    Returns:
        List of dicts with provider info
    """
    providers = []
    
    provider_configs = [
        (ChatbotProvider.OPENAI, "OPENAI_API_KEY", "OpenAI ChatGPT (GPT-4)"),
        (ChatbotProvider.ANTHROPIC, "ANTHROPIC_API_KEY", "Anthropic Claude"),
        (ChatbotProvider.GOOGLE, "GOOGLE_AI_API_KEY", "Google Gemini"),
        (ChatbotProvider.XAI, "XAI_API_KEY", "x.ai Grok"),
        (ChatbotProvider.PERPLEXITY, "PERPLEXITY_API_KEY", "Perplexity AI"),
    ]
    
    for provider_id, env_var, display_name in provider_configs:
        if os.getenv(env_var):
            providers.append({
                "id": provider_id,
                "name": display_name,
                "env_var": env_var
            })
    
    return providers
