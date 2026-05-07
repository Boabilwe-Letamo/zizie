"""
Voice Profile Model - Biometric voice enrollment
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from sqlalchemy.orm import relationship

from app.db.session import Base


class VoiceProfile(Base):
    """Voice profile for biometric authentication."""
    
    __tablename__ = "voice_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    profile_name = Column(String(100), nullable=False)
    
    # Permission level (0-4)
    permission_level = Column(Integer, default=1)
    
    # Voice embedding stored as bytes (for biometric)
    # For SQLite, use LargeBinary; for PostgreSQL, use BYTEA
    voice_embedding = Column(LargeBinary, nullable=False)
    
    # Salt for encryption
    embedding_salt = Column(String(64), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Enrollment info
    enrollment_complete = Column(Boolean, default=False)
    enrollment_samples = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="voice_profiles")
    sessions = relationship("VoiceSession", back_populates="profile")
    
    def __repr__(self):
        return f"<VoiceProfile(id={self.id}, name={self.profile_name})>"