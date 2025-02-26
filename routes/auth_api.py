from fastapi import APIRouter, Depends, HTTPException, status
import logging

from core.auth import AuthHandler
from services.auth_service import AuthService
from schemas.auth_schema import (
    LoginRequest,
    RegisterRequest,
    TokenSchema,
    UserResponse
)
from models.user import UserCredentials


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

auth_service = AuthService()

@router.post("/login", response_model=TokenSchema)
async def login(request: LoginRequest):
    """Login with email and password"""
    return await auth_service.login(request)

@router.post("/register", response_model=TokenSchema)
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
async def logout(current_user: UserCredentials = Depends(AuthHandler.get_current_user)):
    """
    Logout user
    Note: In a production environment, you might want to blacklist the token
    """
    return {"detail": "Successfully logged out"}

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: UserCredentials = Depends(AuthHandler.get_current_user)):
    """Get current user profile"""
    return current_user 

@router.get("/debug/users", tags=["debug"]) # TODO: Remove this endpoint. Or add admin access to it
async def get_all_users():
    """Debug endpoint to see all users in the database"""
    users = await UserCredentials.find_all().to_list()
    return users 