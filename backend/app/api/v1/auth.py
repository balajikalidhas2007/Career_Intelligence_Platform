import secrets
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db_session
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import TokenResponse, UserResponse
from app.services.auth_service import (
    create_or_update_user_from_github,
    create_tokens,
    refresh_access_token,
    revoke_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_USER_URL = "https://api.github.com/user"

@router.get("/github")
async def login_github():
    """Redirect to GitHub for authentication."""
    state = secrets.token_urlsafe(32)
    redirect_uri = f"{settings.backend_url}/api/v1/auth/github/callback"
    url = f"{GITHUB_AUTH_URL}?client_id={settings.github_client_id}&redirect_uri={redirect_uri}&state={state}&scope=read:user user:email repo"
    redirect_response = RedirectResponse(url)
    redirect_response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        max_age=600,
        samesite="lax",
    )
    return redirect_response

@router.get("/github/callback")
async def github_callback(
    request: Request,
    response: Response,
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Callback for GitHub OAuth."""
    # Verify state
    cookie_state = request.cookies.get("oauth_state")
    if not cookie_state or cookie_state != state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
        
    response.delete_cookie("oauth_state")
    
    # Exchange code for token
    redirect_uri = f"{settings.backend_url}/api/v1/auth/github/callback"
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            GITHUB_TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            }
        )
        token_data = token_res.json()
        
        if "error" in token_data:
            raise HTTPException(status_code=400, detail=token_data.get("error_description", "Failed to authenticate"))
            
        access_token = token_data["access_token"]
        
        # Get user profile
        user_res = await client.get(
            GITHUB_API_USER_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        github_user = user_res.json()
        
        # Get user emails (primary one) if not public
        if not github_user.get("email"):
            emails_res = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            emails = emails_res.json()
            primary_email = next((e["email"] for e in emails if e["primary"]), None)
            github_user["email"] = primary_email

    # Process user in DB
    user = await create_or_update_user_from_github(db, github_user, access_token)
    
    # Issue tokens
    new_access_token, new_refresh_token = await create_tokens(db, user)
    
    # Redirect back to frontend (no token in URL)
    frontend_callback = f"{settings.frontend_url}/auth/success"
    redirect_response = RedirectResponse(url=frontend_callback)
    
    redirect_response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        path="/api/v1/auth",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )
    
    return redirect_response

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session)
):
    """Refresh access token using refresh token cookie."""
    refresh_token_val = request.cookies.get("refresh_token")
    if not refresh_token_val:
        raise HTTPException(status_code=401, detail="Refresh token missing")
        
    new_access, new_refresh = await refresh_access_token(db, refresh_token_val)
    if not new_access:
        response.delete_cookie("refresh_token")
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        path="/api/v1/auth",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )
    
    return TokenResponse(access_token=new_access)

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session)
):
    """Log out by revoking the refresh token."""
    refresh_token_val = request.cookies.get("refresh_token")
    if refresh_token_val:
        await revoke_refresh_token(db, refresh_token_val)
        
    response.delete_cookie("refresh_token", path="/api/v1/auth")
    return {"status": "logged out"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return current_user
