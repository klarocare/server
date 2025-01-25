import json

from fastapi import Query, APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse

from services.whatsapp_service import WhatsappService
from utils.security import verify_signature

router = APIRouter(
    prefix="/webhook",
    tags=["webhook"],
    responses={404: {"description": "Not found"}},
)

service = WhatsappService()

@router.get("", response_class=PlainTextResponse)
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
):
    """
    Verify webhook as required by WhatsApp.
    """
    try:
        challenge_response = service.verify(hub_mode, hub_verify_token, hub_challenge)
        return challenge_response
    except ValueError as e:
        raise HTTPException(
            status_code=403, 
            detail={"status": "error", "message": str(e)}
        )

@router.post("")
async def handle_webhook(background_tasks: BackgroundTasks, body_str: str = Depends(verify_signature)):
    """
    Handle incoming webhook events from WhatsApp.
    """
    try:
        body = json.loads(body_str)
        response_body, status_code = await service.handle_message(body, background_tasks)
        return JSONResponse(content=json.loads(response_body), status_code=status_code)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON provided")
