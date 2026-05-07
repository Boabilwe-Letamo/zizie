"""
Reminders API Routes
Reminders management
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.reminder import Reminder
from app.api.v1.auth import get_current_user


router = APIRouter()


# ==================== Pydantic Schemas ====================

class ReminderCreate(BaseModel):
    """Reminder create schema."""
    content: str = Field(..., min_length=1, max_length=1000)
    due_date: Optional[str] = None  # ISO format date
    due_time: Optional[str] = None  # ISO format datetime
    relative_time: Optional[str] = None  # e.g., "in 30 minutes"
    repeat_pattern: Optional[str] = None  # daily, weekly, monthly
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None


class ReminderUpdate(BaseModel):
    """Reminder update schema."""
    content: Optional[str] = None
    due_date: Optional[str] = None
    due_time: Optional[str] = None
    relative_time: Optional[str] = None
    repeat_pattern: Optional[str] = None
    status: Optional[str] = None


class ReminderResponse(BaseModel):
    """Reminder response schema."""
    id: str
    content: str
    due_date: Optional[str] = None
    due_time: Optional[str] = None
    relative_time: Optional[str] = None
    repeat_pattern: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    status: str
    completed_at: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True


# ==================== API Routes ====================

@router.get("/", response_model=List[ReminderResponse])
async def list_reminders(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List reminders for the user."""
    query = Reminder.query.filter(Reminder.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Reminder.status == status_filter)
    
    reminders = query.order_by(Reminder.due_time.asc()).all()
    
    return reminders


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new reminder."""
    # Parse due time
    due_date = None
    due_time = None
    
    if reminder.due_date:
        due_date = datetime.fromisoformat(reminder.due_date).date()
    if reminder.due_time:
        due_time = datetime.fromisoformat(reminder.due_time)
    
    # Parse entity_id
    entity_id = None
    if reminder.entity_id:
        from uuid import UUID
        entity_id = UUID(reminder.entity_id)
    
    db_reminder = Reminder(
        user_id=current_user.id,
        content=reminder.content,
        due_date=due_date,
        due_time=due_time,
        relative_time=reminder.relative_time,
        repeat_pattern=reminder.repeat_pattern,
        entity_type=reminder.entity_type,
        entity_id=entity_id,
        status="pending"
    )
    
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    
    return db_reminder


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific reminder."""
    from sqlalchemy.dialects.postgresql import UUID
    
    reminder = db.query(Reminder).filter(
        Reminder.id == UUID(reminder_id),
        Reminder.user_id == current_user.id
    ).first()
    
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    return reminder


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: str,
    reminder: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a reminder."""
    from sqlalchemy.dialects.postgresql import UUID
    
    db_reminder = db.query(Reminder).filter(
        Reminder.id == UUID(reminder_id),
        Reminder.user_id == current_user.id
    ).first()
    
    if not db_reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    # Update fields
    if reminder.content is not None:
        db_reminder.content = reminder.content
    if reminder.due_date is not None:
        db_reminder.due_date = datetime.fromisoformat(reminder.due_date).date()
    if reminder.due_time is not None:
        db_reminder.due_time = datetime.fromisoformat(reminder.due_time)
    if reminder.relative_time is not None:
        db_reminder.relative_time = reminder.relative_time
    if reminder.repeat_pattern is not None:
        db_reminder.repeat_pattern = reminder.repeat_pattern
    if reminder.status is not None:
        db_reminder.status = reminder.status
    
    db.commit()
    db.refresh(db_reminder)
    
    return db_reminder


@router.delete("/{reminder_id}")
async def delete_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a reminder."""
    from sqlalchemy.dialects.postgresql import UUID
    
    reminder = db.query(Reminder).filter(
        Reminder.id == UUID(reminder_id),
        Reminder.user_id == current_user.id
    ).first()
    
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    db.delete(reminder)
    db.commit()
    
    return {"message": "Reminder deleted"}


@router.post("/{reminder_id}/complete", response_model=ReminderResponse)
async def complete_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a reminder as completed."""
    from sqlalchemy.dialects.postgresql import UUID
    
    reminder = db.query(Reminder).filter(
        Reminder.id == UUID(reminder_id),
        Reminder.user_id == current_user.id
    ).first()
    
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    reminder.status = "completed"
    reminder.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(reminder)
    
    return reminder


@router.post("/{reminder_id}/snooze")
async def snooze_reminder(
    reminder_id: str,
    minutes: int = 15,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Snooze a reminder."""
    from sqlalchemy.dialects.postgresql import UUID
    from datetime import timedelta
    
    reminder = db.query(Reminder).filter(
        Reminder.id == UUID(reminder_id),
        Reminder.user_id == current_user.id
    ).first()
    
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    # Snooze by given minutes
    new_due = datetime.utcnow() + timedelta(minutes=minutes)
    reminder.due_time = new_due
    reminder.status = "snoozed"
    
    db.commit()
    
    return {
        "message": f"Reminder snoozed for {minutes} minutes",
        "new_due": new_due.isoformat()
    }