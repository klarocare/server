from fastapi import APIRouter, HTTPException
from typing import List
from models.inbox import InboxItem

router = APIRouter()

@router.get("/inbox", response_model=List[InboxItem])
async def get_inbox_items():
    items = await InboxItem.find_all().to_list()
    return items 

@router.post("/inbox")
async def create_inbox_item(item: InboxItem):
    try:
        await item.insert()
        return {"success": True, "message": "Inbox item created successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 