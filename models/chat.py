from datetime import datetime
from typing import Optional, Dict

from pydantic import Field

from models.base import MongoModel
from utils.object_id import PyObjectId

class UserSession(MongoModel):
    whatsapp_id: str
    last_active: datetime = Field(default_factory=datetime.now)

class ChatMessage(MongoModel):
    session_id: PyObjectId
    whatsapp_id: str
    role: str
    content: str
    metadata: Optional[Dict] = None