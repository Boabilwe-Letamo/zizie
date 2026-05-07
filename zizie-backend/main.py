"""
Zizie - Voice-First AI Executive Assistant
Main Application Entry Point
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient  # For demo mode

from app.api.v1 import auth, voice, contacts, calendar, email, notes, reminders
from app.core.config import settings
from app.core.security import SecurityUtils
from app.db.base import Base
from app.db.session import engine, SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    # Create database tables (in development)
    if settings.DEBUG:
        Base.metadata.create_all(bind=engine)
    
    yield
    
    # Shutdown
    pass


app = FastAPI(
    title="Zizie API",
    description="Voice-First AI Executive Assistant Backend",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(voice.router, prefix="/api/v1/voice", tags=["Voice"])
app.include_router(contacts.router, prefix="/api/v1/contacts", tags=["Contacts"])
app.include_router(calendar.router, prefix="/api/v1/calendar", tags=["Calendar"])
app.include_router(email.router, prefix="/api/v1/email", tags=["Email"])
app.include_router(notes.router, prefix="/api/v1/notes", tags=["Notes"])
app.include_router(reminders.router, prefix="/api/v1/reminders", tags=["Reminders"])


@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Zizie API",
        "version": "1.0.0"
    }


@app.get("/api/v1/health", tags=["Health"])
async def api_health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )