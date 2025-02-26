from fastapi import APIRouter, Depends

from core.auth import AuthHandler
from schemas.rag_schema import Language, RAGResponse, RAGRequest
from services.rag_service import RAGService
from models.user import User


service = RAGService()

router = APIRouter(
    prefix="/rag",
    tags=["rag"],
    responses={404: {"description": "Not found"}},
)

@router.post("/query", response_model=RAGResponse)
async def query(request: RAGRequest, current_user: User = Depends(AuthHandler.get_current_user)):
    # Add input to the history
    response = service.query(message=request.message, chat_history=request.chat_history, language=Language.GERMAN)
    return response
