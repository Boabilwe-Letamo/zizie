"""
User Model
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Boolean, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    phone = Column(String(50))
    
    # Language preference
    language = Column(String(10), default="en")
    
    # Device identifier
    device_id = Column(String(255))
    
    # OAuth providers (Google, Apple, etc.)
    providers = Column(JSON, default=dict)
    
    # User settings
    settings = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    contacts = relationship("Contact", back_populates="user", cascade="all, delete-orphan")
    voice_profiles = relationship(
        "VoiceProfile",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    calendar_events = relationship(
        "CalendarEvent",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship(
        "Reminder",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"