from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from cryptography.fernet import Fernet
import hashlib
from typing import Any, Dict
from app.config import settings

def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            seconds=settings.access_token_expire_seconds
        )
    to_encode = {"exp": int(expire.timestamp()), "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt

def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode a JWT access token."""
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])

def hash_token(token: str) -> str:
    """Hash a token (like a refresh token) for database storage using SHA-256."""
    return hashlib.sha256(token.encode()).hexdigest()

def verify_token_hash(plain_token: str, hashed_token: str) -> bool:
    """Verify a token against its hash."""
    return hash_token(plain_token) == hashed_token


def encrypt_github_token(token: str) -> str:
    """Encrypt a GitHub access token using Fernet."""
    if not settings.github_token_encryption_key:
        raise ValueError("GITHUB_TOKEN_ENCRYPTION_KEY is not set")
    f = Fernet(settings.github_token_encryption_key.encode())
    return f.encrypt(token.encode()).decode()


def decrypt_github_token(encrypted_token: str) -> str:
    """Decrypt a GitHub access token using Fernet."""
    if not settings.github_token_encryption_key:
        raise ValueError("GITHUB_TOKEN_ENCRYPTION_KEY is not set")
    f = Fernet(settings.github_token_encryption_key.encode())
    return f.decrypt(encrypted_token.encode()).decode()
