from datetime import datetime
from typing import Optional, Dict

from pydantic import Field
from beanie import PydanticObjectId

from models.base import MongoModel
from models.chat import Message
from schemas.rag_schema import Language


class WhatsappUser(MongoModel):
    whatsapp_id: str
    last_active: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)
    language: Language = Field(default=Language.GERMAN) 

    @classmethod
    async def get_or_create_session(cls, whatsapp_id):
        is_created = False
        obj = await cls.find_one(cls.whatsapp_id == whatsapp_id)
        if not obj:
            obj = WhatsappUser(whatsapp_id=whatsapp_id)
            is_created = True
            await obj.insert()
            
        return obj, is_created


class WhatsappChatMessage(Message):
    session_id: PydanticObjectId
    whatsapp_id: str
    object_id: Optional[str] = None
    metadata: Optional[Dict] = None

    @classmethod
    async def get_recent_messages(cls, whatsapp_id: str, limit: int = 10):
        return await cls.find(cls.whatsapp_id == whatsapp_id).sort(-cls.created_at).limit(limit).to_list()

    @classmethod
    async def get_message_by_object_id(cls, object_id: str):
        return await cls.find(cls.object_id == object_id).first_or_none()
        