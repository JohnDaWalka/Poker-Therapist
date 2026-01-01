"""Streamlit chatbot application with persistent memory using SQLite and xAI API."""

import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

import streamlit as st
from openai import OpenAI

# Add python_src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import voice and UI components
try:
    from python_src.services.voice_service import VoiceService, REX_SYSTEM_PROMPT
    from python_src.ui.voice_chatbot import (
        render_audio_player,
        render_voice_controls,
        render_voice_recorder,
        render_voice_settings,
        show_voice_error,
    )
    from python_src.ui.chat_components import (
        render_chat_header,
        render_quick_actions,
        render_user_info,
    )

    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

# Database configuration
DB_PATH = Path("chatbot_history.db")

# Authorized email addresses for Rex Poker Coach
AUTHORIZED_EMAILS = [
    "m.fanelli1@icloud.com",
    "johndawalka@icloud.com",
    "mauro.fanelli@ctstate.edu",
    "maurofanellijr@gmail.com",
    "cooljack87@icloud.com",
    "jdwalka@pm.me",
]


def init_database() -> None:
    """Initialize SQLite database for message history."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        conn.commit()


def get_or_create_user(email: str) -> int:
    """Get user ID by email or create new user."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Try to get existing user
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()

        if result:
            return result[0]

        # Create new user
        cursor.execute("INSERT INTO users (email) VALUES (?)", (email,))
        conn.commit()
        return cursor.lastrowid


def save_message(user_id: int, role: str, content: str) -> None:
    """Save message to database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content),
        )

        conn.commit()


def load_messages(user_id: int, limit: int = 50) -> list[dict[str, Any]]:
    """Load message history for user."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT role, content, created_at
            FROM messages
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        )

        messages = [
            {"role": row[0], "content": row[1], "created_at": row[2]}
            for row in cursor.fetchall()
        ]

        return list(reversed(messages))  # Return in chronological order


