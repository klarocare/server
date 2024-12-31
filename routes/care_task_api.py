from fastapi import APIRouter

from schemas.care_task_schema import GenerateRequest, CareTaskList
from services.care_task_service import CareTaskService

service = CareTaskService()

router = APIRouter(
    prefix="/care-task",
    tags=["care-task"],
    responses={404: {"description": "Not found"}},
)

@router.post("/generate", response_model=CareTaskList)
async def generate_endpoint(request: GenerateRequest):
    # Setup the llm
    response = service.generate(request)
    return response
