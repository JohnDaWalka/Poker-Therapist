"""Voice chatbot UI components for Streamlit."""

import base64
from typing import Any, Optional

import streamlit as st


def render_voice_controls(voice_enabled: bool = False) -> bool:
    """
    Render voice control toggle in sidebar.

    Args:
        voice_enabled: Current voice enabled state

    Returns:
        Updated voice enabled state

    """
    st.sidebar.divider()
    st.sidebar.subheader("🎙️ Voice Mode")

    voice_enabled = st.sidebar.checkbox(
        "Enable Voice",
        value=voice_enabled,
        help="Turn on voice input and Rex voice output",
    )

    if voice_enabled:
        st.sidebar.info("🎤 Voice mode active - Rex will speak responses")
    else:
        st.sidebar.info("💬 Text-only mode")

    return voice_enabled


def render_audio_player(audio_data: bytes, autoplay: bool = True) -> None:
    """
    Render audio player for TTS output.

    Args:
        audio_data: Audio data as bytes
        autoplay: Whether to autoplay the audio

    """
    # Convert audio bytes to base64 for HTML embedding
    audio_b64 = base64.b64encode(audio_data).decode()
    audio_html = f"""
        <audio controls {"autoplay" if autoplay else ""}>
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)


def render_voice_recorder() -> Optional[bytes]:
    """
    Render voice recorder component.
    
    Note: This is currently a file upload implementation. 
    Real-time recording requires additional components:
    - streamlit-webrtc for WebRTC audio capture
    - audio_recorder_streamlit component
    - Custom JavaScript component
    
    Future enhancement will add browser-based recording.

    Returns:
        Recorded audio data as bytes, or None if no recording

    """
    st.info("🎤 **Voice Input**: Upload an audio file for transcription")
    
    # Note: Browser-based recording will be added in future version
    st.caption("💡 Real-time recording coming soon. Currently supports file uploads.")

    uploaded_audio = st.file_uploader(
        "Upload an audio file (WAV, MP3, M4A, OGG)",
        type=["wav", "mp3", "m4a", "ogg"],
        help="Upload a voice recording to transcribe",
    )

    if uploaded_audio is not None:
        return uploaded_audio.read()

    return None


def render_voice_activity_indicator(is_active: bool = False) -> None:
    """
    Render voice activity indicator.

    Args:
        is_active: Whether voice activity is detected

    """
    if is_active:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 10px; height: 10px; border-radius: 50%; 
                     background-color: #ff4444; animation: pulse 1s infinite;">
                </div>
                <span style="color: #ff4444;">🎤 Listening...</span>
            </div>
            <style>
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.3; }
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown("🎤 Voice input ready")


def render_transcription_display(transcription: str) -> None:
    """
    Render real-time transcription display.

    Args:
        transcription: Transcribed text to display

    """
    if transcription:
        with st.expander("📝 Transcription", expanded=True):
            st.markdown(f"**You said:** {transcription}")


def render_voice_settings() -> dict[str, Any]:
    """
    Render voice settings in sidebar.

    Returns:
        Dictionary of voice settings

    """
    st.sidebar.divider()
    st.sidebar.subheader("Voice Settings")

    voice_choice = st.sidebar.selectbox(
        "Rex Voice",
        options=["onyx", "alloy", "echo", "fable", "nova", "shimmer"],
        index=0,  # onyx is default (deep, authoritative)
        help="Choose Rex's voice personality",
    )

    autoplay = st.sidebar.checkbox(
        "Auto-play responses",
        value=True,
        help="Automatically play Rex's voice responses",
    )

    language = st.sidebar.selectbox(
        "Speech Language",
        options=["en", "es", "fr", "de", "it", "pt", "nl", "pl", "ru", "ja", "ko", "zh"],
        index=0,
        help="Language for speech recognition",
    )

    return {
        "voice": voice_choice,
        "autoplay": autoplay,
        "language": language,
    }


def show_voice_error(error_message: str) -> None:
    """
    Display voice-related error message.

    Args:
        error_message: Error message to display

    """
    st.error(f"🎤 Voice Error: {error_message}")
    st.info("💡 Falling back to text-only mode. Check your configuration.")


def show_voice_success(message: str) -> None:
    """
    Display voice success message.

    Args:
        message: Success message to display

    """
    st.success(f"✅ {message}")
