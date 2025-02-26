from typing import List
from pydantic import EmailStr

from models.base import MongoModel
from schemas.care_task_schema import Caregiver, CareTask


class User(MongoModel, Caregiver):
    """
    User model that extends Caregiver with authentication fields
    """
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    
    @classmethod
    async def get_by_email(cls, email: str):
        return await cls.find_one(cls.email == email)
