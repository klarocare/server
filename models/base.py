from datetime import datetime
from pydantic import Field

from beanie import Document


class MongoModel(Document):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
