from typing import Optional

from pydantic import EmailStr, Field

from models.base import MongoModel
from models.chat import ChatMessage
from schemas.rag_schema import Language


class User(MongoModel):
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    username: str
    caretaker_name: Optional[str] = None
    language: Language = Field(default=Language.GERMAN)

    @classmethod
    async def get_by_email(cls, email: str):
        return await cls.find_one(cls.email == email)

    async def get_recent_messages(self, limit: int = 20):
        """Retrieve all messages associated with this user."""
        return await ChatMessage.find(ChatMessage.user_id == self.id).sort(-ChatMessage.created_at).limit(limit).to_list()
    
    async def get_article_info(self):
        return f"Username is: {self.username}"

