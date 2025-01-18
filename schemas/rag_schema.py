from enum import Enum

from typing import List, Optional

from pydantic import BaseModel


class Language(Enum):
    ENGLISH = "en"
    GERMAN = "de"


class RAGMessage(BaseModel):
    role: str
    content: str


class RAGRequest(BaseModel):
    message: str
    chat_history: List[RAGMessage]


class RAGResponse(BaseModel):
    answer: str
    sources: List[str]
    thumbnails: Optional[List[str]] = None
    video_URLs: Optional[List[str]] = None