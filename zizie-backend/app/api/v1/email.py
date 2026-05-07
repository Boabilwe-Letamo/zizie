"""
Email API Routes
Email read, draft, and send functionality
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user


router = APIRouter()


# ==================== Pydantic Schemas ====================

class EmailCreate(BaseModel):
    """Email create schema (for sending)."""
    to: List[EmailStr] = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    reply_to: Optional[str] = None


class EmailDraftCreate(BaseModel):
    """Email draft create schema."""
    to: List[EmailStr] = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    body: str
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None


class EmailDraftUpdate(BaseModel):
    """Email draft update schema."""
    to: Optional[List[EmailStr]] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None


class EmailResponse(BaseModel):
    """Email response schema."""
    id: str
    to: List[str]
    from_email: str
    subject: str
    body: str
    cc: List[str] = []
    bcc: List[str] = []
    is_read: bool = False
    is_draft: bool = False
    is_sent: bool = False
    created_at: str


class EmailSendConfirmation(BaseModel):
    """Email send confirmation response."""
    to: List[str]
    subject: str
    body: str
    needs_confirmation: bool = True


# In-memory storage for drafts (replace with database in production)
email_drafts = {}
email_sent = []


# ==================== API Routes ====================

@router.get("/messages", response_model=List[EmailResponse])
async def list_messages(
    folder: str = "inbox",
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List email messages."""
    # In production, fetch from Gmail API
    # For MVP, return mock data
    
    messages = []
    
    if folder == "sent":
        messages = email_sent[-limit:] if email_sent else []
    
    return messages


@router.get("/messages/{message_id}", response_model=EmailResponse)
async def get_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific email message."""
    # In production, fetch from Gmail API
    
    # Check drafts
    if message_id in email_drafts:
        return email_drafts[message_id]
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Message not found"
    )


@router.post("/draft", response_model=EmailResponse, status_code=status.HTTP_201_CREATED)
async def create_draft(
    draft: EmailDraftCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create an email draft."""
    import uuid
    
    draft_id = str(uuid.uuid4())
    
    email_drafts[draft_id] = EmailResponse(
        id=draft_id,
        to=draft.to,
        from_email=current_user.email,
        subject=draft.subject,
        body=draft.body,
        cc=draft.cc or [],
        bcc=draft.bcc or [],
        is_draft=True,
        created_at=""
    ).model_dump()
    
    return email_drafts[draft_id]


@router.put("/draft/{draft_id}", response_model=EmailResponse)
async def update_draft(
    draft_id: str,
    draft: EmailDraftUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an email draft."""
    if draft_id not in email_drafts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )
    
    existing = email_drafts[draft_id]
    
    if draft.to is not None:
        existing["to"] = draft.to
    if draft.subject is not None:
        existing["subject"] = draft.subject
    if draft.body is not None:
        existing["body"] = draft.body
    if draft.cc is not None:
        existing["cc"] = draft.cc
    if draft.bcc is not None:
        existing["bcc"] = draft.bcc
    
    return existing


@router.delete("/draft/{draft_id}")
async def delete_draft(
    draft_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an email draft."""
    if draft_id not in email_drafts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )
    
    del email_drafts[draft_id]
    
    return {"message": "Draft deleted"}


@router.post("/send", response_model=EmailResponse)
async def send_email(
    email: EmailCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send an email (requires confirmation in voice flow)."""
    import uuid
    
    # In production, send via Gmail API or SMTP
    
    message_id = str(uuid.uuid4())
    
    # Check if user has voice verification completed
    # In production, verify from voice session
    
    # Create email record
    email_record = EmailResponse(
        id=message_id,
        to=email.to,
        from_email=current_user.email,
        subject=email.subject,
        body=email.body,
        cc=email.cc or [],
        bcc=email.bcc or [],
        is_sent=True,
        created_at=""
    )
    
    # Add to sent folder
    email_sent.append(email_record.model_dump())
    
    return email_record


@router.post("/send/confirm")
async def confirm_send(
    draft_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Confirm and send a draft email."""
    if draft_id not in email_drafts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )
    
    draft = email_drafts[draft_id]
    
    # Mark as sent
    draft["is_sent"] = True
    draft["is_draft"] = False
    email_sent.append(draft)
    
    # Remove from drafts
    del email_drafts[draft_id]
    
    return {"message": "Email sent successfully", "message_id": draft_id}


@router.post("/read-back")
async def read_back_email(
    email_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Read back an email for confirmation."""
    email_data = None
    
    # Check drafts
    if email_id in email_drafts:
        email_data = email_drafts[email_id]
    # Check sent
    else:
        for sent in email_sent:
            if sent["id"] == email_id:
                email_data = sent
                break
    
    if not email_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # Format for voice reading
    return {
        "to": ", ".join(email_data["to"]),
        "subject": email_data["subject"],
        "body": email_data["body"],
        "message": f"To: {', '.join(email_data['to'])}"
                 f"Subject: {email_data['subject']}"
                 f"Body: {email_data['body']}"
    }