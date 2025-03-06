from typing import List

from fastapi import APIRouter, Depends

from core.auth import AuthHandler
from models.content import Article
from services.content_service import ContentService
from models.user import User


service = ContentService()

router = APIRouter(
    prefix="/content",
    tags=["content"],
    responses={404: {"description": "Not found"}},
)

@router.post("/articles/generate", response_model=Article)
async def generate_article(current_user: User = Depends(AuthHandler.get_current_user)):
    # Add input to the history
    response = await service.generate_article(current_user)
    return response

@router.get("/articles", response_model=List[Article])
async def get_articles(current_user: User = Depends(AuthHandler.get_current_user)):
    # Add input to the history
    return await Article.get_articles_by_user(current_user.id)

@router.get("/articles/{id}", response_model=Article)
async def get_article_by_id(id: str, current_user: User = Depends(AuthHandler.get_current_user)):
    # Add input to the history
    return await Article.get(id)
