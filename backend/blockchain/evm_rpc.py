"""Minimal async EVM JSON-RPC helpers.

We intentionally avoid heavy dependencies (e.g., web3.py) and instead use
httpx to query standard Ethereum JSON-RPC methods.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx


class EvmRpcError(RuntimeError):
    """Raised when an EVM JSON-RPC call fails."""


async def _rpc_call(rpc_url: str, method: str, params: list[Any]) -> Any:
    payload: Dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(rpc_url, json=payload)
        resp.raise_for_status()
        data = resp.json()

    if "error" in data:
        raise EvmRpcError(str(data["error"]))
    return data.get("result")


async def get_chain_id(rpc_url: str) -> Optional[str]:
    """Return hex chain id string (e.g., '0x1') if available."""
    try:
        result = await _rpc_call(rpc_url, "eth_chainId", [])
        return str(result) if result is not None else None
    except Exception:
        return None


async def get_transaction_receipt(rpc_url: str, tx_hash: str) -> Optional[Dict[str, Any]]:
    """Return receipt dict if tx is mined, else None."""
    try:
        result = await _rpc_call(rpc_url, "eth_getTransactionReceipt", [tx_hash])
        if result is None:
            return None
        if not isinstance(result, dict):
            return None
        return result
    except Exception:
        return None


def _hex_to_int(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    try:
        return int(value, 16)
    except Exception:
        return None


async def verify_tx(rpc_url: str, tx_hash: str) -> Dict[str, Any]:
    """Verify a transaction exists and return normalized verification fields."""
    receipt = await get_transaction_receipt(rpc_url, tx_hash)
    chain_id = await get_chain_id(rpc_url)

    if receipt is None:
        return {
            "verified": False,
            "chain_id": chain_id,
            "block_number": None,
            "tx_status": None,
        }

    block_number = _hex_to_int(receipt.get("blockNumber"))
    status = _hex_to_int(receipt.get("status"))

    return {
        "verified": True,
        "chain_id": chain_id,
        "block_number": block_number,
        "tx_status": status,
    }
