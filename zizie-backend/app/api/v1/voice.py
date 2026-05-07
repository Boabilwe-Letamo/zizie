"""
Voice API Routes
Voice enrollment, verification, streaming
"""
import base64
import json
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import SecurityUtils
from app.db.session import get_db
from app.models.user import User
from app.models.voice_profile import VoiceProfile
from app.models.voice_session import VoiceSession
from app.models.audit_log import AuditLog
from app.api.v1.auth import get_current_user


router = APIRouter()


# ==================== Pydantic Schemas ====================

class VoiceEnrollmentStartRequest(BaseModel):
    """Request to start voice enrollment."""
    profile_name: str = Field(..., min_length=1, max_length=100)


class VoiceEnrollmentCompleteRequest(BaseModel):
    """Request to complete voice enrollment."""
    enrollment_id: str


class VoiceVerifyRequest(BaseModel):
    """Request to verify voice."""
    audio_data: str = Field(..., description="Base64 encoded audio")
    session_id: Optional[str] = None


class VoiceVerifyResponse(BaseModel):
    """Voice verification response."""
    verified: bool
    profile_id: Optional[str] = None
    confidence: float = 0.0
    permission_level: int = 0
    requires_confirmation: bool = False


class VoiceProfileResponse(BaseModel):
    """Voice profile response."""
    id: str
    profile_name: str
    permission_level: int
    is_active: bool
    enrollment_complete: bool
    enrollment_samples: int
    last_used_at: Optional[datetime] = None


class VoiceSessionResponse(BaseModel):
    """Voice session response."""
    session_id: str
    commands_count: int
    status: str


# ==================== API Routes ====================

@router.post("/enroll", status_code=status.HTTP_201_CREATED)
async def start_voice_enrollment(
    request: VoiceEnrollmentStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start voice enrollment process."""
    # Generate enrollment ID
    enrollment_id = str(uuid.uuid4())
    
    # Generate salt for embedding encryption
    salt = SecurityUtils.generate_salt()
    
    # Create voice profile (pending enrollment)
    profile = VoiceProfile(
        id=uuid.uuid4(),
        user_id=current_user.id,
        profile_name=request.profile_name,
        permission_level=1,  # Default to basic
        voice_embedding=b'',  # Empty until enrollment complete
        embedding_salt=salt,
        enrollment_complete=False,
        enrollment_samples=0,
    )
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    # Generate challenge phrase for enrollment
    phrase, pattern = SecurityUtils.generate_voice_challenge()
    
    return {
        "enrollment_id": str(profile.id),
        "challenge_phrase": phrase,
        "challenge_pattern": pattern,
        "message": "Please speak the phrase above. You will need to record 5-10 samples."
    }


@router.post("/enroll/complete")
async def complete_voice_enrollment(
    request: VoiceEnrollmentCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete voice enrollment after collecting samples."""
    from sqlalchemy.dialects.postgresql import UUID
    
    # Get voice profile
    profile = db.query(VoiceProfile).filter(
        VoiceProfile.id == UUID(request.enrollment_id),
        VoiceProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    if profile.enrollment_complete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enrollment already completed"
        )
    
    if profile.enrollment_samples < settings.VOICE_ENROLLMENT_SAMPLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Need {settings.VOICE_ENROLLMENT_SAMPLES} samples, have {profile.enrollment_samples}"
        )
    
    # Mark enrollment complete
    profile.enrollment_complete = True
    profile.is_active = True
    
    db.commit()
    
    return {
        "message": "Voice enrollment completed successfully",
        "profile_id": str(profile.id)
    }


