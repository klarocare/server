from typing import Optional, Annotated
from datetime import datetime

from pydantic import EmailStr, Field
from beanie import Indexed

from models.base import MongoModel
from models.chat import ChatMessage
from schemas.rag_schema import Language


class User(MongoModel):
    email: Annotated[EmailStr, Indexed(unique=True)]
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    verification_token: Optional[str] = None
    verification_token_expires: Optional[datetime] = None
    username: str
    caretaker_name: Optional[str] = None
    language: Language = Field(default=Language.GERMAN)

    @classmethod
    async def get_by_email(cls, email: str):
        return await cls.find_one(cls.email == email)

    @classmethod
    async def get_by_verification_token(cls, token: str):
        return await cls.find_one(
            cls.verification_token == token,
            cls.verification_token_expires > datetime.now()
        )

    async def get_recent_messages(self, limit: int = 20):
        """Retrieve all messages associated with this user."""
        return await ChatMessage.find(ChatMessage.user_id == self.id).sort(-ChatMessage.created_at).limit(limit).to_list()
    
    async def get_article_info(self):
        return f"Username is: {self.username}"

