"""Cryptocurrency price tracking using CoinGecko API."""

import os
from datetime import datetime
from typing import Dict, List, Optional

import httpx

# Mapping of common symbols to CoinGecko IDs
CRYPTO_IDS = {
    "ETH": "ethereum",
    "RNDR": "render-token",
    "SUI": "sui",
    "UNI": "uniswap",
    "LTC": "litecoin",
    "ONDO": "ondo-finance",
    "POL": "polygon-ecosystem-token",
    "VIRTUAL": "virtuals-protocol",
    "SOL": "solana",
    "JUP": "jupiter-exchange-solana",
    "AIXBET": "aixbt-by-virtuals",  # AIxBET token
    "BTC": "bitcoin",
    "USDC": "usd-coin",
    "USDT": "tether",
}

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"


async def get_crypto_prices(
    symbols: Optional[List[str]] = None,
    vs_currency: str = "usd"
) -> Dict[str, Dict]:
    """Get current cryptocurrency prices.
    
    Args:
        symbols: List of crypto symbols (e.g., ['ETH', 'SOL']). If None, gets all supported tokens.
        vs_currency: Fiat currency for prices (default: 'usd')
        
    Returns:
        Dictionary mapping symbol to price data:
        {
            'ETH': {
                'price': 2500.50,
                'market_cap': 300000000000,
                'volume_24h': 15000000000,
                'change_24h': 2.5,
                'last_updated': '2026-01-11T03:00:00Z'
            },
            ...
        }
    """
    if symbols is None:
        symbols = list(CRYPTO_IDS.keys())
    
    # Get CoinGecko IDs for requested symbols
    ids = [CRYPTO_IDS.get(symbol.upper()) for symbol in symbols if symbol.upper() in CRYPTO_IDS]
    
    if not ids:
        return {}
    
    try:
        api_key = os.getenv("COINGECKO_API_KEY")
        headers = {}
        if api_key:
            headers["x-cg-pro-api-key"] = api_key
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{COINGECKO_API_URL}/simple/price",
                params={
                    "ids": ",".join(ids),
                    "vs_currencies": vs_currency,
                    "include_market_cap": "true",
                    "include_24hr_vol": "true",
                    "include_24hr_change": "true",
                    "include_last_updated_at": "true",
                },
                headers=headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
        
        # Convert from CoinGecko ID back to symbol
        result = {}
        for symbol in symbols:
            symbol_upper = symbol.upper()
            gecko_id = CRYPTO_IDS.get(symbol_upper)
            if gecko_id and gecko_id in data:
                price_data = data[gecko_id]
                result[symbol_upper] = {
                    "price": price_data.get(vs_currency, 0),
                    "market_cap": price_data.get(f"{vs_currency}_market_cap", 0),
                    "volume_24h": price_data.get(f"{vs_currency}_24h_vol", 0),
                    "change_24h": price_data.get(f"{vs_currency}_24h_change", 0),
                    "last_updated": datetime.fromtimestamp(
                        price_data.get("last_updated_at", 0)
                    ).isoformat() if price_data.get("last_updated_at") else None,
                }
        
        return result
        
    except httpx.HTTPError as e:
        print(f"Error fetching crypto prices: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error fetching crypto prices: {e}")
        return {}


async def get_historical_price(
    symbol: str,
    date: str,
    vs_currency: str = "usd"
) -> Optional[float]:
    """Get historical cryptocurrency price for a specific date.
    
    Args:
        symbol: Crypto symbol (e.g., 'ETH')
        date: Date in format 'dd-mm-yyyy'
        vs_currency: Fiat currency for price (default: 'usd')
        
    Returns:
        Price at that date, or None if not available
    """
    gecko_id = CRYPTO_IDS.get(symbol.upper())
    if not gecko_id:
        return None
    
    try:
        api_key = os.getenv("COINGECKO_API_KEY")
        headers = {}
        if api_key:
            headers["x-cg-pro-api-key"] = api_key
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{COINGECKO_API_URL}/coins/{gecko_id}/history",
                params={"date": date, "localization": "false"},
                headers=headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
        
        market_data = data.get("market_data", {})
        current_price = market_data.get("current_price", {})
        return current_price.get(vs_currency)
        
    except Exception as e:
        print(f"Error fetching historical price for {symbol}: {e}")
        return None


async def update_all_prices() -> Dict[str, Dict]:
    """Update prices for all supported cryptocurrencies.
    
    Returns:
        Dictionary of all current prices
    """
    return await get_crypto_prices()


# For quick testing
if __name__ == "__main__":
    import asyncio
    
    async def test():
        prices = await get_crypto_prices(["ETH", "SOL", "ONDO", "VIRTUAL"])
        for symbol, data in prices.items():
            print(f"{symbol}: ${data['price']:.2f} (24h: {data['change_24h']:.2f}%)")
    
    asyncio.run(test())
