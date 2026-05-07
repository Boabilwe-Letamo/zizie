"""
Voice Session Model - Track voice command sessions
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class VoiceSession(Base):
    """Voice session for audit trail."""
    
    __tablename__ = "voice_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("voice_profiles.id", ondelete="SET NULL")
    )
    
    # Session timing
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    
    # Session metadata
    commands_count = Column(Integer, default=0)
    commands = Column(JSON, default=list)
    
    # Status: active, completed, failed
    status = Column(String(50), default="active")
    
    # Error info if any
    error = Column(String(500))
    
    # Relationships
    user = relationship("User", back_populates="voice_profiles")
    profile = relationship("VoiceProfile", back_populates="sessions")
    audit_logs = relationship("AuditLog", back_populates="session")
    
    def __repr__(self):
        return f"<VoiceSession(id={self.id}, user_id={self.user_id})>"