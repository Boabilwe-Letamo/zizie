"""
Note Model
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Note(Base):
    """Note model."""
    
    __tablename__ = "notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title = Column(String(500))
    content = Column(Text, nullable=False)
    
    # Tags for organization
    tags = Column(JSON, default=list)
    
    # Linked entities (calendar_event_id, contact_id, etc.)
    linked_entities = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notes")
    
    def __repr__(self):
        return f"<Note(id={self.id}, title={self.title})>"