"""
Calendar API Routes
Calendar event management
"""
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.calendar_event import CalendarEvent
from app.api.v1.auth import get_current_user


router = APIRouter()


# ==================== Pydantic Schemas ====================

class CalendarEventCreate(BaseModel):
    """Calendar event create schema."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: List[str] = Field(default_factory=list)
    recurrence: Optional[str] = None
    reminder_minutes: Optional[int] = None


class CalendarEventUpdate(BaseModel):
    """Calendar event update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    recurrence: Optional[str] = None
    reminder_minutes: Optional[int] = None


class CalendarEventResponse(BaseModel):
    """Calendar event response schema."""
    id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: List[str] = []
    external_id: Optional[str] = None
    sync_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AvailabilityRequest(BaseModel):
    """Check availability request."""
    start_date: datetime
    end_date: datetime


class AvailabilityResponse(BaseModel):
    """Availability response."""
    available_slots: List[dict]
    busy_slots: List[dict]


# ==================== API Routes ====================

@router.get("/events", response_model=List[CalendarEventResponse])
async def list_events(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List calendar events."""
    query = CalendarEvent.query.filter(
        CalendarEvent.user_id == current_user.id
    )
    
    if start_date:
        query = query.filter(CalendarEvent.start_time >= start_date)
    if end_date:
        query = query.filter(CalendarEvent.end_time <= end_date)
    
    events = query.order_by(CalendarEvent.start_time).all()
    
    return events


@router.post("/events", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: CalendarEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new calendar event."""
    # Validate time
    if event.end_time <= event.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Create event
    db_event = CalendarEvent(
        user_id=current_user.id,
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        attendees=event.attendees,
        recurrence=event.recurrence,
        reminder_minutes=event.reminder_minutes,
        sync_status="pending"
    )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    return db_event


@router.get("/events/{event_id}", response_model=CalendarEventResponse)
async def get_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific calendar event."""
    from sqlalchemy.dialects.postgresql import UUID
    
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == UUID(event_id),
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return event


@router.put("/events/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: str,
    event: CalendarEventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a calendar event."""
    from sqlalchemy.dialects.postgresql import UUID
    
    db_event = db.query(CalendarEvent).filter(
        CalendarEvent.id == UUID(event_id),
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Update fields
    if event.title is not None:
        db_event.title = event.title
    if event.description is not None:
        db_event.description = event.description
    if event.start_time is not None:
        db_event.start_time = event.start_time
    if event.end_time is not None:
        db_event.end_time = event.end_time
    if event.location is not None:
        db_event.location = event.location
    if event.attendees is not None:
        db_event.attendees = event.attendees
    if event.recurrence is not None:
        db_event.recurrence = event.recurrence
    if event.reminder_minutes is not None:
        db_event.reminder_minutes = event.reminder_minutes
    
    db_event.sync_status = "pending"
    db.commit()
    db.refresh(db_event)
    
    return db_event


@router.delete("/events/{event_id}")
async def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a calendar event."""
    from sqlalchemy.dialects.postgresql import UUID
    
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == UUID(event_id),
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    db.delete(event)
    db.commit()
    
    return {"message": "Event deleted"}


@router.post("/availability", response_model=AvailabilityResponse)
async def check_availability(
    request: AvailabilityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check calendar availability in a time range."""
    # Get existing events in the time range
    events = db.query(CalendarEvent).filter(
        CalendarEvent.user_id == current_user.id,
        CalendarEvent.start_time >= request.start_date,
        CalendarEvent.end_time <= request.end_date
    ).all()
    
    # Build busy slots
    busy_slots = [
        {
            "start": e.start_time.isoformat(),
            "end": e.end_time.isoformat(),
            "title": e.title
        }
        for e in events
    ]
    
    # Calculate available slots (simplified)
    available_slots = []
    current = request.start_date
    
    while current < request.end_date:
        is_busy = False
        for event in events:
            if event.start_time <= current < event.end_time:
                is_busy = True
                break
        
        if not is_busy:
            slot_end = min(current + timedelta(hours=1), request.end_date)
            available_slots.append({
                "start": current.isoformat(),
                "end": slot_end.isoformat()
            })
        
        current += timedelta(hours=1)
    
    return AvailabilityResponse(
        available_slots=available_slots,
        busy_slots=busy_slots
    )