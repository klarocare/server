from enum import Enum
from typing import List, Optional, Dict

from pydantic import BaseModel


class Language(Enum):
    ENGLISH = "en"
    GERMAN = "de"

class ChatRequest(BaseModel):
    input: str


class SetupRequest(BaseModel):
    language: Language


class ChatResponse(BaseModel):
    chat_history: List[dict]
    sources: List[str]
    thumbnails: Optional[List[str]] = None
    video_URLs: Optional[List[str]] = None
    locations: Optional[Dict] = None
    answer: str
