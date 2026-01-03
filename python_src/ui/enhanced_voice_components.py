"""Enhanced voice UI components with streaming, emotion display, and conversation mode."""

from typing import Any, Optional

import streamlit as st


def render_streaming_controls(is_streaming: bool = False) -> dict[str, bool]:
    """
    Render real-time streaming controls.
    
    Args:
        is_streaming: Current streaming state
        
    Returns:
        Dictionary with control states
    """
    st.sidebar.divider()
    st.sidebar.subheader("🔴 Live Streaming")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        start_stream = st.button(
            "▶️ Start" if not is_streaming else "⏸️ Pause",
            use_container_width=True,
            disabled=is_streaming,
        )
    
    with col2:
        stop_stream = st.button(
            "⏹️ Stop",
            use_container_width=True,
            disabled=not is_streaming,
        )
    
    # Show streaming status
    if is_streaming:
        st.sidebar.success("🔴 Live streaming active")
    else:
        st.sidebar.info("⚪ Streaming inactive")
    
    return {
        "start": start_stream,
        "stop": stop_stream,
        "is_active": is_streaming,
    }


def render_conversation_mode_controls() -> dict[str, Any]:
    """
    Render conversation mode controls.
    
    Returns:
        Dictionary with mode settings
    """
    st.sidebar.divider()
    st.sidebar.subheader("💬 Conversation Mode")
    
    mode = st.sidebar.radio(
        "Mode",
        options=["Single Turn", "Continuous Chat", "Voice Activated"],
        index=0,
        help="Choose how Rex responds to your input",
    )
    
    # Mode-specific settings
    if mode == "Continuous Chat":
        auto_continue = st.sidebar.checkbox(
            "Auto-continue conversation",
            value=True,
            help="Rex will keep conversation going",
        )
        
        turn_timeout = st.sidebar.slider(
            "Turn timeout (seconds)",
            min_value=3,
            max_value=30,
            value=10,
            help="Silence duration before Rex responds",
        )
    else:
        auto_continue = False
        turn_timeout = 10
    
    if mode == "Voice Activated":
        vad_sensitivity = st.sidebar.slider(
            "Voice detection sensitivity",
            min_value=0,
            max_value=3,
            value=2,
            help="0=least sensitive, 3=most sensitive",
        )
    else:
        vad_sensitivity = 2
    
    return {
        "mode": mode.lower().replace(" ", "_"),
        "auto_continue": auto_continue,
        "turn_timeout": turn_timeout,
        "vad_sensitivity": vad_sensitivity,
    }


