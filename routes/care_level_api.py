from fastapi import APIRouter

from services.care_level_service import CareLevelService
from schemas.care_level_schema import CareAssessmentSchema, CareEstimateSchema


router = APIRouter(
    prefix="/care-level",
    tags=["care-level"],
    responses={404: {"description": "Not found"}},
)

@router.post("", response_model=CareEstimateSchema)
async def estimate_care_level(request: CareAssessmentSchema):
    return CareLevelService.get_care_benefits(request)
