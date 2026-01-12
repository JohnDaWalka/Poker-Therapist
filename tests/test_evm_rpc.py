"""Tests for backend.blockchain.evm_rpc module."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.blockchain.evm_rpc import (
    EvmRpcError,
    _rpc_call,
    get_chain_id,
    get_transaction_receipt,
    verify_tx,
    _hex_to_int,
)


@pytest.mark.asyncio
async def test_rpc_call_success() -> None:
    """Test successful RPC call."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"jsonrpc": "2.0", "id": 1, "result": "0x1"}
    mock_response.raise_for_status = MagicMock()
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        result = await _rpc_call("http://localhost:8545", "eth_chainId", [])
        assert result == "0x1"


@pytest.mark.asyncio
async def test_rpc_call_error() -> None:
    """Test RPC call with error response."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"code": -32601, "message": "Method not found"},
    }
    mock_response.raise_for_status = MagicMock()
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        with pytest.raises(EvmRpcError):
            await _rpc_call("http://localhost:8545", "invalid_method", [])


@pytest.mark.asyncio
async def test_rpc_call_http_error() -> None:
    """Test RPC call with HTTP error."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("HTTP 500")
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        with pytest.raises(Exception):
            await _rpc_call("http://localhost:8545", "eth_chainId", [])


@pytest.mark.asyncio
async def test_get_chain_id_success() -> None:
    """Test successful chain ID retrieval."""
    with patch(
        "backend.blockchain.evm_rpc._rpc_call", new_callable=AsyncMock
    ) as mock_rpc:
        mock_rpc.return_value = "0x1"
        result = await get_chain_id("http://localhost:8545")
        assert result == "0x1"
        mock_rpc.assert_called_once_with("http://localhost:8545", "eth_chainId", [])


@pytest.mark.asyncio
async def test_get_chain_id_returns_none() -> None:
    """Test chain ID retrieval when result is None."""
    with patch(
        "backend.blockchain.evm_rpc._rpc_call", new_callable=AsyncMock
    ) as mock_rpc:
        mock_rpc.return_value = None
        result = await get_chain_id("http://localhost:8545")
        assert result is None


@pytest.mark.asyncio
async def test_get_chain_id_exception() -> None:
    """Test chain ID retrieval with exception."""
    with patch(
        "backend.blockchain.evm_rpc._rpc_call", new_callable=AsyncMock
    ) as mock_rpc:
        mock_rpc.side_effect = Exception("Connection error")
        result = await get_chain_id("http://localhost:8545")
        assert result is None


@pytest.mark.asyncio
async def test_get_transaction_receipt_success() -> None:
    """Test successful transaction receipt retrieval."""
    expected_receipt = {
        "blockNumber": "0x123",
        "status": "0x1",
        "transactionHash": "0xabc",
    }
    with patch(
        "backend.blockchain.evm_rpc._rpc_call", new_callable=AsyncMock
    ) as mock_rpc:
        mock_rpc.return_value = expected_receipt
        result = await get_transaction_receipt(
            "http://localhost:8545",
            "0xabc",
        )
        assert result == expected_receipt
        mock_rpc.assert_called_once_with(
            "http://localhost:8545", "eth_getTransactionReceipt", ["0xabc"]
        )


@pytest.mark.asyncio
async def test_get_transaction_receipt_none() -> None:
    """Test transaction receipt retrieval when tx is not mined."""
    with patch(
        "backend.blockchain.evm_rpc._rpc_call", new_callable=AsyncMock
    ) as mock_rpc:
        mock_rpc.return_value = None
        result = await get_transaction_receipt(
            "http://localhost:8545",
            "0xabc",
        )
        assert result is None


@pytest.mark.asyncio
async def test_get_transaction_receipt_invalid_type() -> None:
    """Test transaction receipt retrieval with invalid return type."""
    with patch(
        "backend.blockchain.evm_rpc._rpc_call", new_callable=AsyncMock
    ) as mock_rpc:
        mock_rpc.return_value = "invalid"
        result = await get_transaction_receipt(
            "http://localhost:8545",
            "0xabc",
        )
        assert result is None


@pytest.mark.asyncio
async def test_get_transaction_receipt_exception() -> None:
    """Test transaction receipt retrieval with exception."""
    with patch(
        "backend.blockchain.evm_rpc._rpc_call", new_callable=AsyncMock
    ) as mock_rpc:
        mock_rpc.side_effect = Exception("Connection error")
        result = await get_transaction_receipt(
            "http://localhost:8545",
            "0xabc",
        )
        assert result is None


def test_hex_to_int_valid() -> None:
    """Test hex to int conversion with valid input."""
    assert _hex_to_int("0x1") == 1
    assert _hex_to_int("0xa") == 10
    assert _hex_to_int("0xff") == 255
    assert _hex_to_int("0x123") == 291


