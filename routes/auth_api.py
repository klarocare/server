from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import logging

from core.auth import AuthHandler
from services.auth_service import AuthService
from schemas.auth_schema import (
    LoginRequest,
    RegisterRequest,
    TokenSchema
)
from models.user import User


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

auth_service = AuthService()

@router.post("/login", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with username (email) and password"""
    login_request = LoginRequest(
        email=form_data.username,
        password=form_data.password
    )
    return await auth_service.login(login_request)

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

@router.get("/verify/{token}", response_model=TokenSchema)
async def verify_email(token: str):
    """Verify user's email address"""
    return await auth_service.verify_email(token)
