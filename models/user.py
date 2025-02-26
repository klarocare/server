from pydantic import EmailStr, Field

from models.base import MongoModel
from schemas.rag_schema import Language


# TODO: Bu model User'ı extend edebilir, buradaki relation'ı düşünelim
class UserCredentials(MongoModel):
    """
    User model that extends Caregiver with authentication fields
    """
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    
    @classmethod
    async def get_by_email(cls, email: str):
        return await cls.find_one(cls.email == email)


class User(UserCredentials):
    username: str
    caretaker_name: str
    language: Language = Field(default=Language.GERMAN)
