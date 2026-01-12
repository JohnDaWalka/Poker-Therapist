"""Cryptocurrency API routes."""

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..crypto.price_tracker import get_crypto_prices
from ..crypto.wallet_tracker import CryptoTracker

router = APIRouter()


class PricesResponse(BaseModel):
    """Response model for cryptocurrency prices."""
    
    prices: Dict[str, Dict]


class WalletRequest(BaseModel):
    """Request model for adding a wallet."""
    
    user_id: str
    blockchain: str
    address: str
    label: Optional[str] = None


class WalletBalanceRequest(BaseModel):
    """Request model for getting wallet balances."""
    
    user_id: str
    wallets: List[Dict[str, str]]  # [{"blockchain": "ethereum", "address": "0x..."}]


class PortfolioResponse(BaseModel):
    """Response model for portfolio value."""
    
    total_usd: float
    wallets: List[Dict]
    by_token: Dict
    last_updated: str


@router.get("/prices", response_model=PricesResponse)
async def get_prices(
    symbols: Optional[str] = None
) -> PricesResponse:
    """Get current cryptocurrency prices.
    
    Args:
        symbols: Comma-separated list of crypto symbols (e.g., 'ETH,SOL,ONDO')
                If not provided, returns all supported tokens.
    
    Returns:
        Dictionary of current prices with market data
    """
    try:
        symbol_list = None
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(",")]
        
        prices = await get_crypto_prices(symbol_list)
        
        return PricesResponse(prices=prices)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/wallet/add")
async def add_wallet(request: WalletRequest) -> Dict:
    """Add a cryptocurrency wallet for tracking."""
    try:
        tracker = CryptoTracker(user_id=request.user_id)
        wallet = await tracker.add_wallet(
            blockchain=request.blockchain,
            address=request.address,
            label=request.label,
        )
        
        return {
            "success": True,
            "wallet": wallet,
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/portfolio", response_model=PortfolioResponse)
async def get_portfolio(request: WalletBalanceRequest) -> PortfolioResponse:
    """Get portfolio value across all wallets.
    
    Args:
        request: User ID and list of wallets to check
        
    Returns:
        Total portfolio value and breakdown by wallet and token
    """
    try:
        # Get current prices for all supported tokens
        prices = await get_crypto_prices()
        price_dict = {k: v["price"] for k, v in prices.items()}
        
        # Get portfolio value
        tracker = CryptoTracker(user_id=request.user_id)
        portfolio = await tracker.get_portfolio_value(
            wallets=request.wallets,
            prices=price_dict,
        )
        
        return PortfolioResponse(
            total_usd=portfolio["total_usd"],
            wallets=portfolio["wallets"],
            by_token=portfolio["by_token"],
            last_updated=portfolio["last_updated"],
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/wallet/{user_id}/{blockchain}/{address}")
async def get_wallet_balance(
    user_id: str,
    blockchain: str,
    address: str
) -> Dict:
    """Get balance for a specific wallet.
    
    Args:
        user_id: User identifier
        blockchain: Blockchain name (ethereum, solana, etc.)
        address: Wallet address
        
    Returns:
        Wallet balance in native token and USD value
    """
    try:
        tracker = CryptoTracker(user_id=user_id)
        balance = await tracker.get_wallet_balance(blockchain, address)
        
        if balance is None:
            raise HTTPException(
                status_code=404,
                detail=f"Could not fetch balance for {blockchain} wallet"
            )
        
        # Get current price
        blockchain_to_symbol = {
            "ethereum": "ETH",
            "eth": "ETH",
            "solana": "SOL",
            "sol": "SOL",
            "polygon": "POL",
            "pol": "POL",
        }
        
        symbol = blockchain_to_symbol.get(blockchain.lower(), blockchain.upper())
        prices = await get_crypto_prices([symbol])
        price_usd = prices.get(symbol, {}).get("price", 0)
        
        return {
            "user_id": user_id,
            "blockchain": blockchain,
            "address": address,
            "balance": balance,
            "symbol": symbol,
            "price_usd": price_usd,
            "value_usd": balance * price_usd,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/supported-tokens")
async def get_supported_tokens() -> Dict:
    """Get list of supported cryptocurrency tokens."""
    return {
        "tokens": [
            {"symbol": "ETH", "name": "Ethereum", "blockchain": "ethereum"},
            {"symbol": "RNDR", "name": "Render", "blockchain": "ethereum"},
            {"symbol": "SUI", "name": "Sui", "blockchain": "sui"},
            {"symbol": "UNI", "name": "Uniswap", "blockchain": "ethereum"},
            {"symbol": "LTC", "name": "Litecoin", "blockchain": "litecoin"},
            {"symbol": "ONDO", "name": "Ondo Finance", "blockchain": "ethereum"},
            {"symbol": "POL", "name": "Polygon", "blockchain": "polygon"},
            {"symbol": "VIRTUAL", "name": "Virtuals Protocol", "blockchain": "ethereum"},
            {"symbol": "SOL", "name": "Solana", "blockchain": "solana"},
            {"symbol": "JUP", "name": "Jupiter", "blockchain": "solana"},
            {"symbol": "AIXBET", "name": "AIxBET", "blockchain": "ethereum"},
        ]
    }
