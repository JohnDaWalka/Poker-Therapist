"""Reusable chat UI components for Streamlit chatbot."""

from typing import Any, Optional

import streamlit as st


def render_message_with_avatar(role: str, content: str) -> None:
    """
    Render a chat message with appropriate avatar.

    Args:
        role: Message role (user or assistant)
        content: Message content

    """
    avatar = "👤" if role == "user" else "🎰"  # Poker chip for Rex
    with st.chat_message(role, avatar=avatar):
        st.markdown(content)


def render_thinking_process(thinking_text: str) -> None:
    """
    Render AI thinking process in an expander.

    Args:
        thinking_text: Thinking process text to display

    """
    if thinking_text and thinking_text.strip():
        with st.expander("💭 Rex's Analysis", expanded=False):
            st.markdown(thinking_text)


def render_chat_header() -> None:
    """Render the chat header with Rex branding."""
    st.title("🎰 Rex - Elite Poker Coach")
    st.markdown(
        """
        **Your AI poker therapist, coach, and strategist**  
        Combining CFR analysis, psychological coaching, and decades of experience.
        """,
    )


def render_welcome_message() -> None:
    """Render welcome message for new users."""
    st.info(
        """
        ### Welcome to Rex - Your Elite Poker Coach! 🎰

        I'm here to help you with:
        - 🧠 **CFR Analysis**: Advanced mathematical strategy optimization
        - 💪 **Poker Coaching**: Strategic gameplay improvements
        - 🧘 **Mental Wellness**: Psychological coaching for tilt management
        - 🎙️ **Voice Mode**: Talk to me naturally with voice input/output

        **Features:**
        - 💬 **Persistent Memory**: Your conversations are saved
        - 🔄 **Streaming Responses**: Real-time feedback
        - 💭 **Thinking Display**: See my analysis process
        - 🎤 **Voice Integration**: Enable voice mode in the sidebar

        To get started, enter your email in the sidebar!
        """,
    )


def render_user_info(email: str, message_count: int) -> None:
    """
    Render user info in sidebar.

    Args:
        email: User email
        message_count: Number of messages in conversation

    """
    st.sidebar.success(f"✅ Logged in as: {email}")
    st.sidebar.metric("Conversation Messages", message_count)


def render_model_info(model: str, streaming: bool, thinking: bool) -> None:
    """
    Render model configuration info.

    Args:
        model: Model name
        streaming: Whether streaming is enabled
        thinking: Whether thinking display is enabled

    """
    st.sidebar.divider()
    st.sidebar.subheader("Model Configuration")
    st.sidebar.info(f"🤖 Model: {model}")
    st.sidebar.info(f"🔄 Streaming: {'Enabled' if streaming else 'Disabled'}")
    st.sidebar.info(f"💭 Thinking: {'Enabled' if thinking else 'Disabled'}")


def render_quick_actions() -> Optional[str]:
    """
    Render quick action buttons for common queries.

    Returns:
        Selected action text, or None

    """
    st.sidebar.divider()
    st.sidebar.subheader("Quick Actions")

    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("🎯 Strategy Tips", use_container_width=True):
            return "Give me 3 advanced poker strategy tips for tournament play"

        if st.button("🧘 Tilt Help", use_container_width=True):
            return "I'm feeling tilted after a bad beat. Help me reset my mindset"

    with col2:
        if st.button("📊 Hand Analysis", use_container_width=True):
            return "I want to analyze a poker hand I played recently"

        if st.button("💪 Mental Game", use_container_width=True):
            return "How can I improve my mental game and focus at the table?"

    return None


def render_footer() -> None:
    """Render application footer."""
    st.divider()
    st.caption(
        "🎰 Rex Poker Coach | Powered by xAI Grok | "
        "💬 Persistent conversations with SQLite",
    )
