from fastapi import APIRouter

from schemas.chat_schema import ChatRequest, ChatResponse, SetupRequest
from services.chat_service import ChatService

service = ChatService()

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

@router.post("/setup")
async def setup_endpoint(request: SetupRequest):
    # Setup the llm
    service.setup(request)
    return "Setup has successfully completed"

@router.post("/query", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Add input to the history
    response = await service.query(request)
    return response
