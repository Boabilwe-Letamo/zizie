"""
Database Base and Session Management
Supports: Supabase (PostgreSQL), SQLite (dev fallback)
"""
import os
from supabase import create_client, Client
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# Supabase client singleton
supabase_client: Client = None


def get_supabase_client() -> Client:
    """Get or create Supabase client."""
    global supabase_client
    
    if supabase_client is None and settings.SUPABASE_URL and settings.SUPABASE_KEY:
        supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    
    return supabase_client


def get_database_url():
    """Get database URL."""
    
    # For development, use SQLite (works anywhere)
    # For production Supabase, you'll need the correct connection string
    # and network access to Supabase servers
    return "sqlite:///./zizie_dev.db"


# Create engine
database_url = get_database_url()
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()