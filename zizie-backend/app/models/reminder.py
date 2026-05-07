"""
Reminder Model
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Reminder(Base):
    """Reminder model."""
    
    __tablename__ = "reminders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    content = Column(String(1000), nullable=False)
    
    # Due date/time
    due_date = Column(Date)
    due_time = Column(DateTime)
    
    # Or relative time (e.g., "in 30 minutes")
    relative_time = Column(String(50))
    
    # Repeat pattern: daily, weekly, monthly
    repeat_pattern = Column(String(50))
    
    # Associated entity (contact, event, note)
    entity_type = Column(String(50))
    entity_id = Column(UUID(as_uuid=True))
    
    # Status
    status = Column(String(50), default="pending")
    # Values: pending, completed, snoozed, dismissed
    
    # Completion info
    completed_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="reminders")
    
    def __repr__(self):
        return f"<Reminder(id={self.id}, content={self.content})>"