def render_emotion_display(emotion_data: dict[str, Any]) -> None:
    """
    Display detected emotion with visual indicators.
    
    Args:
        emotion_data: Dictionary with emotion type and confidence
    """
    if not emotion_data or emotion_data.get("emotion") == "neutral":
        return
    
    emotion = emotion_data.get("emotion", "neutral")
    confidence = emotion_data.get("confidence", 0.0)
    
    # Emoji mapping for emotions
    emotion_emojis = {
        "happy": "😊",
        "sad": "😢",
        "angry": "😠",
        "frustrated": "😤",
        "excited": "🤩",
        "confident": "😎",
        "anxious": "😰",
        "neutral": "😐",
    }
    
    # Color mapping
    emotion_colors = {
        "happy": "#4CAF50",
        "sad": "#2196F3",
        "angry": "#F44336",
        "frustrated": "#FF9800",
        "excited": "#FF5722",
        "confident": "#9C27B0",
        "anxious": "#FFC107",
        "neutral": "#9E9E9E",
    }
    
    emoji = emotion_emojis.get(emotion, "😐")
    color = emotion_colors.get(emotion, "#9E9E9E")
    
    # Display emotion indicator
    st.markdown(
        f"""
        <div style="padding: 10px; border-left: 4px solid {color}; 
             background-color: {color}15; border-radius: 5px; margin: 10px 0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 24px;">{emoji}</span>
                <div>
                    <strong style="color: {color};">Emotion: {emotion.title()}</strong>
                    <div style="font-size: 12px; color: #666;">
                        Confidence: {confidence:.0%}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_language_selector() -> str:
    """
    Render language selector for Rex personality.
    
    Returns:
        Selected language code
    """
    st.sidebar.divider()
    st.sidebar.subheader("🌍 Rex Language")
    
    languages = [
        ("en", "English"),
        ("es", "Spanish (Español)"),
        ("fr", "French (Français)"),
        ("de", "German (Deutsch)"),
        ("it", "Italian (Italiano)"),
        ("pt", "Portuguese (Português)"),
        ("ja", "Japanese (日本語)"),
        ("zh", "Chinese (中文)"),
    ]
    
    language = st.sidebar.selectbox(
        "Select Rex's Language",
        options=[code for code, _ in languages],
        format_func=lambda code: next(name for c, name in languages if c == code),
        index=0,
        help="Choose the language for Rex's personality and responses",
    )
    
    return language


def render_voice_cloning_uploader() -> Optional[list[bytes]]:
    """
    Render voice sample uploader for voice cloning.
    
    Returns:
        List of uploaded audio samples or None
    """
    st.sidebar.divider()
    st.sidebar.subheader("🎙️ Custom Rex Voice")
    
    st.sidebar.info(
        "Upload 3-5 audio samples (10-15 seconds each) "
        "of clear speech to create a custom Rex voice."
    )
    
    uploaded_samples = st.sidebar.file_uploader(
        "Voice Samples",
        type=["wav", "mp3", "m4a"],
        accept_multiple_files=True,
        help="Upload clear audio samples for voice cloning",
    )
    
    if uploaded_samples:
        st.sidebar.success(f"✅ {len(uploaded_samples)} samples uploaded")
        
        # Show validation info
        if len(uploaded_samples) < 3:
            st.sidebar.warning("⚠️ Upload at least 3 samples for best results")
        
        return [sample.read() for sample in uploaded_samples]
    
    return None


def render_voice_profile_manager(profiles: list[dict]) -> Optional[str]:
    """
    Render voice profile manager.
    
    Args:
        profiles: List of available voice profiles
        
    Returns:
        Selected profile ID or None
    """
    if not profiles:
        st.sidebar.info("No custom voice profiles yet. Upload samples to create one!")
        return None
    
    st.sidebar.divider()
    st.sidebar.subheader("🎭 Voice Profiles")
    
    profile_options = {
        "default": "Default Rex Voice",
        **{p["profile_id"]: p["name"] for p in profiles},
    }
    
    selected = st.sidebar.selectbox(
        "Active Voice Profile",
        options=list(profile_options.keys()),
        format_func=lambda x: profile_options[x],
        help="Choose which voice profile Rex should use",
    )
    
    if selected != "default":
        # Show profile details
        profile = next(p for p in profiles if p["profile_id"] == selected)
        st.sidebar.caption(f"📊 Samples: {profile['sample_count']}")
        if profile.get("description"):
            st.sidebar.caption(f"ℹ️ {profile['description']}")
    
    return selected if selected != "default" else None


def render_streaming_transcription(text: str, is_final: bool = False) -> None:
    """
    Render real-time streaming transcription.
    
    Args:
        text: Transcribed text
        is_final: Whether this is final transcription
    """
    if not text:
        return
    
    style = "background-color: #e3f2fd;" if is_final else "background-color: #fff3e0;"
    prefix = "✅" if is_final else "⏳"
    
    st.markdown(
        f"""
        <div style="padding: 10px; {style} border-radius: 5px; margin: 5px 0;">
            {prefix} <strong>{"Transcription:" if is_final else "Live:"}</strong> {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_conversation_status(
    is_active: bool,
    turn_count: int,
    duration: Optional[int] = None,
) -> None:
    """
    Render conversation session status.
    
    Args:
        is_active: Whether conversation is active
        turn_count: Number of conversation turns
        duration: Optional session duration in seconds
    """
    st.sidebar.divider()
    st.sidebar.subheader("📊 Session Status")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        st.metric("Status", "🟢 Active" if is_active else "⚪ Inactive")
    
    with col2:
        st.metric("Turns", turn_count)
    
    if duration is not None:
        minutes = duration // 60
        seconds = duration % 60
        st.sidebar.caption(f"⏱️ Duration: {minutes}m {seconds}s")


def render_voice_activity_indicator(is_speaking: bool = False) -> None:
    """
    Enhanced voice activity indicator with animation.
    
    Args:
        is_speaking: Whether voice is detected
    """
    if is_speaking:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; padding: 10px;">
                <div class="voice-pulse"></div>
                <span style="color: #ff4444; font-weight: bold;">🎤 Speaking...</span>
            </div>
            <style>
                @keyframes voice-pulse {
                    0%, 100% { 
                        transform: scale(1);
                        opacity: 1;
                    }
                    50% { 
                        transform: scale(1.5);
                        opacity: 0.5;
                    }
                }
                .voice-pulse {
                    width: 15px;
                    height: 15px;
                    border-radius: 50%;
                    background-color: #ff4444;
                    animation: voice-pulse 1s infinite;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown("🎤 Ready to listen")


def show_feature_info(feature_name: str) -> None:
    """
    Display information about a new feature.
    
    Args:
        feature_name: Name of the feature
    """
    feature_info = {
        "streaming": {
            "icon": "🔴",
            "title": "Real-time Voice Streaming",
            "description": "Talk to Rex naturally with WebRTC streaming for instant responses.",
        },
        "voice_activation": {
            "icon": "🎤",
            "title": "Voice-Activated Recording",
            "description": "Automatic recording that starts when you speak and stops when you're done.",
        },
        "conversation_mode": {
            "icon": "💬",
            "title": "Continuous Conversation",
            "description": "Natural back-and-forth dialogue with Rex, like a real coaching session.",
        },
        "emotion_analysis": {
            "icon": "😊",
            "title": "Emotion Detection",
            "description": "Rex understands your emotional state and adapts his coaching style.",
        },
        "multi_language": {
            "icon": "🌍",
            "title": "Multi-Language Support",
            "description": "Rex speaks multiple languages with authentic poker terminology.",
        },
        "voice_cloning": {
            "icon": "🎭",
            "title": "Custom Voice Profiles",
            "description": "Create a personalized Rex voice that sounds the way you want.",
        },
    }
    
    info = feature_info.get(feature_name, {})
    if info:
        st.info(
            f"{info['icon']} **{info['title']}**\n\n{info['description']}"
        )
