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
    """Logged poker hand histories (PokerTracker 4.18.16)."""

    __tablename__ = "hand_histories"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    source = Column(String, default="PokerTracker")
    source_version = Column(String, default="4.18.16")
    hand_id = Column(String, nullable=True, index=True)
    hand_history = Column(Text, nullable=False)
    emotional_context = Column(Text)
    gto_analysis = Column(Text)
    meta_context = Column(Text)
    hud_insights = Column(Text)
    models = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
