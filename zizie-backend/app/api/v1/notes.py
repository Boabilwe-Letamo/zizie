"""
Notes API Routes
Notes management
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.note import Note
from app.api.v1.auth import get_current_user


router = APIRouter()


# ==================== Pydantic Schemas ====================

class NoteCreate(BaseModel):
    """Note create schema."""
    title: Optional[str] = None
    content: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)
    linked_entities: dict = Field(default_factory=dict)


class NoteUpdate(BaseModel):
    """Note update schema."""
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    linked_entities: Optional[dict] = None


class NoteResponse(BaseModel):
    """Note response schema."""
    id: str
    title: Optional[str] = None
    content: str
    tags: List[str] = []
    linked_entities: dict = {}
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


# ==================== API Routes ====================

@router.get("/", response_model=List[NoteResponse])
async def list_notes(
    tag: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List notes for the user."""
    query = Note.query.filter(Note.user_id == current_user.id)
    
    if tag:
        query = query.filter(Note.tags.any(tag))
    
    notes = query.order_by(Note.updated_at.desc()).limit(limit).all()
    
    return notes


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new note."""
    db_note = Note(
        user_id=current_user.id,
        title=note.title,
        content=note.content,
        tags=note.tags,
        linked_entities=note.linked_entities
    )
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    return db_note


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific note."""
    from sqlalchemy.dialects.postgresql import UUID
    
    note = db.query(Note).filter(
        Note.id == UUID(note_id),
        Note.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    note: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a note."""
    from sqlalchemy.dialects.postgresql import UUID
    
    db_note = db.query(Note).filter(
        Note.id == UUID(note_id),
        Note.user_id == current_user.id
    ).first()
    
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Update fields
    if note.title is not None:
        db_note.title = note.title
    if note.content is not None:
        db_note.content = note.content
    if note.tags is not None:
        db_note.tags = note.tags
    if note.linked_entities is not None:
        db_note.linked_entities = note.linked_entities
    
    db.commit()
    db.refresh(db_note)
    
    return db_note


@router.delete("/{note_id}")
async def delete_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a note."""
    from sqlalchemy.dialects.postgresql import UUID
    
    note = db.query(Note).filter(
        Note.id == UUID(note_id),
        Note.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    db.delete(note)
    db.commit()
    
    return {"message": "Note deleted"}


@router.get("/search", response_model=List[NoteResponse])
async def search_notes(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search notes by content."""
    notes = db.query(Note).filter(
        Note.user_id == current_user.id,
        Note.content.ilike(f"%{q}%")
    ).all()
    
    return notes