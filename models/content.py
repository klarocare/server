from typing import List

from beanie import PydanticObjectId
from pydantic import Field

from models.base import MongoModel

class Article(MongoModel):
    user_id: PydanticObjectId 
    title: str = Field(description="A clear and engaging title for the article")
    tags: List[str] = Field(description="A list of relevant tags (e.g., caregiving, care money, mobility support)")
    summary: str = Field(description="A short summary (2-3 sentences) of the article")
    content: str = Field(description="The main body of the article")
    estimated_reading_time: int = Field(description="Approximate reading time in minutes")

    @classmethod
    async def get_articles_by_user(cls, user_id: PydanticObjectId):
        return await cls.find(cls.user_id == user_id).to_list()
