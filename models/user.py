import logging

from pydantic import EmailStr, Field
from beanie import PydanticObjectId

from models.base import MongoModel
from models.chat import ChatMessage
from schemas.rag_schema import Language


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
    
    async def get_user(self):
        """Retrieve the User document associated with these credentials."""
        user_profile =  await UserProfile.find_one(UserProfile.credentials_id == self.id)
        logging.info(user_profile)
        return user_profile


class UserProfile(MongoModel):
    credentials_id: PydanticObjectId
    username: str
    caretaker_name: str
    language: Language = Field(default=Language.GERMAN)

    async def get_messages(self):
        """Retrieve all messages associated with this user."""
        return await ChatMessage.find(ChatMessage.user_id == self.id).to_list()
