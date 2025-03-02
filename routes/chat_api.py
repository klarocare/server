from fastapi import APIRouter, Depends

from core.auth import AuthHandler
from schemas.rag_schema import RAGResponse, RAGRequest
from services.chat_service import ChatService
from models.user import UserCredentials


service = ChatService()

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

@router.post("/query", response_model=RAGResponse)
async def query(request: RAGRequest, current_user: UserCredentials = Depends(AuthHandler.get_current_user)):
    # Add input to the history
    response = await service.query(user_credentials=current_user, message=request.message)
    return response
