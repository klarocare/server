from fastapi import APIRouter, Depends
import logging
logging.basicConfig(level=logging.INFO)
from core.auth import AuthHandler
from schemas.rag_schema import RAGOutput, RAGRequest, PublicChatRequest, ChatResponse
from services.chat_service import ChatService
from models.user import User


service = ChatService()

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

@router.post("/query", response_model=RAGOutput)
async def query(request: RAGRequest, current_user: User = Depends(AuthHandler.get_current_user)):
    # Add input to the history
    response = await service.query(user=current_user, message=request.message)
    return response

@router.post("/public", response_model=ChatResponse)
async def public_query(request: PublicChatRequest):
    """Public chat endpoint that doesn't require authentication"""
    response = await service.public_query(request)
    logging.info(f"Response: {response}")
    return response
