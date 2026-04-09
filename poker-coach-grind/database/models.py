"""Database models for Poker-Coach-Grind."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class BankrollTransaction(Base):
    """Bankroll transaction record."""

    __tablename__ = "bankroll_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    amount = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    transaction_type = Column(String(50), nullable=False)  # cash_game, tournament, deposit, withdrawal
    platform = Column(String(100))  # CoinPoker, PokerStars, etc.
    stakes = Column(String(50))
    session_id = Column(String(255), index=True)
    notes = Column(Text)
    currency = Column(String(10), default="USD")
    crypto_currency = Column(String(20))  # ETH, SOL, etc.
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class HandHistoryGrind(Base):
    """Hand history records optimized for SQL queries."""

    __tablename__ = "hand_histories_grind"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), index=True)
    hand_id = Column(String(255), index=True)
    platform = Column(String(100), nullable=False, index=True)
    date_played = Column(DateTime, nullable=False, index=True)
    game_type = Column(String(50))  # NLHE, PLO, etc.
    stakes = Column(String(50), index=True)
    table_name = Column(String(255))
    num_players = Column(Integer)
    hero_position = Column(String(20))
    hole_cards = Column(String(50))
    board = Column(String(100))
    pot_size = Column(Float)
    won_amount = Column(Float, index=True)
    vpip = Column(Float)  # Voluntarily put money in pot
    pfr = Column(Float)   # Pre-flop raise
    aggression_factor = Column(Float)
    showdown_won = Column(Integer)  # Boolean: 0 or 1
    all_in = Column(Integer)  # Boolean: 0 or 1
    actions = Column(Text)
    summary = Column(Text)
    raw_text = Column(Text, nullable=False)
    tx_hash = Column(String(66))  # Blockchain transaction hash
    verified = Column(Integer, default=0)  # Boolean: blockchain verified
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class CryptoWallet(Base):
    """Cryptocurrency wallet tracking."""

    __tablename__ = "crypto_wallets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    blockchain = Column(String(50), nullable=False)  # ethereum, solana, etc.
    address = Column(String(255), nullable=False)
    label = Column(String(255))
    is_active = Column(Integer, default=1)  # Boolean
    last_checked = Column(DateTime)
    last_balance = Column(Float)
    last_balance_usd = Column(Float)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class CryptoPrice(Base):
    """Historical cryptocurrency price data."""

    __tablename__ = "crypto_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)  # ETH, SOL, etc.
    timestamp = Column(DateTime, nullable=False, index=True)
    price_usd = Column(Float, nullable=False)
    volume_24h = Column(Float)
    market_cap = Column(Float)
    source = Column(String(50))  # coingecko, coinmarketcap, etc.


class SessionStats(Base):
    """Aggregated session statistics."""

    __tablename__ = "session_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    platform = Column(String(100), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime)
    duration_minutes = Column(Integer)
    stakes = Column(String(50))
    hands_played = Column(Integer, default=0)
    hands_won = Column(Integer, default=0)
    total_won = Column(Float, default=0.0)
    total_lost = Column(Float, default=0.0)
    net_profit = Column(Float, default=0.0)
    bb_per_100 = Column(Float)  # Big blinds per 100 hands
    vpip_avg = Column(Float)
    pfr_avg = Column(Float)
    aggression_factor_avg = Column(Float)
    showdown_win_rate = Column(Float)
    all_in_count = Column(Integer, default=0)
    biggest_pot = Column(Float)
    biggest_win = Column(Float)
    biggest_loss = Column(Float)
    notes = Column(Text)
    mental_state = Column(String(50))  # calm, tilted, focused, etc.
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database initialization
def init_db(database_url: str = "sqlite:///poker_grind.db"):
    """Initialize the database with all tables."""
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session_maker(database_url: str = "sqlite:///poker_grind.db"):
    """Get a session maker for database operations."""
    engine = create_engine(database_url, echo=False)
    return sessionmaker(bind=engine)
