"""Cryptocurrency wallet tracking and balance monitoring."""

import os
from datetime import datetime
from typing import Dict, List, Optional

import httpx


class CryptoTracker:
    """Track cryptocurrency wallets and portfolio value."""
    
    def __init__(self, user_id: str):
        """Initialize tracker for a user.
        
        Args:
            user_id: User identifier
        """
        self.user_id = user_id
        self.eth_rpc_url = os.getenv("ETHEREUM_RPC_URL", "https://eth.llamarpc.com")
        self.solana_rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
    
    async def get_eth_balance(self, address: str) -> Optional[float]:
        """Get Ethereum wallet balance.
        
        Args:
            address: Ethereum wallet address
            
        Returns:
            Balance in ETH, or None if error
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.eth_rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "method": "eth_getBalance",
                        "params": [address, "latest"],
                        "id": 1,
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                
                if "result" in data:
                    # Convert from wei to ETH
                    balance_wei = int(data["result"], 16)
                    return balance_wei / 1e18
                return None
                
        except Exception as e:
            print(f"Error fetching ETH balance: {e}")
            return None
    
    async def get_solana_balance(self, address: str) -> Optional[float]:
        """Get Solana wallet balance.
        
        Args:
            address: Solana wallet address
            
        Returns:
            Balance in SOL, or None if error
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.solana_rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getBalance",
                        "params": [address],
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                
                if "result" in data and "value" in data["result"]:
                    # Convert from lamports to SOL
                    balance_lamports = data["result"]["value"]
                    return balance_lamports / 1e9
                return None
                
        except Exception as e:
            print(f"Error fetching Solana balance: {e}")
            return None
    
    async def get_wallet_balance(self, blockchain: str, address: str) -> Optional[float]:
        """Get balance for any supported blockchain.
        
        Args:
            blockchain: Blockchain name (ethereum, solana, etc.)
            address: Wallet address
            
        Returns:
            Balance in native token, or None if error
        """
        blockchain_lower = blockchain.lower()
        
        if blockchain_lower in ["ethereum", "eth", "polygon", "pol"]:
            return await self.get_eth_balance(address)
        elif blockchain_lower in ["solana", "sol"]:
            return await self.get_solana_balance(address)
        else:
            print(f"Unsupported blockchain: {blockchain}")
            return None
    
    async def get_portfolio_value(
        self,
        wallets: List[Dict[str, str]],
        prices: Dict[str, float]
    ) -> Dict:
        """Calculate total portfolio value across all wallets.
        
        Args:
            wallets: List of wallet dicts with 'blockchain' and 'address' keys
            prices: Dict mapping blockchain symbols to USD prices
            
        Returns:
            Portfolio summary with total value and breakdown
        """
        portfolio = {
            "total_usd": 0.0,
            "wallets": [],
            "by_token": {},
            "last_updated": datetime.utcnow().isoformat(),
        }
        
        blockchain_to_symbol = {
            "ethereum": "ETH",
            "eth": "ETH",
            "solana": "SOL",
            "sol": "SOL",
            "polygon": "POL",
            "pol": "POL",
        }
        
        for wallet in wallets:
            blockchain = wallet.get("blockchain", "").lower()
            address = wallet.get("address", "")
            
            if not blockchain or not address:
                continue
            
            balance = await self.get_wallet_balance(blockchain, address)
            
            if balance is not None:
                symbol = blockchain_to_symbol.get(blockchain, blockchain.upper())
                price_usd = prices.get(symbol, 0)
                value_usd = balance * price_usd
                
                wallet_info = {
                    "blockchain": blockchain,
                    "address": address,
                    "balance": balance,
                    "symbol": symbol,
                    "price_usd": price_usd,
                    "value_usd": value_usd,
                }
                
                portfolio["wallets"].append(wallet_info)
                portfolio["total_usd"] += value_usd
                
                # Aggregate by token
                if symbol not in portfolio["by_token"]:
                    portfolio["by_token"][symbol] = {
                        "balance": 0.0,
                        "value_usd": 0.0,
                        "price_usd": price_usd,
                    }
                portfolio["by_token"][symbol]["balance"] += balance
                portfolio["by_token"][symbol]["value_usd"] += value_usd
        
        return portfolio
    
    async def add_wallet(self, blockchain: str, address: str, label: Optional[str] = None):
        """Add a wallet for tracking (would save to database in production).
        
        Args:
            blockchain: Blockchain name
            address: Wallet address
            label: Optional label for the wallet
        """
        # In a real implementation, this would save to the database
        # For now, just validate the inputs
        if not blockchain or not address:
            raise ValueError("Blockchain and address are required")
        
        return {
            "user_id": self.user_id,
            "blockchain": blockchain.lower(),
            "address": address,
            "label": label,
            "created_at": datetime.utcnow().isoformat(),
        }


# For quick testing
if __name__ == "__main__":
    import asyncio
    from .price_tracker import get_crypto_prices
    
    async def test():
        tracker = CryptoTracker(user_id="test_user")
        
        # Get current prices
        prices = await get_crypto_prices(["ETH", "SOL"])
        price_dict = {k: v["price"] for k, v in prices.items()}
        
        # Example wallets (replace with real addresses for testing)
        wallets = [
            {"blockchain": "ethereum", "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"},
            {"blockchain": "solana", "address": "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs"},
        ]
        
        portfolio = await tracker.get_portfolio_value(wallets, price_dict)
        print(f"Total portfolio value: ${portfolio['total_usd']:.2f}")
        
        for wallet in portfolio["wallets"]:
            print(f"  {wallet['symbol']}: {wallet['balance']:.4f} (${wallet['value_usd']:.2f})")
    
    asyncio.run(test())
