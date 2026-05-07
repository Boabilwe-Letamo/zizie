"""
Meeting API - Video conferencing endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

from app.db.session import get_db
from app.models.meeting import Meeting, MeetingPlatform as MeetingModel
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.services.meetings import (
    MeetingServiceFactory,
    MeetingDetails,
)


router = APIRouter(prefix="/api/v1/meetings", tags=["meetings"])


# Schemas
class MeetingCreate(BaseModel):
    """Create meeting request."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    platform: str = Field(default="google_meet")
    attendees: Optional[List[str]] = None


class MeetingUpdate(BaseModel):
    """Update meeting request."""
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class MeetingResponse(BaseModel):
    """Meeting response."""
    id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    platform: str
    meeting_url: Optional[str]
    meeting_id: Optional[str]
    join_info: Optional[str]
    password: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=MeetingResponse)
async def create_meeting(
    meeting: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new video meeting."""
    try:
        platform = MeetingModel(meeting.platform)
    except ValueError:
        raise HTTPException(400, "Invalid platform. Use: google_meet, zoom, or microsoft_teams")
    
    # Get the meeting service
    try:
        meeting_service = MeetingServiceFactory.get_service(meeting.platform)
    except ValueError as e:
        raise HTTPException(400, str(e))
    
    # Create the meeting
    details = MeetingDetails(
        title=meeting.title,
        description=meeting.description,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        attendees=meeting.attendees,
    )
    
    result = await meeting_service.create_meeting(details)
    
    if not result.success:
        raise HTTPException(500, result.error or "Failed to create meeting")
    
    # Save to database
    db_meeting = Meeting(
        user_id=current_user.id,
        title=meeting.title,
        description=meeting.description,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        duration_minutes=int((meeting.end_time - meeting.start_time).total_seconds() / 60),
        platform=platform,
        meeting_url=result.meeting_url,
        meeting_id=result.meeting_id,
        join_info=result.join_info,
        password=result.password,
    )
    
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    
    return db_meeting


@router.get("/", response_model=List[MeetingResponse])
async def list_meetings(
    skip: int = 0,
    limit: int = 50,
    platform: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's meetings."""
    query = db.query(Meeting).filter(Meeting.user_id == current_user.id)
    
    if platform:
        try:
            platform_enum = MeetingModel(platform)
            query = query.filter(Meeting.platform == platform_enum)
        except ValueError:
            pass
    
    meetings = query.order_by(Meeting.start_time.desc()).offset(skip).limit(limit).all()
    return meetings


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get meeting by ID."""
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.user_id == current_user.id,
    ).first()
    
    if not meeting:
        raise HTTPException(404, "Meeting not found")
    
    return meeting


@router.patch("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: int,
    meeting: MeetingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a meeting."""
    db_meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.user_id == current_user.id,
    ).first()
    
    if not db_meeting:
        raise HTTPException(404, "Meeting not found")
    
    # Update fields
    if meeting.title is not None:
        db_meeting.title = meeting.title
    if meeting.description is not None:
        db_meeting.description = meeting.description
    if meeting.start_time is not None:
        db_meeting.start_time = meeting.start_time
    if meeting.end_time is not None:
        db_meeting.end_time = meeting.end_time
    
    db_meeting.duration_minutes = int(
        (db_meeting.end_time - db_meeting.start_time).total_seconds() / 60
    )
    
    db.commit()
    db.refresh(db_meeting)
    
    return db_meeting


@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a meeting."""
    db_meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.user_id == current_user.id,
    ).first()
    
    if not db_meeting:
        raise HTTPException(404, "Meeting not found")
    
    # Try to delete from platform
    try:
        platform_str = db_meeting.platform.value
        meeting_service = MeetingServiceFactory.get_service(platform_str)
        await meeting_service.delete_meeting(db_meeting.meeting_id)
    except Exception:
        pass  # Ignore errors
    
    db.delete(db_meeting)
    db.commit()
    
    return {"message": "Meeting deleted"}


# Quick create endpoints
@router.post("/quick")
async def quick_create_meeting(
    title: str,
    minutes: int = 60,
    platform: str = "google_meet",
    now: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Quick create a meeting (simplified)."""
    from datetime import timedelta
    
    start_time = datetime.now() if now else datetime.now() + timedelta(hours=1)
    end_time = start_time + timedelta(minutes=minutes)
    
    meeting = MeetingCreate(
        title=title,
        start_time=start_time,
        end_time=end_time,
        platform=platform,
    )
    
    # Get service
    try:
        meeting_service = MeetingServiceFactory.get_service(platform)
    except ValueError as e:
        raise HTTPException(400, str(e))
    
    # Create
    details = MeetingDetails(
        title=title,
        start_time=start_time,
        end_time=end_time,
    )
    
    result = await meeting_service.create_meeting(details)
    
    if not result.success:
        raise HTTPException(500, result.error)
    
    return {
        "title": title,
        "platform": platform,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "meeting_url": result.meeting_url,
        "meeting_id": result.meeting_id,
        "join_info": result.join_info,
    }