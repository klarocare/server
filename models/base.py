from typing import Annotated
from datetime import datetime
from pydantic import Field

from beanie import Document, Indexed


class MongoModel(Document):
    created_at: Annotated[datetime, Indexed()] = Field(default_factory=datetime.now)
    updated_at: Annotated[datetime, Indexed()] = Field(default_factory=datetime.now)
