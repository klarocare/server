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
        obj = await cls.find_one(cls.whatsapp_id == whatsapp_id)
        if not obj:
            obj = UserSession(whatsapp_id=whatsapp_id)
            await obj.insert()
            
        return obj

class ChatMessage(MongoModel):
    session_id: PydanticObjectId
    whatsapp_id: str
    role: str
    content: str
    metadata: Optional[Dict] = None