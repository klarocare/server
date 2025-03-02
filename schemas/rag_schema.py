from enum import Enum

from typing import List, Optional

from pydantic import BaseModel, Field


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


class RAGOutput(BaseModel):
    answer: str = Field(description="The actual answer to the question")
    quick_reply_options: List[str] = Field(description="List of possible quick replies to the generated answer")
