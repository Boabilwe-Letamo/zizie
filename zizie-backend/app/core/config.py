"""
Application Configuration Settings
"""
import os
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Zizie"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Database
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "zizie")
    
    # Supabase (alternative to PostgreSQL)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Additional Supabase settings from provided credentials
    SUPABASE_DB_HOST: str = os.getenv("SUPABASE_DB_HOST", "")
    SUPABASE_DB_PORT: int = int(os.getenv("SUPABASE_DB_PORT", "6543"))
    SUPABASE_DB_NAME: str = os.getenv("SUPABASE_DB_NAME", "postgres")
    SUPABASE_DB_USER: str = os.getenv("SUPABASE_DB_USER", "postgres")
    SUPABASE_DB_PASSWORD: str = os.getenv("SUPABASE_DB_PASSWORD", "")
    
    @property
    def DATABASE_URL(self) -> str:
        """Get database URL."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Get SQLAlchemy database URL."""
        return self.DATABASE_URL
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    
    @property
    def REDIS_URL(self) -> str:
        """Get Redis URL."""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    # Voice Services - Use FREE alternatives
    
    # OpenAI Whisper (OPTIONAL - $0.36/min, first 60min free)
    # Get free key at: https://platform.openai.com
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "whisper-1")
    
    # WhisperX (FREE! Open source, runs locally)
    # Install: pip install whisperx
    # Requires: ffmpeg, torch
    WHISPERX_MODEL: str = os.getenv("WHISPERX_MODEL", "base")
    WHISPERX_DEVICE: str = os.getenv("WHISPERX_DEVICE", "cuda")  # or "cpu"
    USE_WHISPERX: bool = os.getenv("USE_WHISPERX", "true").lower() == "true"
    
    # pyannote.audio (FREE! Speaker diarization)
    # Install: pip install pyannote-audio
    # Requires: pyannote.pipeline (v3+)
    USE_PYANNOTE: bool = os.getenv("USE_PYANNOTE", "true").lower() == "true"
    PYANNOTE_MODEL: str = os.getenv("PYANNOTE_MODEL", "pyannote/v3.1")
    HUGGINGFACE_TOKEN: str = os.getenv("HUGGINGFACE_TOKEN", "")
    
    # FREE: Ollama (local LLM - no API key needed!)
    # Install: curl -fsSL https://ollama.com/install.sh | sh
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    # HuggingFace Inference API (FREE LLM)
    # Note: Requires a valid HF token with Inference API access
    HF_INFERENCE: bool = os.getenv("HF_INFERENCE", "false").lower() == "true"
    HF_MODEL: str = os.getenv("HF_MODEL", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    
    # ElevenLabs (OPTIONAL - for premium TTS)
    # Get free key at: https://elevenlabs.io
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    
    PICOVOICE_API_KEY: str = os.getenv("PICOVOICE_API_KEY", "")
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/google/callback")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    
    # Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "noreply@zizie.app")
    
    # Voice Biometrics
    VOICE_MATCH_THRESHOLD: float = float(os.getenv("VOICE_MATCH_THRESHOLD", "0.75"))
    VOICE_ENROLLMENT_SAMPLES: int = int(os.getenv("VOICE_ENROLLMENT_SAMPLES", "5"))
    
    # LLM
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get settings instance (cached)."""
    return Settings()


settings = get_settings()