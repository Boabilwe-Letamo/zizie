"""
Audit Log Model - Track all actions for security
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class AuditLog(Base):
    """Audit log for security tracking."""
    
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("voice_sessions.id", ondelete="SET NULL")
    )
    
    # Action details
    action_type = Column(String(100), nullable=False)
    # Values: voice_verify, email_send, calendar_create, etc.
    
    action_details = Column(JSON, default=dict)
    
    # Result status: success, failure, blocked
    result = Column(String(50))
    
    # IP address (if available)
    ip_address = Column(String(45))
    
    # User agent
    user_agent = Column(String(500))
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("VoiceSession", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action_type={self.action_type})>"