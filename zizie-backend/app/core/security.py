"""
Security Utilities
Password hashing, JWT token handling, encryption
"""
import base64
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


class SecurityUtils:
    """Security utility functions."""
    
    # Password hashing context
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password."""
        return SecurityUtils.pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return SecurityUtils.pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        """Decode a JWT access token."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def create_refresh_token() -> str:
        """Create a refresh token."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_salt() -> str:
        """Generate a random salt."""
        return secrets.token_hex(32)
    
    @staticmethod
    def encrypt_voice_embedding(embedding: bytes, salt: str) -> bytes:
        """Encrypt voice embedding data."""
        # Derive key from salt
        key = hashlib.pbkdf2_hmac(
            'sha256',
            settings.SECRET_KEY.encode(),
            salt.encode(),
            iterations=100000
        )
        
        # Generate random IV
        iv = secrets.token_bytes(16)
        
        # Encrypt using AES
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        # Pad to block size
        padding_length = 16 - (len(embedding) % 16)
        padded_data = embedding + bytes([padding_length] * padding_length)
        
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        
        # Combine IV + encrypted data
        return iv + encrypted
    
    @staticmethod
    def decrypt_voice_embedding(encrypted_data: bytes, salt: str) -> bytes:
        """Decrypt voice embedding data."""
        # Derive key from salt
        key = hashlib.pbkdf2_hmac(
            'sha256',
            settings.SECRET_KEY.encode(),
            salt.encode(),
            iterations=100000
        )
        
        # Extract IV and encrypted data
        iv = encrypted_data[:16]
        encrypted = encrypted_data[16:]
        
        # Decrypt using AES
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        
        decrypted = decryptor.update(encrypted) + decryptor.finalize()
        
        # Remove padding
        padding_length = decrypted[-1]
        return decrypted[:-padding_length]
    
    @staticmethod
    def generate_voice_challenge() -> Tuple[str, str]:
        """Generate a voice challenge phrase and expected pattern."""
        phrases = [
            "Hey Zizie, schedule my day",
            "Send an email to my lawyer about the contract",
            "Remind me to call my accountant tomorrow",
            "Add a note about the meeting",
            "What's on my calendar for tomorrow",
            "Create an event for next Monday at 3pm",
            "Send a message to my assistant",
            "Read my unread emails",
        ]
        
        phrase = secrets.choice(phrases)
        
        # Create a simple challenge pattern from the phrase
        pattern = hashlib.sha256(phrase.encode()).hexdigest()[:16]
        
        return phrase, pattern
    
    @staticmethod
    def verify_voice_challenge(phrase: str, expected_pattern: str) -> bool:
        """Verify a voice challenge phrase."""
        actual_pattern = hashlib.sha256(phrase.encode()).hexdigest()[:16]
        return secrets.compare_digest(actual_pattern, expected_pattern)
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate an API key."""
        return f"zizie_{secrets.token_urlsafe(32)}"
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash an API key."""
        return hashlib.sha256(api_key.encode()).hexdigest()