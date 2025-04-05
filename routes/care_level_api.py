from fastapi import APIRouter, Depends

from core.auth import AuthHandler
from models.user import User
from services.care_level_service import CareLevelService
from schemas.care_level_schema import CareLevelRequestSchema, CareLevelResponseSchema


router = APIRouter(
    prefix="/care-level",
    tags=["care-level"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=CareLevelResponseSchema)
async def calculate_care_level(request: CareLevelRequestSchema, current_user: User = Depends(AuthHandler.get_current_user)) -> CareLevelResponseSchema:
    """
    Calculate care level based on assessment data.
    The calculation follows the new scoring system with weighted modules:
    - M1 Mobility (10%)
    - M2a/b Cognition/Behavior (15%, higher score used)
    - M3 Self-care (40%)
    - M4 Health-related demands (20%)
    - M5 Everyday & social life (15%)
    """
    return CareLevelService.calculate_care_level(request, current_user)
