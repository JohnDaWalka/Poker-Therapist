"""Bankroll management API routes."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, func, select

from ..database.models import BankrollTransaction
from ..database.session import get_grind_db

router = APIRouter()


class TransactionRequest(BaseModel):
    """Request model for creating a transaction."""
    
    user_id: str
    amount: float
    transaction_type: str  # cash_game, tournament, deposit, withdrawal
    platform: Optional[str] = None
    stakes: Optional[str] = None
    session_id: Optional[str] = None
    notes: Optional[str] = None
    currency: str = "USD"
    crypto_currency: Optional[str] = None


class TransactionResponse(BaseModel):
    """Response model for a transaction."""
    
    id: int
    user_id: str
    timestamp: datetime
    amount: float
    balance_after: float
    transaction_type: str
    platform: Optional[str]
    stakes: Optional[str]
    session_id: Optional[str]
    notes: Optional[str]
    currency: str
    crypto_currency: Optional[str]


class BankrollResponse(BaseModel):
    """Response model for current bankroll."""
    
    user_id: str
    current_balance: float
    currency: str
    last_updated: Optional[datetime]
    transaction_count: int


class BankrollStatsResponse(BaseModel):
    """Response model for bankroll statistics."""
    
    user_id: str
    current_balance: float
    total_deposits: float
    total_withdrawals: float
    total_won: float
    total_lost: float
    net_profit: float
    roi: float
    transaction_count: int
    first_transaction: Optional[datetime]
    last_transaction: Optional[datetime]


@router.get("/{user_id}", response_model=BankrollResponse)
async def get_bankroll(user_id: str) -> BankrollResponse:
    """Get current bankroll for a user."""
    try:
        async with get_grind_db() as db:
            # Get most recent transaction to find current balance
            stmt = (
                select(BankrollTransaction)
                .where(BankrollTransaction.user_id == user_id)
                .order_by(desc(BankrollTransaction.timestamp))
                .limit(1)
            )
            result = await db.execute(stmt)
            last_transaction = result.scalar_one_or_none()
            
            # Count total transactions
            count_stmt = select(func.count(BankrollTransaction.id)).where(
                BankrollTransaction.user_id == user_id
            )
            count_result = await db.execute(count_stmt)
            count = count_result.scalar_one()
            
            if last_transaction:
                return BankrollResponse(
                    user_id=user_id,
                    current_balance=last_transaction.balance_after,
                    currency=last_transaction.currency,
                    last_updated=last_transaction.timestamp,
                    transaction_count=count,
                )
            else:
                # No transactions yet
                return BankrollResponse(
                    user_id=user_id,
                    current_balance=0.0,
                    currency="USD",
                    last_updated=None,
                    transaction_count=0,
                )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/transaction", response_model=TransactionResponse)
async def create_transaction(request: TransactionRequest) -> TransactionResponse:
    """Create a new bankroll transaction."""
    try:
        async with get_grind_db() as db:
            # Get current balance
            stmt = (
                select(BankrollTransaction)
                .where(BankrollTransaction.user_id == request.user_id)
                .order_by(desc(BankrollTransaction.timestamp))
                .limit(1)
            )
            result = await db.execute(stmt)
            last_transaction = result.scalar_one_or_none()
            
            current_balance = last_transaction.balance_after if last_transaction else 0.0
            new_balance = current_balance + request.amount
            
            # Create new transaction
            transaction = BankrollTransaction(
                user_id=request.user_id,
                timestamp=datetime.utcnow(),
                amount=request.amount,
                balance_after=new_balance,
                transaction_type=request.transaction_type,
                platform=request.platform,
                stakes=request.stakes,
                session_id=request.session_id,
                notes=request.notes,
                currency=request.currency,
                crypto_currency=request.crypto_currency,
            )
            
            db.add(transaction)
            await db.commit()
            await db.refresh(transaction)
            
            return TransactionResponse(
                id=transaction.id,
                user_id=transaction.user_id,
                timestamp=transaction.timestamp,
                amount=transaction.amount,
                balance_after=transaction.balance_after,
                transaction_type=transaction.transaction_type,
                platform=transaction.platform,
                stakes=transaction.stakes,
                session_id=transaction.session_id,
                notes=transaction.notes,
                currency=transaction.currency,
                crypto_currency=transaction.crypto_currency,
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/history/{user_id}", response_model=List[TransactionResponse])
async def get_bankroll_history(
    user_id: str,
    limit: int = 100,
    offset: int = 0
) -> List[TransactionResponse]:
    """Get bankroll transaction history."""
    try:
        async with get_grind_db() as db:
            stmt = (
                select(BankrollTransaction)
                .where(BankrollTransaction.user_id == user_id)
                .order_by(desc(BankrollTransaction.timestamp))
                .limit(limit)
                .offset(offset)
            )
            result = await db.execute(stmt)
            transactions = result.scalars().all()
            
            return [
                TransactionResponse(
                    id=t.id,
                    user_id=t.user_id,
                    timestamp=t.timestamp,
                    amount=t.amount,
                    balance_after=t.balance_after,
                    transaction_type=t.transaction_type,
                    platform=t.platform,
                    stakes=t.stakes,
                    session_id=t.session_id,
                    notes=t.notes,
                    currency=t.currency,
                    crypto_currency=t.crypto_currency,
                )
                for t in transactions
            ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/stats/{user_id}", response_model=BankrollStatsResponse)
async def get_bankroll_stats(user_id: str) -> BankrollStatsResponse:
    """Get comprehensive bankroll statistics."""
    try:
        async with get_grind_db() as db:
            # Get all transactions
            stmt = (
                select(BankrollTransaction)
                .where(BankrollTransaction.user_id == user_id)
                .order_by(BankrollTransaction.timestamp)
            )
            result = await db.execute(stmt)
            transactions = result.scalars().all()
            
            if not transactions:
                return BankrollStatsResponse(
                    user_id=user_id,
                    current_balance=0.0,
                    total_deposits=0.0,
                    total_withdrawals=0.0,
                    total_won=0.0,
                    total_lost=0.0,
                    net_profit=0.0,
                    roi=0.0,
                    transaction_count=0,
                    first_transaction=None,
                    last_transaction=None,
                )
            
            # Calculate statistics
            current_balance = transactions[-1].balance_after
            total_deposits = sum(t.amount for t in transactions if t.transaction_type == "deposit")
            total_withdrawals = sum(abs(t.amount) for t in transactions if t.transaction_type == "withdrawal")
            total_won = sum(t.amount for t in transactions if t.amount > 0 and t.transaction_type in ["cash_game", "tournament"])
            total_lost = sum(abs(t.amount) for t in transactions if t.amount < 0 and t.transaction_type in ["cash_game", "tournament"])
            net_profit = total_won - total_lost
            
            # Calculate ROI
            roi = 0.0
            if total_deposits > 0:
                roi = (net_profit / total_deposits) * 100
            
            return BankrollStatsResponse(
                user_id=user_id,
                current_balance=current_balance,
                total_deposits=total_deposits,
                total_withdrawals=total_withdrawals,
                total_won=total_won,
                total_lost=total_lost,
                net_profit=net_profit,
                roi=roi,
                transaction_count=len(transactions),
                first_transaction=transactions[0].timestamp,
                last_transaction=transactions[-1].timestamp,
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
