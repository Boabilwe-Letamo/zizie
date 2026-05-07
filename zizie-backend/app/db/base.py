"""
Database Base - Empty base for Alembic migrations
"""
from app.db.session import Base

# Import all models to register them with Base
from app.models.user import User
from app.models.contact import Contact
from app.models.voice_profile import VoiceProfile
from app.models.calendar_event import CalendarEvent
from app.models.note import Note
from app.models.reminder import Reminder
from app.models.voice_session import VoiceSession
from app.models.audit_log import AuditLog