"""
Contact Model with relationship mapping
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Contact(Base):
    """Contact model with role relationships."""
    
    __tablename__ = "contacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    
    # Role relationships: lawyer, assistant, accountant, etc.
    # Stored as JSON array of role labels
    relationships = Column(JSON, default=list)
    
    # Additional metadata (renamed to avoid SQLAlchemy conflict)
    extra_data = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        # Unique constraint on user_id + email (if email is not null)
    )
    
    # Relationships
    user = relationship("User", back_populates="contacts")
    
    def __repr__(self):
        return f"<Contact(id={self.id}, name={self.name})>"