def clear_user_history(user_id: int) -> None:
    """Clear all messages for a user."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))

        conn.commit()


def get_xai_client() -> OpenAI:
    """Get xAI API client using Streamlit secrets or environment variables."""
    # Try Streamlit secrets first
    api_key = None
    if hasattr(st, "secrets") and "XAI_API_KEY" in st.secrets:
        api_key = st.secrets["XAI_API_KEY"]
    else:
        # Fall back to environment variable
        api_key = os.getenv("XAI_API_KEY")

    if not api_key:
        st.error(
            "xAI API key not found. "
            "Please configure XAI_API_KEY in secrets.toml or environment.",
        )
        st.stop()

    return OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1",
    )


class ThinksCallback:
    """Callback handler for streaming responses with thinking display."""

    def __init__(self, container: Any) -> None:
        """Initialize callback with Streamlit container."""
        self.container = container
        self.thinking_text = ""
        self.response_text = ""
        self.in_thinking = False

    def process_chunk(self, chunk: str) -> None:
        """Process streaming chunk and update display."""
        if "<thinking>" in chunk:
            # Split on thinking tag
            parts = chunk.split("<thinking>", 1)
            # Add text before thinking to response
            if parts[0]:
                self.response_text += parts[0]
            self.in_thinking = True
            # Process remaining text after tag
            chunk = parts[1] if len(parts) > 1 else ""

        if "</thinking>" in chunk:
            # Split on closing tag
            parts = chunk.split("</thinking>", 1)
            # Add text before closing tag to thinking
            if parts[0]:
                self.thinking_text += parts[0]
            self.in_thinking = False
            # Show thinking in expander when complete
            if self.thinking_text:
                with self.container, st.expander("💭 AI Thinking Process", expanded=False):
                    st.markdown(self.thinking_text)
            # Add text after closing tag to response
            if len(parts) > 1:
                self.response_text += parts[1]
                self.container.markdown(self.response_text)
            return

        if self.in_thinking:
            self.thinking_text += chunk
        else:
            self.response_text += chunk
            # Update response in real-time
            self.container.markdown(self.response_text)


def main() -> None:  # noqa: C901, PLR0912, PLR0915
    """Run the main Streamlit chatbot application."""
    st.set_page_config(
        page_title="AI Chatbot",
        page_icon="🤖",
        layout="wide",
    )

    # Initialize database
    init_database()

    # Sidebar for user configuration
    with st.sidebar:
        st.title("⚙️ Configuration")

        # User email input with authorized accounts
        st.subheader("👤 Account Login")
        
        # Show dropdown for authorized emails or custom input
        email_option = st.radio(
            "Select or enter your email:",
            options=["Select from authorized", "Enter custom email"],
            help="Choose an authorized account or enter your own email",
        )
        
        if email_option == "Select from authorized":
            email = st.selectbox(
                "Authorized Accounts",
                options=[""] + AUTHORIZED_EMAILS,
                format_func=lambda x: "Select an account..." if x == "" else x,
                help="Select your authorized email address",
            )
        else:
            email = st.text_input(
                "Your Email",
                value=st.session_state.get("user_email", ""),
                placeholder="user@example.com",
                help="Enter your email to access your conversation history",
            )

        if email and email != st.session_state.get("user_email", ""):
            # Validate email format
            if "@" in email and "." in email.split("@")[1]:
                st.session_state.user_email = email
                st.session_state.user_id = get_or_create_user(email)
                
                # Show special badge for authorized users
                if email in AUTHORIZED_EMAILS:
                    st.success(f"✅ Logged in as: {email} 🎰 (Authorized User)")
                else:
                    st.success(f"✅ Logged in as: {email}")
                st.rerun()
            else:
                st.error("❌ Please enter a valid email address")

        # Show user info if logged in
        if "user_id" in st.session_state and "user_email" in st.session_state:
            if st.session_state.user_email in AUTHORIZED_EMAILS:
                st.info("🎰 **VIP Access**: Full voice and Rex personality features enabled")
            
            # Show message count
            message_count = len(st.session_state.get("messages", []))
            st.metric("Messages in Session", message_count)

        # Show clear history button if user is logged in
        if "user_id" in st.session_state:
            st.divider()
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                clear_user_history(st.session_state.user_id)
                st.session_state.messages = []
                st.success("Chat history cleared!")
                st.rerun()

        # Model configuration
        st.divider()
        st.subheader("Model Settings")

        # Get streaming and thinking settings from secrets or defaults
        enable_streaming = True
        enable_thinking = True

        if hasattr(st, "secrets"):
            enable_streaming = st.secrets.get("ENABLE_STREAMING", True)
            enable_thinking = st.secrets.get("ENABLE_THINKING", True)

        st.info(f"🔄 Streaming: {'Enabled' if enable_streaming else 'Disabled'}")
        st.info(f"💭 Thinking Display: {'Enabled' if enable_thinking else 'Disabled'}")

        # Voice mode controls
        voice_enabled = False
        voice_settings = {"voice": "onyx", "autoplay": True, "language": "en"}
        if VOICE_AVAILABLE:
            voice_enabled = render_voice_controls(
                st.session_state.get("voice_enabled", False),
            )
            st.session_state.voice_enabled = voice_enabled

            if voice_enabled:
                voice_settings = render_voice_settings()

        # Quick action buttons
        if VOICE_AVAILABLE:
            quick_action = render_quick_actions()
            if quick_action:
                st.session_state.quick_action = quick_action

    # Main chat interface
    if VOICE_AVAILABLE:
        render_chat_header()
    else:
        st.title("🤖 AI Chatbot with Persistent Memory")

    # Check if user is logged in
    if "user_email" not in st.session_state or not st.session_state.user_email:
        st.warning("👈 Please enter your email in the sidebar to start chatting")
        if VOICE_AVAILABLE:
            from python_src.ui.chat_components import render_welcome_message

            render_welcome_message()
        else:
            st.info("""
            ### Welcome to the AI Chatbot!

            This chatbot features:
            - 🧠 **Persistent Memory**: Your conversations are saved and can be resumed later
            - 👥 **Multi-User Support**: Each user has their own conversation history
            - 🔄 **Streaming Responses**: See responses in real-time
            - 💭 **Thinking Display**: Understand the AI's reasoning process
            - 🔐 **Secure**: API keys stored in secrets or environment variables

            To get started, enter your email in the sidebar!
            """)
        return

    # Initialize session state for messages
    if "messages" not in st.session_state:
        # Load message history from database
        st.session_state.messages = []
        if "user_id" in st.session_state:
            db_messages = load_messages(st.session_state.user_id)
            for msg in db_messages:
                st.session_state.messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle quick actions if set
    if VOICE_AVAILABLE and st.session_state.get("quick_action"):
        prompt = st.session_state.quick_action
        st.session_state.quick_action = None
        st.rerun()

    # Voice input option
    prompt = None
    if VOICE_AVAILABLE and voice_enabled:
        with st.expander("🎤 Voice Input", expanded=False):
            audio_data = render_voice_recorder()
            if audio_data:
                try:
                    voice_service = VoiceService()
                    prompt = voice_service.speech_to_text(
                        audio_data,
                        language=voice_settings.get("language", "en"),
                    )
                    st.success(f"✅ Transcribed: {prompt}")
                except Exception as e:
                    show_voice_error(f"Speech recognition failed: {e!s}")

    # Chat input (text)
    if not prompt:
        prompt = st.chat_input("Type your message here... or use voice input above 🎤" if voice_enabled else "Type your message here...")

    if prompt:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Save user message to database
        save_message(st.session_state.user_id, "user", prompt)

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            try:
                client = get_xai_client()

                # Prepare conversation history
                conversation = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
                
                # Add Rex personality system prompt for authorized users
                if VOICE_AVAILABLE and st.session_state.get("user_email") in AUTHORIZED_EMAILS:
                    conversation.insert(0, {"role": "system", "content": REX_SYSTEM_PROMPT})

                # Get streaming and thinking settings
                enable_streaming = True
                enable_thinking = True

                if hasattr(st, "secrets"):
                    enable_streaming = st.secrets.get("ENABLE_STREAMING", True)
                    enable_thinking = st.secrets.get("ENABLE_THINKING", True)

                # Stream response
                if enable_streaming:
                    callback = ThinksCallback(message_placeholder)
                    full_response = ""

                    stream = client.chat.completions.create(
                        model="grok-beta",
                        messages=conversation,
                        stream=True,
                    )

                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            chunk_text = chunk.choices[0].delta.content
                            full_response += chunk_text

                            if enable_thinking:
                                callback.process_chunk(chunk_text)
                            else:
                                message_placeholder.markdown(full_response)

                    # Final response without thinking tags
                    if enable_thinking and callback.response_text:
                        response = callback.response_text
                    else:
                        # Remove thinking tags if present
                        response = full_response
                        if "<thinking>" in response and "</thinking>" in response:
                            start = response.index("<thinking>")
                            end = response.index("</thinking>") + len("</thinking>")
                            response = response[:start] + response[end:]

                    message_placeholder.markdown(response)

                else:
                    # Non-streaming response
                    response_obj = client.chat.completions.create(
                        model="grok-beta",
                        messages=conversation,
                        stream=False,
                    )
                    response = response_obj.choices[0].message.content
                    message_placeholder.markdown(response)

                # Add assistant response to messages
                st.session_state.messages.append({"role": "assistant", "content": response})

                # Save assistant message to database
                save_message(st.session_state.user_id, "assistant", response)

                # Generate voice output if enabled
                if VOICE_AVAILABLE and voice_enabled:
                    try:
                        with st.spinner("🎤 Rex is speaking..."):
                            voice_service = VoiceService()
                            audio_data = voice_service.text_to_speech(
                                response,
                                voice=voice_settings.get("voice", "onyx"),
                            )
                            st.markdown("---")
                            st.markdown("🔊 **Rex's Voice Response:**")
                            render_audio_player(
                                audio_data,
                                autoplay=voice_settings.get("autoplay", True),
                            )
                    except Exception as voice_error:
                        show_voice_error(f"Voice generation failed: {voice_error!s}")
                        st.info("💡 Rex's text response is still available above.")

            except Exception as e:  # noqa: BLE001
                error_msg = f"❌ Error: {e!s}"
                message_placeholder.error(error_msg)
                st.error(
                    "Please check your API key configuration "
                    "in secrets.toml or environment variables.",
                )


if __name__ == "__main__":
    main()
