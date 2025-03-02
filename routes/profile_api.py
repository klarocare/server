from fastapi import APIRouter, Depends

from models.user import User
from core.auth import AuthHandler
from services.profile_service import ProfileService
from schemas.profile_schema import UpdateProfileRequest


router = APIRouter(
    prefix="/profile",
    tags=["profile"],
)

service = ProfileService()

@router.get("", response_model=User)
async def get_profile(current_user: User = Depends(AuthHandler.get_current_user)):
    """Get current user profile"""
    return current_user

@router.put("", response_model=User)
async def update_profile(request: UpdateProfileRequest, current_user: User = Depends(AuthHandler.get_current_user)):
    """Get current user profile"""
    return service.update_user(request, current_user)
