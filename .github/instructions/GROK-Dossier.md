import streamlit as st
import sqlite3
import requests
from datetime import datetime
import os

# --- Configuration ---
DB_FILE = "grok_memory.db"

# Securely load xAI API key from Streamlit secrets or env var
try:
    XAI_API_KEY = st.secrets["XAI_API_KEY"]
except FileNotFoundError:
    XAI_API_KEY = os.getenv("XAI_API_KEY")

if not XAI_API_KEY:
    st.error("🚨 XAI_API_KEY not found! Add it to `.streamlit/secrets.toml` or set as environment variable.")
    st.stop()

# User identification - flexible for future multi-user
if "user_email" not in st.session_state:
    st.session_state.user_email = "johndawalka@iCloud.com"  # Default

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_email TEXT,
                  role TEXT,
                  content TEXT,
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()

def save_message(user_email, role, content):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (user_email, role, content, timestamp) VALUES (?, ?, ?, ?)",
              (user_email, role, content, datetime.now()))
    conn.commit()
    conn.close()

def load_memory(user_email, max_messages=30):
    """Load the MOST RECENT messages (newest first in DB, reverse to chronological for API)"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT role, content FROM chat_history 
        WHERE user_email=? 
        ORDER BY id DESC 
        LIMIT ?
    """, (user_email, max_messages))
    rows = c.fetchall()
    conn.close()
    # Reverse to oldest → newest for Grok context
    messages = [{"role": row[0], "content": row[1]} for row in reversed(rows)]
    return messages

def clear_all_memory(user_email):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM chat_history WHERE user_email=?", (user_email,))
    conn.commit()
    conn.close()

# --- Grok API Call ---
def query_grok(messages, model="grok-beta"):
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {XAI_API_KEY}"
    }
    payload = {
        "messages": messages,
        "model": model,
        "stream": False,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        if not data.get("choices"):
            return "⚠️ Empty response from Grok."
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "⏰ Request timed out — Grok takin' too long. Try again."
    except requests.exceptions.ConnectionError:
        return "🌐 Connection failed. Check your network or xAI status."
    except requests.exceptions.HTTPError as e:
        return f"🚫 API Error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return f"💥 Unexpected error: {str(e)}"

# --- Streamlit UI ---
def main():
    st.set_page_config(page_title="Grok Persistent Memory 🧠", page_icon="🧠")
    init_db()

    # Sidebar
    with st.sidebar:
        st.title("🔐 User & Settings")
        user_email = st.text_input("Your Email", value=st.session_state.user_email)
        if user_email != st.session_state.user_email:
            st.session_state.user_email = user_email
            st.rerun()

        st.code(user_email)

        st.divider()
        st.caption("Model")
        model = st.selectbox("Grok Model", ["grok-beta", "grok-2-latest", "grok-2"], index=0)

        st.divider()
        if st.button("🗑️ Clear ALL Memory (Permanent)"):
            clear_all_memory(st.session_state.user_email)
            st.success("Memory wiped clean, fam.")
            st.rerun()

        if st.button("🆕 Start Fresh Conversation (Keep History)"):
            st.session_state.new_convo = True
            st.rerun()

    st.title("Grok Persistent Chat 🧠🚀")
    st.caption("I remember everything we talk about — across sessions. Real persistence.")

    # Load history or start fresh
    if st.session_state.get("new_convo"):
        history = []
        st.info("🆕 New conversation started. Old history saved but hidden.")
        if st.button("🔙 Back to Full History"):
            st.session_state.new_convo = False
            st.rerun()
    else:
        history = load_memory(st.session_state.user_email)
        st.session_state.new_convo = False

    # Display history
    for msg in history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    if prompt := st.chat_input("What's good?"):
        # Show user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Save user message
        save_message(st.session_state.user_email, "user", prompt)

        # Reload full context
        updated_history = [] if st.session_state.get("new_convo") else load_memory(st.session_state.user_email)

        # Get Grok response
        with st.chat_message("assistant"):
            with st.spinner("Grok thinkin' hard..."):
                response = query_grok(updated_history, model=model)
                st.markdown(response)

        # Save assistant response
        save_message(st.session_state.user_email, "assistant", response)

if __name__ == "__main__":
    main()
Aight, fam — code complete and upgraded heavy. 🔥
Dis joint now secure wit secrets, smarter memory (only last 30 msgs so tokens stay chill), fresh convo option without losin’ history, model picker, better errors, and lil’ ebonics flavor when it hit you wit feedback. Deploy dis on Streamlit Cloud, drop yo key in secrets.toml, and you got a personal Grok dat actually remembers errythang — better than the official one.
Hit me if you want mo’ tweaks, like token counter, export chat, or voice mode hooks. We buildin’. 🚀
— John Da Walka | Full-Stack Force of Nature jdwalka@pm.me | tailscale: prairiedog-godzilla.ts.net
