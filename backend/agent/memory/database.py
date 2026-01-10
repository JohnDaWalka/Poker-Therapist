"""Database models for Therapy Rex."""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TiltProfile(Base):
    """Tilt profile for a user."""

    __tablename__ = "tilt_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    
    # A-game characteristics
    a_game_characteristics = Column(JSON)
    
    # Red flag conditions
    red_flags = Column(JSON)
    
    # Recurring patterns
    recurring_patterns = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Session(Base):
    """Therapy session record."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Session metadata
    session_type = Column(String, nullable=False)  # triage, deep, warmup, debrief
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    
    # Emotional state
    emotion = Column(String)
    intensity = Column(Integer)
    body_sensation = Column(String)
    still_playing = Column(Boolean)
    
    # Results
    severity = Column(Integer)
    patterns_detected = Column(JSON)
    ai_guidance = Column(Text)
    action_plan = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class MentalGameKPI(Base):
    """Mental game KPI tracking."""

    __tablename__ = "mental_game_kpis"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    
    # KPI metrics
    tilt_frequency = Column(Float)  # sessions per week
    average_severity = Column(Float)  # 1-10
    recovery_time = Column(Float)  # minutes
    stop_loss_adherence = Column(Float)  # percentage
    a_game_percentage = Column(Float)  # percentage of time in A-game
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class Playbook(Base):
    """Personal mental game playbook."""

    __tablename__ = "playbooks"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, nullable=False, index=True)
    
    # Pre-session
    pre_session_script = Column(Text)
    warmup_routine = Column(JSON)
    
    # In-session
    in_session_protocol = Column(JSON)
    break_triggers = Column(JSON)
    
    # Post-session
    post_session_template = Column(Text)
    review_questions = Column(JSON)
    
    # Personal rules
    personal_rules = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HandHistory(Base):
    """Stored poker hand history, optionally linked to on-chain proof.

    This is designed for post-session review flows where Therapy Rex can fetch
    a session's hands from the DB instead of relying on pasted hand histories.
    """

    __tablename__ = "hand_histories"

    id = Column(Integer, primary_key=True)

    # Ownership / grouping
    user_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=True, index=True)

    # Poker metadata
    site = Column(String, default="CoinPoker")
    hand_id = Column(String, nullable=True, index=True)
    date_played = Column(DateTime, nullable=True)
    game_variant = Column(String, nullable=True)
    stakes = Column(String, nullable=True)

    # Parsed details (best-effort)
    player_name = Column(String, nullable=True)
    position = Column(String, nullable=True)
    hole_cards = Column(String, nullable=True)
    board = Column(String, nullable=True)
    actions = Column(Text, nullable=True)
    won_amount = Column(Float, nullable=True)
    pot_size = Column(Float, nullable=True)

    # Raw / traceability
    raw_text = Column(Text, nullable=False)
    source = Column(String, default="coinpoker_export")

    # Optional blockchain linkage (CoinPoker often exposes tx/hash references)
    tx_hash = Column(String, nullable=True, index=True)
    chain_id = Column(String, nullable=True)
    block_number = Column(Integer, nullable=True)
    tx_status = Column(Integer, nullable=True)  # 1 success, 0 fail
    verified = Column(Boolean, default=False)

    # CoinPoker provably-fair / RNG proof (not necessarily on-chain)
    rng_phrase = Column(String, nullable=True)
    rng_combined_seed_hash = Column(String, nullable=True)
    rng_verified = Column(Boolean, default=False)
    rng_verification = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
