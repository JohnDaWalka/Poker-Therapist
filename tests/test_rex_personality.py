"""Tests for multi-language Rex personality system."""

import pytest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from python_src.services.rex_personality import (
    RexPersonality,
    Language,
    get_personality,
)


def test_rex_personality_english_default() -> None:
    """Test default English personality."""
    personality = RexPersonality()
    
    assert personality.language == Language.ENGLISH
    prompt = personality.get_system_prompt()
    assert "Rex" in prompt
    assert "poker" in prompt.lower()
    assert "CFR" in prompt


def test_rex_personality_spanish() -> None:
    """Test Spanish personality."""
    personality = RexPersonality(Language.SPANISH)
    
    assert personality.language == Language.SPANISH
    prompt = personality.get_system_prompt()
    assert "Rex" in prompt
    assert "póker" in prompt.lower() or "poker" in prompt.lower()


def test_rex_personality_french() -> None:
    """Test French personality."""
    personality = RexPersonality(Language.FRENCH)
    
    prompt = personality.get_system_prompt()
    assert "Rex" in prompt
    assert "poker" in prompt.lower()


def test_rex_personality_japanese() -> None:
    """Test Japanese personality."""
    personality = RexPersonality(Language.JAPANESE)
    
    prompt = personality.get_system_prompt()
    assert "Rex" in prompt


def test_get_voice_preference() -> None:
    """Test voice preference selection."""
    english_personality = RexPersonality(Language.ENGLISH)
    japanese_personality = RexPersonality(Language.JAPANESE)
    
    assert english_personality.get_voice_preference() == "onyx"
    assert japanese_personality.get_voice_preference() == "alloy"


def test_get_greeting_multiple_languages() -> None:
    """Test greetings in different languages."""
    languages_to_test = [
        (Language.ENGLISH, "Rex"),
        (Language.SPANISH, "Rex"),
        (Language.FRENCH, "Rex"),
        (Language.GERMAN, "Rex"),
        (Language.ITALIAN, "Rex"),
    ]
    
    for language, expected_name in languages_to_test:
        personality = RexPersonality(language)
        greeting = personality.get_greeting()
        assert expected_name in greeting
        assert len(greeting) > 0


def test_get_language_name() -> None:
    """Test getting human-readable language names."""
    test_cases = [
        (Language.ENGLISH, "English"),
        (Language.SPANISH, "Spanish"),
        (Language.FRENCH, "French"),
        (Language.GERMAN, "German"),
    ]
    
    for language, expected_name in test_cases:
        personality = RexPersonality(language)
        name = personality.get_language_name()
        assert expected_name in name


def test_from_code_valid() -> None:
    """Test creating personality from valid language code."""
    personality = RexPersonality.from_code("es")
    assert personality.language == Language.SPANISH
    
    personality = RexPersonality.from_code("fr")
    assert personality.language == Language.FRENCH


def test_from_code_invalid() -> None:
    """Test creating personality from invalid code defaults to English."""
    personality = RexPersonality.from_code("invalid")
    assert personality.language == Language.ENGLISH


def test_get_available_languages() -> None:
    """Test getting list of available languages."""
    languages = RexPersonality.get_available_languages()
    
    assert len(languages) > 0
    assert all(isinstance(lang, tuple) for lang in languages)
    assert all(len(lang) == 2 for lang in languages)
    
    # Check English is included
    language_codes = [lang[0] for lang in languages]
    assert Language.ENGLISH in language_codes


def test_personality_traits_exist() -> None:
    """Test that personality traits are defined."""
    traits = RexPersonality.TRAITS
    
    assert "authoritative" in traits
    assert "analytical" in traits
    assert "empathetic" in traits
    assert "witty" in traits
    assert "supportive" in traits


def test_all_languages_have_prompts() -> None:
    """Test that all defined languages have system prompts."""
    for language in Language:
        personality = RexPersonality(language)
        prompt = personality.get_system_prompt()
        # Should either have specific prompt or fallback to English
        assert len(prompt) > 0
        assert "Rex" in prompt or "rex" in prompt.lower()


def test_all_languages_have_voice_preferences() -> None:
    """Test that all languages have voice preferences."""
    for language in Language:
        personality = RexPersonality(language)
        voice = personality.get_voice_preference()
        # Should return a valid voice name
        assert voice in ["onyx", "alloy", "echo", "fable", "nova", "shimmer"]


def test_get_personality_factory() -> None:
    """Test personality factory function."""
    personality = get_personality("en")
    assert isinstance(personality, RexPersonality)
    assert personality.language == Language.ENGLISH
    
    personality = get_personality("es")
    assert personality.language == Language.SPANISH


def test_chinese_personality() -> None:
    """Test Chinese personality."""
    personality = RexPersonality(Language.CHINESE)
    
    prompt = personality.get_system_prompt()
    assert "Rex" in prompt
    greeting = personality.get_greeting()
    assert "Rex" in greeting


def test_system_prompt_contains_key_elements() -> None:
    """Test that system prompts contain key Rex elements."""
    # Test a few key languages
    languages_to_test = [
        Language.ENGLISH,
        Language.SPANISH,
        Language.GERMAN,
    ]
    
    for language in languages_to_test:
        personality = RexPersonality(language)
        prompt = personality.get_system_prompt()
        
        # Check for CFR mention (in some form)
        assert "CFR" in prompt or "Regret" in prompt or "regret" in prompt.lower()
        
        # Check for coaching/experience mention
        assert len(prompt) > 100  # Should be substantial


def test_personality_immutability() -> None:
    """Test that personality attributes are set correctly."""
    personality = RexPersonality(Language.FRENCH)
    
    # Language should be set and immutable through normal means
    assert personality.language == Language.FRENCH
    
    # Getting properties should not change state
    _ = personality.get_system_prompt()
    _ = personality.get_voice_preference()
    _ = personality.get_greeting()
    
    assert personality.language == Language.FRENCH
