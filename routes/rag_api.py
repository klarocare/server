from fastapi import APIRouter

from schemas.rag_schema import RAGResponse, RAGRequest
from services.rag_service import RAGService


service = RAGService.get_instance()

router = APIRouter(
    prefix="/rag",
    tags=["rag"],
    responses={404: {"description": "Not found"}},
)

@router.post("/query", response_model=RAGResponse)
async def query(request: RAGRequest):
    # Add input to the history
    response = service.query(message=request.message, chat_history=request.chat_history)
    return response
