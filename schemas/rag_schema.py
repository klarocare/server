from enum import Enum

from typing import List, Optional

from pydantic import BaseModel


class Language(Enum):
    ENGLISH = "en"
    GERMAN = "de"

    def get_prompt_language(self):
        match self:
            case Language.ENGLISH:
                return "English"
            case Language.GERMAN:
                return "Deutsch"
            case _:
                return "Deutsch"


class RAGMessage(BaseModel):
    role: str
    content: str


class RAGRequest(BaseModel):
    message: str


class RAGResponse(BaseModel):
    answer: str
    sources: List[str]
    thumbnails: Optional[List[str]] = None
    video_URLs: Optional[List[str]] = None