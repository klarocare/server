from typing import Optional

from pydantic import BaseModel
from schemas.rag_schema import Language


class ProfileRequest(BaseModel):
    username: str
    caretaker_name: str
    language: Optional[Language] = Language.GERMAN
