import json
import logging
from datetime import datetime, timedelta

from fastapi import Query, APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse

from services.whatsapp.service import WhatsappService
from models.whatsapp import WhatsappUser
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
        return JSONResponse(content=response_body, status_code=status_code)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON provided")


def create_session_checker(whatsapp_service: WhatsappService):
    """
    Create a session checker function with the provided WhatsApp service
    """
    async def check_user_sessions():
        """
        Check user sessions and end inactive ones
        """
        try:
            current_time = datetime.now()
            inactive_threshold = current_time - timedelta(minutes=15)

            # Find inactive sessions
            inactive_sessions = await WhatsappUser.find(
                WhatsappUser.last_active < inactive_threshold,
                WhatsappUser.is_active == True
            ).to_list()

            # Process and end inactive sessions
            inactive_count = 0
            for session in inactive_sessions:
                try:
                    # End the user session through WhatsApp
                    await whatsapp_service.end_user_session(session)
                    logging.info(f"Ended session for WhatsApp ID: {session.whatsapp_id}. "
                              f"Last active: {session.last_active}")
                    inactive_count += 1
                except Exception as e:
                    logging.error(f"Error ending session for WhatsApp ID {session.whatsapp_id}: {str(e)}")

            logging.info(f"Processed {inactive_count} inactive sessions")

        except Exception as e:
            logging.error(f"Error checking user sessions: {str(e)}")

    return check_user_sessions