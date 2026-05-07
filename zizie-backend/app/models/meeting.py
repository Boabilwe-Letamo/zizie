"""
Meeting Model - Video conferencing integration
"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean, Text, Enum
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class MeetingPlatform(enum.Enum):
    """Video meeting platforms."""
    GOOGLE_MEET = "google_meet"
    ZOOM = "zoom"
    MICROSOFT_TEAMS = "microsoft_teams"


class Meeting(Base):
    """Video meeting model."""
    
    __tablename__ = "meetings"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Meeting details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Timing
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    
    # Platform
    platform = Column(Enum(MeetingPlatform), nullable=False, default=MeetingPlatform.GOOGLE_MEET)
    
    # Meeting link
    meeting_url = Column(String(500), nullable=True)
    meeting_id = Column(String(255), nullable=True)  # Platform-specific ID
    
    # Password/join info
    join_info = Column(Text, nullable=True)
    password = Column(String(100), nullable=True)
    
    # Status
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships (if using external calendar)
    calendar_event_id = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<Meeting {self.id}: {self.title} ({self.platform.value})>"