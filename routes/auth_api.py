from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from fastapi.responses import RedirectResponse
import logging
from typing import Optional
import re

from core.auth import AuthHandler
from services.auth_service import AuthService
from schemas.auth_schema import (
    LoginRequest,
    RegisterRequest,
    TokenSchema
)
from models.user import User
from core.config import settings


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

auth_service = AuthService()

@router.post("/login", response_model=TokenSchema)
async def login(request: LoginRequest):
    """Login with email and password"""
    return await auth_service.login(request)

@router.post("/register")
async def register(request: RegisterRequest):
    """Register a new user"""
    try:
        return await auth_service.register(request)
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/logout")
async def logout(current_user: User = Depends(AuthHandler.get_current_user)):
    """
    Logout user
    Note: In a production environment, you might want to blacklist the token
    """
    return {"detail": "Successfully logged out"}

def detect_app_installation(request: Request, user_agent: Optional[str]) -> bool:
    """
    Detect if the user has the Flutter app installed based on:
    1. User agent string
    2. Custom app headers
    3. Deep link capability
    """
    # Check for custom app header
    app_version = request.headers.get('x-app-version')
    if app_version:
        return True
    
    # Check user agent for mobile devices
    if user_agent:
        # Common mobile OS patterns
        mobile_patterns = [
            r'Android',
            r'iPhone|iPad|iPod',
        ]
        
        is_mobile = any(re.search(pattern, user_agent) for pattern in mobile_patterns)
        
        if is_mobile:
            # For mobile users, we'll return a deep link URL that can
            # open the app if installed, or fallback to store
            return True
    
    return False

def get_appropriate_url(request: Request, user_agent: Optional[str]) -> str:
    """
    Determine the appropriate URL based on device and app installation status
    """
    has_app = detect_app_installation(request, user_agent)
    
    if has_app:
        # If on mobile, use deep link URL scheme
        # This will open the app if installed, or redirect to store if not
        return f"klaro-app://{settings.FLUTTER_APP_URL.replace('http://', '').replace('https://', '')}"
    else:
        # Use web landing page for desktop or when app status is unknown
        return settings.LANDING_PAGE_URL

@router.get("/verify/{token}")
async def verify_email(
    token: str,
    request: Request,
    user_agent: Optional[str] = Header(default=None)
):
    """Verify user's email address and redirect to frontend"""
    result = await auth_service.verify_email(token)
    
    # Get appropriate URL based on device and app installation
    base_frontend_url = get_appropriate_url(request, user_agent)
    
    if result["success"]:
        # On success, redirect to login page with success message
        redirect_url = (
            f"{base_frontend_url}/login"
            f"?verification=success&token={result['access_token']}"
        )
        return RedirectResponse(
            url=redirect_url,
            status_code=status.HTTP_302_FOUND
        )
    else:
        # On failure, redirect to error page with error message
        redirect_url = (
            f"{base_frontend_url}/verification-failed"
            f"?error={result['error_message']}"
        )
        return RedirectResponse(
            url=redirect_url,
            status_code=status.HTTP_302_FOUND
        )
