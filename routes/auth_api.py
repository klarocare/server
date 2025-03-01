from fastapi import APIRouter, Depends, HTTPException, status
import logging

from core.auth import AuthHandler
from services.auth_service import AuthService
from schemas.auth_schema import (
    LoginRequest,
    RegisterRequest,
    TokenSchema,
    TokenType
)
from models.user import UserCredentials


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

service = AuthService()

@router.post("/login", response_model=TokenSchema)
async def login(request: LoginRequest):
    """Login with email and password"""
    return await service.login(request)

@router.post("/register", response_model=TokenSchema)
async def register(request: RegisterRequest):
    """Register a new user"""
    try:
        return await service.register(request)
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/logout")
async def logout(current_user: UserCredentials = Depends(AuthHandler.get_current_user)):
    """
    Logout user
    Note: In a production environment, you might want to blacklist the token
    """
    return {"detail": "Successfully logged out"}

@router.post("/refresh", response_model=TokenSchema)
async def refresh_token(request):
    """Get new access token using refresh token"""
    user_id = AuthHandler.verify_token(request.token, TokenType.REFRESH)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not authorize the request with refresh token."
        )
    return TokenSchema(
        access_token=AuthHandler.create_access_token(user_id),
        refresh_token=AuthHandler.create_refresh_token(user_id)
    )
