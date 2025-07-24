from typing import List, Optional
from beanie import Document
from pydantic import Field
from bson import ObjectId

class InboxItem(Document):
    # Remove manual id, use MongoDB's default _id
    status: str = Field(..., description="Status of the item, e.g., 'Neu' or 'In Bearbeitung'")
    name: str = Field(..., description="Name associated with the item")
    desc: str = Field(..., description="Description of the item")
    sub: Optional[str] = Field(None, description="Optional sub-status or assignee")
    actions: List[str] = Field(..., description="Available actions for the item")

    class Settings:
        name = "inbox_items" 