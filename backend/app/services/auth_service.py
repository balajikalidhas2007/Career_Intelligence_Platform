from datetime import datetime, timedelta, timezone
import secrets
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.auth_account import AuthAccount
from app.models.refresh_token import RefreshToken
from app.utils.security import create_access_token, hash_token, encrypt_github_token
from app.config import settings

async def create_or_update_user_from_github(
    db: AsyncSession, github_user: dict, github_token: str
) -> User:
    """Create or update a user from GitHub profile data."""
    github_id = str(github_user["id"])
    email = github_user.get("email")
    display_name = github_user.get("name") or github_user.get("login")
    avatar_url = github_user.get("avatar_url")
    username = github_user.get("login")

    # Look for existing AuthAccount
    result = await db.execute(
        select(AuthAccount).where(
            AuthAccount.provider == "github", 
            AuthAccount.provider_account_id == github_id
        )
    )
    auth_account = result.scalar_one_or_none()

    if auth_account:
        # Update existing user and auth account
        user = await db.get(User, auth_account.user_id)
        if user:
            user.display_name = display_name
            user.avatar_url = avatar_url
            if email and not user.email:
                user.email = email
            
        auth_account.access_token_encrypted = encrypt_github_token(github_token)
        auth_account.provider_username = username
        auth_account.raw_profile = github_user
    else:
        # Try to find user by email first to link accounts
        user = None
        if email:
            user_result = await db.execute(select(User).where(User.email == email))
            user = user_result.scalar_one_or_none()
            
        if not user:
            # Create new user
            user = User(
                email=email,
                display_name=display_name,
                avatar_url=avatar_url,
            )
            db.add(user)
            await db.flush() # Get user.id

        # Create new AuthAccount
        auth_account = AuthAccount(
            user_id=user.id,
            provider="github",
            provider_account_id=github_id,
            provider_username=username,
            access_token_encrypted=encrypt_github_token(github_token),
            raw_profile=github_user,
        )
        db.add(auth_account)

    await db.commit()
    await db.refresh(user)
    return user

async def create_tokens(db: AsyncSession, user: User) -> Tuple[str, str]:
    """Create a new access token and refresh token."""
    access_token = create_access_token(subject=str(user.id))
    
    raw_refresh_token = secrets.token_urlsafe(32)
    refresh_token_expires = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(raw_refresh_token),
        expires_at=refresh_token_expires,
    )
    db.add(db_refresh_token)
    await db.commit()
    
    return access_token, raw_refresh_token

async def refresh_access_token(db: AsyncSession, refresh_token_value: str) -> Tuple[str, str]:
    """Validate refresh token and issue new tokens (rotation)."""
    token_hash_val = hash_token(refresh_token_value)
    
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash_val,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.now(timezone.utc)
        )
    )
    db_refresh_token = result.scalar_one_or_none()
    
    if not db_refresh_token:
        return None, None
        
    user = await db.get(User, db_refresh_token.user_id)
    if not user or not user.is_active:
        return None, None
        
    # Revoke old refresh token (rotation)
    db_refresh_token.revoked_at = datetime.now(timezone.utc)
    
    return await create_tokens(db, user)

async def revoke_refresh_token(db: AsyncSession, refresh_token_value: str) -> bool:
    """Revoke a specific refresh token."""
    token_hash_val = hash_token(refresh_token_value)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash_val)
    )
    db_refresh_token = result.scalar_one_or_none()
    
    if db_refresh_token and db_refresh_token.revoked_at is None:
        db_refresh_token.revoked_at = datetime.now(timezone.utc)
        await db.commit()
        return True
    return False