@router.post("/enroll/sample")
async def add_enrollment_sample(
    audio_data: str,
    challenge_phrase: str,
    expected_pattern: str,
    enrollment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a voice sample during enrollment."""
    import hashlib
    
    from sqlalchemy.dialects.postgresql import UUID
    
    # Decode audio
    try:
        audio_bytes = base64.b64decode(audio_data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid audio data format"
        )
    
    # Verify challenge phrase (simplified - real implementation would use speech recognition)
    actual_pattern = hashlib.sha256(challenge_phrase.encode()).hexdigest()[:16]
    if not SecurityUtils.verify_voice_challenge(challenge_phrase, expected_pattern):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Challenge phrase verification failed"
        )
    
    # Get voice profile
    profile = db.query(VoiceProfile).filter(
        VoiceProfile.id == UUID(enrollment_id),
        VoiceProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    # Generate voice embedding (using OpenAI Whisper for embedding in production)
    # This is a placeholder - real implementation would call Whisper API
    # For now, we'll use a hash of the audio as a placeholder embedding
    embedding = hashlib.sha256(audio_bytes).digest()
    
    # If first sample, store directly
    if profile.enrollment_samples == 0:
        profile.voice_embedding = embedding
    else:
        # Average with existing embedding (simplified)
        # In production, use proper averaging or concatenation
        existing = profile.voice_embedding
        combined = bytes([a ^ b for a, b in zip(existing, embedding)])
        profile.voice_embedding = combined
    
    profile.enrollment_samples += 1
    profile.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "samples_collected": profile.enrollment_samples,
        "samples_required": settings.VOICE_ENROLLMENT_SAMPLES,
        "is_complete": profile.enrollment_samples >= settings.VOICE_ENROLLMENT_SAMPLES
    }


@router.get("/profiles", response_model=list[VoiceProfileResponse])
async def list_voice_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's voice profiles."""
    profiles = db.query(VoiceProfile).filter(
        VoiceProfile.user_id == current_user.id
    ).all()
    
    return [
        VoiceProfileResponse(
            id=str(p.id),
            profile_name=p.profile_name,
            permission_level=p.permission_level,
            is_active=p.is_active,
            enrollment_complete=p.enrollment_complete,
            enrollment_samples=p.enrollment_samples,
            last_used_at=p.last_used_at
        )
        for p in profiles
    ]


@router.delete("/profiles/{profile_id}")
async def delete_voice_profile(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a voice profile."""
    from sqlalchemy.dialects.postgresql import UUID
    
    profile = db.query(VoiceProfile).filter(
        VoiceProfile.id == UUID(profile_id),
        VoiceProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice profile not found"
        )
    
    db.delete(profile)
    db.commit()
    
    return {"message": "Voice profile deleted"}


@router.post("/verify", response_model=VoiceVerifyResponse)
async def verify_voice(
    request: VoiceVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify voice for command execution."""
    # Decode audio
    try:
        audio_bytes = base64.b64decode(request.audio_data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid audio data format"
        )
    
    # Get active voice profiles for user
    profiles = db.query(VoiceProfile).filter(
        VoiceProfile.user_id == current_user.id,
        VoiceProfile.is_active == True,
        VoiceProfile.enrollment_complete == True
    ).all()
    
    if not profiles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No voice profiles found. Please enroll first."
        )
    
    # Generate voice embedding (placeholder - real implementation uses Whisper)
    import hashlib
    test_embedding = hashlib.sha256(audio_bytes).digest()
    
    # Compare with each profile (simplified - real implementation uses cosine similarity)
    best_match = None
    best_confidence = 0.0
    
    for profile in profiles:
        # Decrypt stored embedding
        try:
            stored = SecurityUtils.decrypt_voice_embedding(
                profile.voice_embedding,
                profile.embedding_salt
            )
        except Exception:
            continue
        
        # Simple similarity (XOR distance - placeholder)
        # Real implementation would use proper embedding similarity
        distance = sum(a ^ b for a, b in zip(stored[:50], test_embedding[:50]))
        similarity = 1.0 - (distance / 256.0)
        
        if similarity > best_confidence:
            best_confidence = similarity
            best_match = profile
    
    # Check against threshold
    verified = best_confidence >= settings.VOICE_MATCH_THRESHOLD
    
    # Log verification attempt
    audit = AuditLog(
        user_id=current_user.id,
        action_type="voice_verify",
        action_details={
            "confidence": best_confidence,
            "verified": verified,
            "profile_id": str(best_match.id) if best_match else None
        },
        result="success" if verified else "failure"
    )
    db.add(audit)
    db.commit()
    
    # Determine if confirmation is required (sensitive actions always need confirmation)
    requires_confirmation = verified and best_match.permission_level < 2
    
    return VoiceVerifyResponse(
        verified=verified,
        profile_id=str(best_match.id) if best_match else None,
        confidence=best_confidence,
        permission_level=best_match.permission_level if best_match else 0,
        requires_confirmation=requires_confirmation
    )


@router.post("/session/start", response_model=VoiceSessionResponse)
async def start_voice_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new voice session."""
    session = VoiceSession(
        user_id=current_user.id,
        status="active",
        commands_count=0,
        commands=[]
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return VoiceSessionResponse(
        session_id=str(session.id),
        commands_count=session.commands_count,
        status=session.status
    )


@router.post("/session/end")
async def end_voice_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """End a voice session."""
    from sqlalchemy.dialects.postgresql import UUID
    
    session = db.query(VoiceSession).filter(
        VoiceSession.id == UUID(session_id),
        VoiceSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.status = "completed"
    session.end_time = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Session ended", "commands_count": session.commands_count}


# ==================== WebSocket for Streaming ====================

class ConnectionManager:
    """WebSocket connection manager for voice streaming."""
    
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept and track WebSocket connection."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        """Remove WebSocket connection."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_text(self, session_id: str, message: str):
        """Send text message to client."""
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)
    
    async def send_json(self, session_id: str, data: dict):
        """Send JSON data to client."""
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(data)


manager = ConnectionManager()


@router.websocket("/stream/{session_id}")
async def voice_stream_websocket(
    websocket: WebSocket,
    session_id: str
):
    """WebSocket endpoint for streaming voice data."""
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive audio data from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "audio":
                    # Process audio chunk
                    audio_data = message.get("data")
                    
                    # Send acknowledgment
                    await manager.send_json(session_id, {
                        "type": "acknowledgment",
                        "received": True
                    })
                
                elif message_type == "command":
                    # End of voice command
                    await manager.send_json(session_id, {
                        "type": "command_complete",
                        "transcript": message.get("transcript", "")
                    })
                
            except json.JSONDecodeError:
                await manager.send_json(session_id, {
                    "type": "error",
                    "message": "Invalid message format"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)