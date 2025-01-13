from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict

from pydantic import BaseModel, Field

from schemas import PyObjectId, ObjectId

### Models saved into DB ###

class UserSession(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    whatsapp_id: str
    # language: Language = Field(default=Language.ENGLISH) 
    # location: str = "Garching, Munich"
    created_at: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_alias = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ChatMessage(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    session_id: PyObjectId
    whatsapp_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict] = None  # For storing any additional WhatsApp-specific data

    class Config:
        allow_population_by_alias = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
