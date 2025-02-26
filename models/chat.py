from beanie import PydanticObjectId

from models.base import MongoModel

class Message(MongoModel):
    role: str
    content: str


class ChatMessage(Message):
    user: PydanticObjectId
