#!/usr/bin/env python3
"""Manual test script for voice service functionality."""

import os
import sys
from pathlib import Path

# Add python_src to path
sys.path.insert(0, str(Path(__file__).parent))

from python_src.services.voice_service import VoiceService, REX_SYSTEM_PROMPT


def test_voice_service_init() -> None:
    """Test voice service initialization."""
    print("Testing Voice Service Initialization...")
    
    try:
        service = VoiceService()
        print(f"✅ Voice service initialized successfully")
        print(f"   Provider: {service.get_voice_provider()}")
        print(f"   Available: {service.is_available()}")
    except RuntimeError as e:
        print(f"❌ Failed to initialize: {e}")
        print("   Please set XAI_API_KEY or OPENAI_API_KEY environment variable")
        return


def test_rex_prompt() -> None:
    """Test Rex personality prompt."""
    print("\nTesting Rex Personality Prompt...")
    print(f"✅ Rex system prompt loaded ({len(REX_SYSTEM_PROMPT)} characters)")
    print(f"   Preview: {REX_SYSTEM_PROMPT[:100]}...")


def test_tts_mock() -> None:
    """Test TTS with mock data (requires API key)."""
    print("\nTesting Text-to-Speech...")
    
    if not os.getenv("XAI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Skipped: No API key configured")
        return
    
    try:
        service = VoiceService()
        print("   Attempting TTS conversion...")
        audio = service.text_to_speech("Hello, I'm Rex, your poker coach!")
        print(f"✅ TTS successful: Generated {len(audio)} bytes of audio")
    except Exception as e:
        print(f"⚠️  TTS test failed: {e}")
        print("   This is expected if x.ai doesn't support TTS yet")


def test_authorized_emails() -> None:
    """Test authorized emails configuration."""
    print("\nTesting Authorized Emails Configuration...")
    
    # Import after adding to path
    import chatbot_app
    
    emails = chatbot_app.AUTHORIZED_EMAILS
    print(f"✅ Found {len(emails)} authorized emails:")
    for email in emails:
        print(f"   - {email}")


def main() -> None:
    """Run all manual tests."""
    print("=" * 60)
    print("VOICE INTEGRATION MANUAL TEST SUITE")
    print("=" * 60)
    
    test_voice_service_init()
    test_rex_prompt()
    test_tts_mock()
    test_authorized_emails()
    
    print("\n" + "=" * 60)
    print("MANUAL TEST COMPLETE")
    print("=" * 60)
    print("\n💡 To test the full application:")
    print("   1. Set XAI_API_KEY and/or OPENAI_API_KEY")
    print("   2. Run: streamlit run chatbot_app.py")
    print("   3. Select an authorized email")
    print("   4. Enable voice mode in sidebar")
    print("   5. Upload an audio file or type a message")
    print()


if __name__ == "__main__":
    main()
