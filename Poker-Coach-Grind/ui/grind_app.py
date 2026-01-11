"""Streamlit UI for Poker-Coach-Grind."""

import asyncio
from datetime import datetime
from typing import Dict, List

try:
    import streamlit as st
except ImportError:
    print("Streamlit not installed. Install with: pip install streamlit")
    exit(1)

# Import modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto.price_tracker import get_crypto_prices
from crypto.wallet_tracker import CryptoTracker


def show_crypto_prices():
    """Display cryptocurrency prices."""
    st.header("💰 Cryptocurrency Prices")
    
    # Token selection
    all_tokens = ["ETH", "SOL", "ONDO", "VIRTUAL", "JUP", "AIXBET", "RNDR", "UNI", "LTC", "POL", "SUI"]
    selected_tokens = st.multiselect(
        "Select tokens to display",
        all_tokens,
        default=["ETH", "SOL", "ONDO", "VIRTUAL"]
    )
    
    if st.button("Refresh Prices"):
        with st.spinner("Fetching prices..."):
            prices = asyncio.run(get_crypto_prices(selected_tokens))
            
            if prices:
                # Create a table
                data = []
                for symbol, info in sorted(prices.items()):
                    data.append({
                        "Symbol": symbol,
                        "Price": f"${info['price']:.2f}",
                        "24h Change": f"{info['change_24h']:.2f}%",
                        "Volume": f"${info['volume_24h']:,.0f}",
                        "Market Cap": f"${info['market_cap']:,.0f}",
                    })
                
                st.table(data)
            else:
                st.error("Could not fetch prices. Check your internet connection.")


def show_bankroll_tracker():
    """Display bankroll tracking interface."""
    st.header("💵 Bankroll Tracker")
    
    # User ID input
    user_id = st.text_input("User ID", value="user123")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Add Transaction")
        amount = st.number_input("Amount", value=0.0, step=10.0)
        transaction_type = st.selectbox(
            "Transaction Type",
            ["cash_game", "tournament", "deposit", "withdrawal"]
        )
        stakes = st.text_input("Stakes (optional)", value="")
        notes = st.text_area("Notes (optional)", value="")
        
        if st.button("Add Transaction"):
            st.success(f"Transaction added: {transaction_type} ${amount:.2f}")
            # In production, this would call the API
    
    with col2:
        st.subheader("Current Bankroll")
        st.metric("Balance", "$1,250.00", "+$250.00")
        st.metric("ROI", "15.5%", "+2.3%")
        st.metric("Total Sessions", "42", "+3")


def show_hand_history():
    """Display hand history viewer."""
    st.header("📊 Hand History Viewer")
    
    st.subheader("SQL Query")
    
    # Pre-defined queries
    query_templates = {
        "All winning hands": "SELECT * FROM hand_histories_grind WHERE won_amount > 0 AND user_id = 'user123' ORDER BY date_played DESC",
        "Recent sessions": "SELECT session_id, COUNT(*) as hands, SUM(won_amount) as profit FROM hand_histories_grind WHERE user_id = 'user123' GROUP BY session_id ORDER BY MAX(date_played) DESC",
        "Best hands": "SELECT * FROM hand_histories_grind WHERE won_amount > 0 AND user_id = 'user123' ORDER BY won_amount DESC LIMIT 10",
    }
    
    template = st.selectbox("Query Template", list(query_templates.keys()))
    
    query = st.text_area(
        "SQL Query",
        value=query_templates[template],
        height=100
    )
    
    if st.button("Execute Query"):
        st.info("Query execution would happen here via API")
        st.caption("Note: In production, this connects to the API endpoint")


def show_portfolio():
    """Display crypto portfolio."""
    st.header("🪙 Crypto Portfolio")
    
    user_id = st.text_input("User ID", value="user123", key="portfolio_user")
    
    # Add wallet interface
    with st.expander("Add Wallet"):
        blockchain = st.selectbox("Blockchain", ["ethereum", "solana", "polygon"])
        address = st.text_input("Wallet Address")
        label = st.text_input("Label (optional)")
        
        if st.button("Add Wallet"):
            if address:
                st.success(f"Wallet added: {blockchain} - {address[:10]}...")
            else:
                st.error("Please enter a wallet address")
    
    # Display portfolio
    st.subheader("Portfolio Value")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Value", "$2,500.00")
    with col2:
        st.metric("ETH", "0.5 ETH", "$1,250.00")
    with col3:
        st.metric("SOL", "15 SOL", "$1,250.00")


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Poker-Coach-Grind",
        page_icon="🎰",
        layout="wide"
    )
    
    st.title("🎰 Poker-Coach-Grind")
    st.caption("Bankroll Tracker • Hand History Reviewer • Crypto Portfolio")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Bankroll Tracker", "Hand History", "Crypto Prices", "Portfolio"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Poker-Coach-Grind** v1.0.0\n\n"
        "Track your bankroll, review hands, and monitor crypto winnings."
    )
    
    # Show selected page
    if page == "Bankroll Tracker":
        show_bankroll_tracker()
    elif page == "Hand History":
        show_hand_history()
    elif page == "Crypto Prices":
        show_crypto_prices()
    elif page == "Portfolio":
        show_portfolio()


if __name__ == "__main__":
    main()
