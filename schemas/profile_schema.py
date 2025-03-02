from typing import Optional

from pydantic import BaseModel
from schemas.rag_schema import Language


class UpdateProfileRequest(BaseModel):
    username: Optional[str] = None
    caretaker_name: Optional[str] = None
    language: Optional[Language] = None