from datetime import datetime
from typing import List, Optional

from bson import ObjectId

from schemas.chat_schema import ChatMessage, UserSession


class ChatDatabase:
    def __init__(self, database):
        self.db = database
        self.setup_indexes()

    def setup_indexes(self):
        # Create indexes for better query performance
        self.db.sessions.create_index("whatsapp_id")
        self.db.sessions.create_index("last_active")
        self.db.messages.create_index([("session_id", 1), ("timestamp", 1)])
        self.db.messages.create_index("whatsapp_id")

    async def create_session(self, session: UserSession) -> str:
        result = await self.db.sessions.insert_one(session.model_dump(by_alias=True))
        return str(result.inserted_id)

    async def get_session(self, whatsapp_id: str) -> Optional[UserSession]:
        session_data = await self.db.sessions.find_one({"whatsapp_id": whatsapp_id})
        return UserSession.model_validate(session_data) if session_data else None

    async def get_or_create_session(self, whatsapp_id: str) -> UserSession:
        session = await self.get_session(whatsapp_id)
        if not session:
            session = UserSession(whatsapp_id=whatsapp_id)
            await self.create_session(session)
        else:
            await self.update_session_activity(str(session.id))

    async def update_session_activity(self, session_id: str):
        await self.db.sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"last_active": datetime.utcnow()}}
        )

    async def save_message(self, message: ChatMessage):
        await self.db.messages.insert_one(message.model_dump(by_alias=True))

    async def get_recent_messages(self, whatsapp_id: str, limit: int = 10) -> List[ChatMessage]:
        cursor = self.db.messages.find({"whatsapp_id": whatsapp_id})\
            .sort("timestamp", -1)\
            .limit(limit)
        messages = await cursor.to_list(length=limit)
        return [ChatMessage.model_validate(msg) for msg in messages]