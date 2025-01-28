from datetime import datetime
from typing import Optional, Dict

from pydantic import Field
from beanie import PydanticObjectId

from models.base import MongoModel

class UserSession(MongoModel):
    whatsapp_id: str
    last_active: datetime = Field(default_factory=datetime.now)

    @classmethod
    async def get_or_create_session(cls, whatsapp_id):
        is_created = False
        obj = await cls.find_one(cls.whatsapp_id == whatsapp_id)
        if not obj:
            obj = UserSession(whatsapp_id=whatsapp_id)
            is_created = True
            await obj.insert()
            
        return obj, is_created

class ChatMessage(MongoModel):
    session_id: PydanticObjectId
    whatsapp_id: str
    object_id: Optional[str] = None
    role: str
    content: str
    metadata: Optional[Dict] = None

    @classmethod
    async def get_recent_messages(cls, whatsapp_id: str, limit: int = 10):
        return await cls.find(cls.whatsapp_id == whatsapp_id).sort(-cls.created_at).limit(limit).to_list()

    @classmethod
    async def get_message_by_object_id(cls, object_id: str):
        return await cls.find(cls.object_id == object_id).first_or_none()
        