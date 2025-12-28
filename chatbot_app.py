"""Streamlit chatbot application with persistent memory using SQLite and xAI API."""

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
from openai import OpenAI

# Database configuration
DB_PATH = Path("chatbot_history.db")


def init_database() -> None:
    """Initialize SQLite database for message history."""
    conn = sqlite3.connect(DB_PATH)
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
    conn.close()


def get_or_create_user(email: str) -> int:
    """Get user ID by email or create new user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Try to get existing user
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()

    if result:
        user_id = result[0]
    else:
        # Create new user
        cursor.execute("INSERT INTO users (email) VALUES (?)", (email,))
        conn.commit()
        user_id = cursor.lastrowid

    conn.close()
    return user_id


def save_message(user_id: int, role: str, content: str) -> None:
    """Save message to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
        (user_id, role, content),
    )

    conn.commit()
    conn.close()


def load_messages(user_id: int, limit: int = 50) -> list[dict[str, Any]]:
    """Load message history for user."""
    conn = sqlite3.connect(DB_PATH)
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

    conn.close()
    return list(reversed(messages))  # Return in chronological order


def clear_user_history(user_id: int) -> None:
    """Clear all messages for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()


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
        st.error("xAI API key not found. Please configure XAI_API_KEY in secrets.toml or environment.")
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
                with self.container:
                    with st.expander("💭 AI Thinking Process", expanded=False):
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


def main() -> None:
    """Main Streamlit application."""
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

        # User email input
        email = st.text_input(
            "Your Email",
            value=st.session_state.get("user_email", ""),
            placeholder="user@example.com",
            help="Enter your email to access your conversation history",
        )

        if email and email != st.session_state.get("user_email", ""):
            st.session_state.user_email = email
            st.session_state.user_id = get_or_create_user(email)
            st.success(f"✅ Logged in as: {email}")
            st.rerun()

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

    # Main chat interface
    st.title("🤖 AI Chatbot with Persistent Memory")

    # Check if user is logged in
    if "user_email" not in st.session_state or not st.session_state.user_email:
        st.warning("👈 Please enter your email in the sidebar to start chatting")
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

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
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

            except Exception as e:
                error_msg = f"❌ Error: {e!s}"
                message_placeholder.error(error_msg)
                st.error("Please check your API key configuration in secrets.toml or environment variables.")


if __name__ == "__main__":
    main()
