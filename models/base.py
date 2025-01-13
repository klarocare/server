from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from utils.object_id import PyObjectId

class MongoModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId: str},
        populate_by_name=True
    )