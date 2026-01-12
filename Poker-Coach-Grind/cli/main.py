"""Command-line interface for Poker-Coach-Grind."""

import asyncio
import sys
from datetime import datetime
from typing import Optional

try:
    from ..crypto.price_tracker import get_crypto_prices
    from ..crypto.wallet_tracker import CryptoTracker
    from ..database.models import init_db
except ImportError:
    # Handle running as script
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from crypto.price_tracker import get_crypto_prices
    from crypto.wallet_tracker import CryptoTracker
    from database.models import init_db


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_section(text: str):
    """Print a formatted section header."""
    print(f"\n{text}")
    print("-" * 40)


async def show_crypto_prices(symbols: Optional[list] = None):
    """Show current cryptocurrency prices."""
    print_header("Cryptocurrency Prices")
    
    if symbols is None:
        symbols = ["ETH", "SOL", "ONDO", "VIRTUAL", "JUP", "AIXBET", "RNDR", "UNI", "LTC", "POL", "SUI"]
    
    prices = await get_crypto_prices(symbols)
    
    if not prices:
        print("Could not fetch prices. Check your internet connection.")
        return
    
    print(f"\n{'Symbol':<10} {'Price (USD)':<15} {'24h Change':<15} {'Market Cap':<20}")
    print("-" * 70)
    
    for symbol, data in sorted(prices.items()):
        price = data.get("price", 0)
        change = data.get("change_24h", 0)
        market_cap = data.get("market_cap", 0)
        
        change_str = f"{change:+.2f}%" if change else "N/A"
        market_cap_str = f"${market_cap:,.0f}" if market_cap else "N/A"
        
        print(f"{symbol:<10} ${price:<14.2f} {change_str:<15} {market_cap_str:<20}")


async def show_portfolio(user_id: str, wallets: list):
    """Show portfolio value."""
    print_header(f"Portfolio for {user_id}")
    
    # Get current prices
    prices = await get_crypto_prices()
    price_dict = {k: v["price"] for k, v in prices.items()}
    
    # Get portfolio value
    tracker = CryptoTracker(user_id=user_id)
    portfolio = await tracker.get_portfolio_value(wallets, price_dict)
    
    print(f"\nTotal Portfolio Value: ${portfolio['total_usd']:.2f}")
    print(f"Last Updated: {portfolio['last_updated']}")
    
    print_section("By Token")
    for symbol, data in sorted(portfolio["by_token"].items()):
        print(f"  {symbol}: {data['balance']:.4f} (${data['value_usd']:.2f})")
    
    print_section("By Wallet")
    for i, wallet in enumerate(portfolio["wallets"], 1):
        print(f"  {i}. {wallet['blockchain'].upper()}")
        print(f"     Address: {wallet['address']}")
        print(f"     Balance: {wallet['balance']:.4f} {wallet['symbol']} (${wallet['value_usd']:.2f})")


def init_database():
    """Initialize the database."""
    print_header("Database Initialization")
    print("\nInitializing database tables...")
    
    try:
        init_db()
        print("✓ Database initialized successfully!")
        print("  Location: poker_grind.db")
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        return False
    
    return True


def show_help():
    """Show help information."""
    print_header("Poker-Coach-Grind CLI")
    
    print("\nUsage: python -m Poker-Coach-Grind.cli.main [command] [options]")
    
    print_section("Commands")
    print("  init-db              Initialize the database")
    print("  prices [symbols]     Show cryptocurrency prices")
    print("                       Example: prices ETH,SOL,ONDO")
    print("  portfolio <user_id>  Show portfolio value (requires wallet config)")
    print("  help                 Show this help message")
    
    print_section("Examples")
    print("  python -m Poker-Coach-Grind.cli.main init-db")
    print("  python -m Poker-Coach-Grind.cli.main prices")
    print("  python -m Poker-Coach-Grind.cli.main prices ETH,SOL,VIRTUAL")
    
    print_section("API Server")
    print("  Start the API server:")
    print("  uvicorn Poker-Coach-Grind.api.main:app --reload --port 8001")
    print()


async def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "help" or command == "--help" or command == "-h":
        show_help()
    
    elif command == "init-db":
        init_database()
    
    elif command == "prices":
        symbols = None
        if len(sys.argv) > 2:
            symbols = [s.strip().upper() for s in sys.argv[2].split(",")]
        await show_crypto_prices(symbols)
    
    elif command == "portfolio":
        if len(sys.argv) < 3:
            print("Error: user_id required")
            print("Usage: python -m Poker-Coach-Grind.cli.main portfolio <user_id>")
            return
        
        user_id = sys.argv[2]
        
        # Example wallets - in production, load from database
        print("\nNote: Using example wallets. Configure wallets via API for real data.")
        wallets = [
            {"blockchain": "ethereum", "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"},
            {"blockchain": "solana", "address": "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs"},
        ]
        
        await show_portfolio(user_id, wallets)
    
    else:
        print(f"Unknown command: {command}")
        print("Run 'python -m Poker-Coach-Grind.cli.main help' for usage information")


if __name__ == "__main__":
    asyncio.run(main())