def test_hex_to_int_none() -> None:
    """Test hex to int conversion with None."""
    assert _hex_to_int(None) is None


def test_hex_to_int_empty() -> None:
    """Test hex to int conversion with empty string."""
    assert _hex_to_int("") is None


def test_hex_to_int_invalid() -> None:
    """Test hex to int conversion with invalid input."""
    assert _hex_to_int("invalid") is None
    assert _hex_to_int("0xGGG") is None


@pytest.mark.asyncio
async def test_verify_tx_success() -> None:
    """Test successful transaction verification."""
    mock_receipt = {
        "blockNumber": "0x123",
        "status": "0x1",
        "transactionHash": "0xabc",
    }
    
    with patch(
        "backend.blockchain.evm_rpc.get_transaction_receipt", new_callable=AsyncMock
    ) as mock_get_receipt, patch(
        "backend.blockchain.evm_rpc.get_chain_id", new_callable=AsyncMock
    ) as mock_get_chain:
        mock_get_receipt.return_value = mock_receipt
        mock_get_chain.return_value = "0x1"
        
        result = await verify_tx("http://localhost:8545", "0xabc")
        
        assert result["verified"] is True
        assert result["chain_id"] == "0x1"
        assert result["block_number"] == 0x123
        assert result["tx_status"] == 1


@pytest.mark.asyncio
async def test_verify_tx_not_found() -> None:
    """Test transaction verification when tx is not found."""
    with patch(
        "backend.blockchain.evm_rpc.get_transaction_receipt", new_callable=AsyncMock
    ) as mock_get_receipt, patch(
        "backend.blockchain.evm_rpc.get_chain_id", new_callable=AsyncMock
    ) as mock_get_chain:
        mock_get_receipt.return_value = None
        mock_get_chain.return_value = "0x1"
        
        result = await verify_tx("http://localhost:8545", "0xabc")
        
        assert result["verified"] is False
        assert result["chain_id"] == "0x1"
        assert result["block_number"] is None
        assert result["tx_status"] is None


@pytest.mark.asyncio
async def test_verify_tx_failed_status() -> None:
    """Test transaction verification with failed status."""
    mock_receipt = {
        "blockNumber": "0x456",
        "status": "0x0",
        "transactionHash": "0xdef",
    }
    
    with patch(
        "backend.blockchain.evm_rpc.get_transaction_receipt", new_callable=AsyncMock
    ) as mock_get_receipt, patch(
        "backend.blockchain.evm_rpc.get_chain_id", new_callable=AsyncMock
    ) as mock_get_chain:
        mock_get_receipt.return_value = mock_receipt
        mock_get_chain.return_value = "0x89"
        
        result = await verify_tx("http://localhost:8545", "0xdef")
        
        assert result["verified"] is True
        assert result["chain_id"] == "0x89"
        assert result["block_number"] == 0x456
        assert result["tx_status"] == 0


@pytest.mark.asyncio
async def test_verify_tx_no_chain_id() -> None:
    """Test transaction verification when chain ID is unavailable."""
    mock_receipt = {
        "blockNumber": "0x789",
        "status": "0x1",
        "transactionHash": "0xghi",
    }
    
    with patch(
        "backend.blockchain.evm_rpc.get_transaction_receipt", new_callable=AsyncMock
    ) as mock_get_receipt, patch(
        "backend.blockchain.evm_rpc.get_chain_id", new_callable=AsyncMock
    ) as mock_get_chain:
        mock_get_receipt.return_value = mock_receipt
        mock_get_chain.return_value = None
        
        result = await verify_tx("http://localhost:8545", "0xghi")
        
        assert result["verified"] is True
        assert result["chain_id"] is None
        assert result["block_number"] == 0x789
        assert result["tx_status"] == 1


@pytest.mark.asyncio
async def test_verify_tx_missing_fields() -> None:
    """Test transaction verification with missing receipt fields."""
    mock_receipt = {
        "transactionHash": "0xjkl",
    }
    
    with patch(
        "backend.blockchain.evm_rpc.get_transaction_receipt", new_callable=AsyncMock
    ) as mock_get_receipt, patch(
        "backend.blockchain.evm_rpc.get_chain_id", new_callable=AsyncMock
    ) as mock_get_chain:
        mock_get_receipt.return_value = mock_receipt
        mock_get_chain.return_value = "0x1"
        
        result = await verify_tx("http://localhost:8545", "0xjkl")
        
        assert result["verified"] is True
        assert result["chain_id"] == "0x1"
        assert result["block_number"] is None
        assert result["tx_status"] is None
