from enum import Enum

from typing import List

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


class PublicChatRequest(BaseModel):
    message: str
    chat_history: List[RAGMessage] = Field(default=[], description="Previous chat messages from client")
    language: Language = Field(default=Language.GERMAN, description="Preferred language for the response")


class RAGOutput(BaseModel):
    answer: str = Field(description="The actual answer to the question")
    quick_reply_options: List[str] = Field(description="List of possible quick replies to the generated answer")


class ArticleOutput(BaseModel):
    title: str = Field(description="A clear and engaging title for the article")
    tags: List[str] = Field(description="A list of relevant tags (e.g., caregiving, care money, mobility support)")
    summary: str = Field(description="A short summary (2-3 sentences) of the article")
    content: str = Field(description="The main body of the article")
    estimated_reading_time: int = Field(description="Approximate reading time in minutes")
