#!/usr/bin/env python3
"""Test script for multi-provider chatbot support."""

import os
import sys
from pathlib import Path

# Add python_src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python_src.services.chatbot_factory import (
    get_chatbot_client,
    get_available_providers,
    ChatbotProvider,
    UnifiedChatbotClient,
)


def test_provider_constants():
    """Test that provider constants are defined."""
    print("Testing provider constants...")
    assert ChatbotProvider.OPENAI == "openai"
    assert ChatbotProvider.ANTHROPIC == "anthropic"
    assert ChatbotProvider.GOOGLE == "google"
    assert ChatbotProvider.XAI == "xai"
    assert ChatbotProvider.PERPLEXITY == "perplexity"
    print("✅ All provider constants defined correctly")


def test_get_available_providers():
    """Test getting available providers based on configured API keys."""
    print("\nTesting available providers detection...")
    
    # Set a mock API key
    os.environ['OPENAI_API_KEY'] = 'sk-test-12345'
    os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-test-12345'
    
    providers = get_available_providers()
    print(f"Found {len(providers)} available provider(s):")
    for p in providers:
        print(f"  - {p['name']}")
    
    assert len(providers) >= 1, "At least one provider should be available"
    print("✅ Provider detection working")


def test_client_creation():
    """Test creating clients for different providers."""
    print("\nTesting client creation...")
    
    providers_to_test = [
        ("openai", "OPENAI_API_KEY", "sk-test-12345", True),
        ("anthropic", "ANTHROPIC_API_KEY", "sk-ant-test-12345", False),  # Optional
        ("google", "GOOGLE_AI_API_KEY", "AIzaTest12345", True),
        ("xai", "XAI_API_KEY", "xai-test-12345", True),
        ("perplexity", "PERPLEXITY_API_KEY", "pplx-test-12345", True),
    ]
    
    for provider_id, env_var, test_key, required in providers_to_test:
        print(f"\n  Testing {provider_id}...")
        os.environ[env_var] = test_key
        
        try:
            client = get_chatbot_client(provider_id)
            info = client.get_provider_info()
            
            assert info['provider'] == provider_id
            assert info['model'] is not None
            assert info['display_name'] is not None
            
            print(f"    ✅ {info['display_name']} - {info['model']}")
        except RuntimeError as e:
            if "package not installed" in str(e) and not required:
                print(f"    ⚠️  Skipped (optional dependency not installed)")
            else:
                print(f"    ❌ Error: {e}")
                if required:
                    raise
        except Exception as e:
            print(f"    ❌ Error: {e}")
            if required:
                raise


def test_unified_interface():
    """Test that all providers use the same interface."""
    print("\nTesting unified interface...")
    
    os.environ['OPENAI_API_KEY'] = 'sk-test-12345'
    client = get_chatbot_client("openai")
    
    # Check that client has required methods
    assert hasattr(client, 'chat_completion')
    assert hasattr(client, 'get_provider_info')
    
    # Check that chat_completion has correct signature
    import inspect
    sig = inspect.signature(client.chat_completion)
    params = list(sig.parameters.keys())
    assert 'messages' in params
    assert 'stream' in params
    assert 'temperature' in params
    
    print("✅ Unified interface verified")


def test_error_handling():
    """Test error handling for missing API keys."""
    print("\nTesting error handling...")
    
    # Clear all API keys
    for key in ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_AI_API_KEY', 
                'XAI_API_KEY', 'PERPLEXITY_API_KEY']:
        os.environ.pop(key, None)
    
    try:
        client = get_chatbot_client("openai")
        print("❌ Should have raised RuntimeError for missing API key")
        assert False
    except RuntimeError as e:
        assert "OPENAI_API_KEY" in str(e)
        print("✅ Error handling working correctly")


def test_invalid_provider():
    """Test error handling for invalid provider."""
    print("\nTesting invalid provider handling...")
    
    os.environ['OPENAI_API_KEY'] = 'sk-test-12345'
    
    try:
        client = get_chatbot_client("invalid_provider")
        print("❌ Should have raised ValueError for invalid provider")
        assert False
    except ValueError as e:
        assert "Unknown provider" in str(e)
        print("✅ Invalid provider error handling working")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Multi-Provider Chatbot Factory Test Suite")
    print("=" * 60)
    
    try:
        test_provider_constants()
        test_get_available_providers()
        test_client_creation()
        test_unified_interface()
        test_error_handling()
        test_invalid_provider()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return 0
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Test failed: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
