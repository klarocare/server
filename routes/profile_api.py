from fastapi import APIRouter, Depends, HTTPException, status
import logging

from core.auth import AuthHandler
from services.profile_service import ProfileService
from schemas.profile_schema import ProfileRequest
from models.user import UserCredentials, UserProfile


router = APIRouter(
    prefix="/profile",
    tags=["profile"],
)

service = ProfileService()

@router.post("")
async def create_profile(request: ProfileRequest, current_user: UserCredentials = Depends(AuthHandler.get_current_user)):
    """
    Logout user
    Note: In a production environment, you might want to blacklist the token
    """
    return await service.create(request, current_user)

@router.get("", response_model=UserProfile)
async def get_profile(current_user: UserCredentials = Depends(AuthHandler.get_current_user)):
    """Get current user profile"""
    return await current_user.get_user() 
