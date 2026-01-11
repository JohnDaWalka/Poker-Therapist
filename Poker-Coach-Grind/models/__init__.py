"""Pydantic models for Poker-Coach-Grind."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class BankrollTracker(BaseModel):
    """Model for tracking bankroll."""
    
    user_id: str
    current_balance: float = 0.0
    currency: str = "USD"


class HandHistorySummary(BaseModel):
    """Summary of a poker hand."""
    
    hand_id: Optional[str]
    date_played: datetime
    stakes: Optional[str]
    won_amount: Optional[float]
    result: str  # win, loss, break-even


class SessionSummary(BaseModel):
    """Summary of a poker session."""
    
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    hands_played: int
    net_profit: float
    bb_per_100: Optional[float]


class CryptoWalletInfo(BaseModel):
    """Information about a crypto wallet."""
    
    blockchain: str
    address: str
    label: Optional[str]
    balance: Optional[float]
    value_usd: Optional[float]


__all__ = [
    "BankrollTracker",
    "HandHistorySummary",
    "SessionSummary",
    "CryptoWalletInfo",
]
