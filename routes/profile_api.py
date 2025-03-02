from fastapi import APIRouter, Depends

from core.auth import AuthHandler
from services.profile_service import ProfileService
from models.user import User


router = APIRouter(
    prefix="/profile",
    tags=["profile"],
)

service = ProfileService()

@router.get("", response_model=User)
async def get_profile(current_user: User = Depends(AuthHandler.get_current_user)):
    """Get current user profile"""
    return current_user
