"""
Calendar Event Model
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class CalendarEvent(Base):
    """Calendar event model."""
    
    __tablename__ = "calendar_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title = Column(String(500), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String(500))
    
    # Attendees (array of email addresses)
    attendees = Column(JSON, default=list)
    
    # External calendar ID (Google Calendar ID)
    external_id = Column(String(255))
    
    # Sync status
    sync_status = Column(String(50), default="pending")
    # Values: pending, synced, failed
    
    # Recurrence (RRULE format)
    recurrence = Column(String(500))
    
    # Reminder
    reminder_minutes = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="calendar_events")
    
    def __repr__(self):
        return f"<CalendarEvent(id={self.id}, title={self.title})>"