from typing import List
from datetime import datetime

from repositories.base import MongoRepository
from schemas.chat_schema import ChatMessage, UserSession


class SessionRepository(MongoRepository[UserSession]):
    def __init__(self):
        super().__init__(UserSession, "sessions")
    
    async def get_or_create_session(self, whatsapp_id: str) -> UserSession:
        session = await self.get_by_field("whatsapp_id", whatsapp_id)
        if not session:
            session = await self.create(UserSession(whatsapp_id=whatsapp_id))
        else:
            await self.update(str(session.id), {"last_active": datetime.now()})
        return session

class MessageRepository(MongoRepository[ChatMessage]):
    def __init__(self):
        super().__init__(ChatMessage, "messages")
    
    async def get_recent_messages(self, whatsapp_id: str, limit: int = 10) -> List[ChatMessage]:
        return await self.list(
            filter_query={"whatsapp_id": whatsapp_id},
            sort_by="created_at",
            sort_desc=True,
            limit=limit
        )