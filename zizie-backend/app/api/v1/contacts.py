"""
Contacts API Routes
Contact management with role relationships
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.contact import Contact
from app.api.v1.auth import get_current_user


router = APIRouter()


# ==================== Pydantic Schemas ====================

class ContactCreate(BaseModel):
    """Contact create schema."""
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    relationships: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class ContactUpdate(BaseModel):
    """Contact update schema."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    relationships: Optional[List[str]] = None
    metadata: Optional[dict] = None


class ContactResponse(BaseModel):
    """Contact response schema."""
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    relationships: List[str] = []
    metadata: dict = {}
    created_at: str
    
    class Config:
        from_attributes = True


class RoleAssignmentRequest(BaseModel):
    """Request to assign role to contact."""
    role: str = Field(..., min_length=1)
    action: str = Field(default="add")  # add or remove


# ==================== API Routes ====================

@router.get("/", response_model=List[ContactResponse])
async def list_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all contacts for the user."""
    contacts = db.query(Contact).filter(
        Contact.user_id == current_user.id
    ).all()
    
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new contact."""
    # Check for duplicate email
    if contact.email:
        existing = db.query(Contact).filter(
            Contact.user_id == current_user.id,
            Contact.email == contact.email
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contact with this email already exists"
            )
    
    # Create contact
    db_contact = Contact(
        user_id=current_user.id,
        name=contact.name,
        email=contact.email,
        phone=contact.phone,
        relationships=contact.relationships,
        metadata=contact.metadata
    )
    
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    
    return db_contact


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific contact."""
    from sqlalchemy.dialects.postgresql import UUID
    
    contact = db.query(Contact).filter(
        Contact.id == UUID(contact_id),
        Contact.user_id == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: str,
    contact: ContactUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a contact."""
    from sqlalchemy.dialects.postgresql import UUID
    
    db_contact = db.query(Contact).filter(
        Contact.id == UUID(contact_id),
        Contact.user_id == current_user.id
    ).first()
    
    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Update fields
    if contact.name is not None:
        db_contact.name = contact.name
    if contact.email is not None:
        db_contact.email = contact.email
    if contact.phone is not None:
        db_contact.phone = contact.phone
    if contact.relationships is not None:
        db_contact.relationships = contact.relationships
    if contact.metadata is not None:
        db_contact.metadata = contact.metadata
    
    db.commit()
    db.refresh(db_contact)
    
    return db_contact


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a contact."""
    from sqlalchemy.dialects.postgresql import UUID
    
    contact = db.query(Contact).filter(
        Contact.id == UUID(contact_id),
        Contact.user_id == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    db.delete(contact)
    db.commit()
    
    return {"message": "Contact deleted"}


@router.get("/resolve/{role}")
async def resolve_role(
    role: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve a role to a contact."""
    # Search for contact with the given role
    # Using SQLAlchemy's any for array column
    contact = db.query(Contact).filter(
        Contact.user_id == current_user.id,
        Contact.relationships.any(role)
    ).first()
    
    if not contact:
        return {
            "role": role,
            "found": False,
            "message": f"No contact found with role '{role}'"
        }
    
    return {
        "role": role,
        "found": True,
        "contact": {
            "id": str(contact.id),
            "name": contact.name,
            "email": contact.email,
            "phone": contact.phone
        }
    }


@router.post("/{contact_id}/assign-role", response_model=ContactResponse)
async def assign_role(
    contact_id: str,
    request: RoleAssignmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign a role to a contact."""
    from sqlalchemy.dialects.postgresql import UUID
    
    contact = db.query(Contact).filter(
        Contact.id == UUID(contact_id),
        Contact.user_id == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Get current relationships
    relationships = list(contact.relationships) if contact.relationships else []
    
    if request.action == "add" and request.role not in relationships:
        relationships.append(request.role)
    elif request.action == "remove" and request.role in relationships:
        relationships.remove(request.role)
    
    contact.relationships = relationships
    db.commit()
    db.refresh(contact)
    
    return contact


# ==================== Predefined Roles ====================

# These are the standard roles users can assign to contacts
PREDEFINED_ROLES = {
    "professional": ["lawyer", "accountant", "doctor", "therapist", "financial_advisor"],
    "personal": ["spouse", "partner", "mother", "father", "sibling", "friend"],
    "work": ["boss", "manager", "colleague", "team_lead", "hr", "assistant"],
    "service": ["landlord", "mechanic", "dentist", "trainer"]
}


@router.get("/roles/available")
async def get_available_roles():
    """Get available role categories."""
    return PREDEFINED_ROLES