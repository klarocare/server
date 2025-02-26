from pydantic import EmailStr

from models.base import MongoModel


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
