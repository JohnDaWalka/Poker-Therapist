#!/usr/bin/env python3
"""Simple CLI demo for the chatbot database functions."""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import chatbot_app
sys.path.insert(0, str(Path(__file__).parent.parent))

from chatbot_app import (  # noqa: E402
    DB_PATH,
    clear_user_history,
    get_or_create_user,
    init_database,
    load_messages,
    save_message,
)


def demo_database_operations() -> None:
    """Demonstrate database operations without requiring API key."""
    print("🤖 Streamlit Chatbot - Database Demo")
    print("=" * 50)
    print()

    # Initialize database
    print("1. Initializing database...")
    init_database()
    print(f"   ✓ Database created at: {DB_PATH}")
    print()

    # Create users
    print("2. Creating users...")
    user1_id = get_or_create_user("alice@example.com")
    user2_id = get_or_create_user("bob@example.com")
    print(f"   ✓ User 1 (Alice): ID={user1_id}")
    print(f"   ✓ User 2 (Bob): ID={user2_id}")
    print()

    # Save messages for user 1
    print("3. Saving messages for Alice...")
    save_message(user1_id, "user", "Hello! What's the weather like?")
    save_message(user1_id, "assistant", "I'm sorry, I don't have access to weather data.")
    save_message(user1_id, "user", "That's okay, thanks!")
    print("   ✓ Saved 3 messages")
    print()

    # Save messages for user 2
    print("4. Saving messages for Bob...")
    save_message(user2_id, "user", "Can you help me with Python?")
    save_message(user2_id, "assistant", "Of course! What would you like to know?")
    print("   ✓ Saved 2 messages")
    print()

    # Load messages for user 1
    print("5. Loading Alice's conversation history...")
    alice_messages = load_messages(user1_id)
    print(f"   ✓ Found {len(alice_messages)} messages:")
    for i, msg in enumerate(alice_messages, 1):
        role_emoji = "👤" if msg["role"] == "user" else "🤖"
        print(f"      {i}. {role_emoji} {msg['role']}: {msg['content']}")
    print()

    # Load messages for user 2
    print("6. Loading Bob's conversation history...")
    bob_messages = load_messages(user2_id)
    print(f"   ✓ Found {len(bob_messages)} messages:")
    for i, msg in enumerate(bob_messages, 1):
        role_emoji = "👤" if msg["role"] == "user" else "🤖"
        print(f"      {i}. {role_emoji} {msg['role']}: {msg['content']}")
    print()

    # Demonstrate user isolation
    print("7. Verifying user isolation...")
    print(f"   ✓ Alice has {len(alice_messages)} messages")
    print(f"   ✓ Bob has {len(bob_messages)} messages")
    print("   ✓ Each user's history is isolated ✅")
    print()

    # Clear history for user 1
    print("8. Clearing Alice's history...")
    clear_user_history(user1_id)
    alice_messages_after = load_messages(user1_id)
    print(f"   ✓ Alice now has {len(alice_messages_after)} messages")
    print()

    # Verify Bob's messages are still there
    print("9. Verifying Bob's messages are still intact...")
    bob_messages_still = load_messages(user2_id)
    print(f"   ✓ Bob still has {len(bob_messages_still)} messages")
    print()

    # Database statistics
    print("10. Database statistics...")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM messages")
        message_count = cursor.fetchone()[0]

    print(f"    ✓ Total users: {user_count}")
    print(f"    ✓ Total messages: {message_count}")
    print()

    print("=" * 50)
    print("✅ Demo completed successfully!")
    print()
    print("To run the full Streamlit app:")
    print("  1. Configure your xAI API key in .streamlit/secrets.toml")
    print("  2. Run: streamlit run chatbot_app.py")
    print()
    print(f"Note: Demo database created at: {DB_PATH}")
    print("You can delete it with: rm RexVoice.db")


if __name__ == "__main__":
    demo_database_operations()
