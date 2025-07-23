from fastapi import APIRouter, HTTPException
import logging
from schemas.callback_schema import CallbackRequest, CallbackResponse
from services.sheets_service import GoogleSheetsService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize service
sheets_service = GoogleSheetsService()

router = APIRouter(
    prefix="/callback",
    tags=["callback"],
    responses={404: {"description": "Not found"}},
)


@router.post("/request", response_model=CallbackResponse)
async def create_callback_request(request: CallbackRequest):
    """
    Create a new callback request and add it to Google Sheets.
    
    This endpoint accepts a topic and phone number, then records the request
    in a Google Sheets document for follow-up.
    """
    try:
        logger.info(f"Received callback request: {request.topic} - {request.phone_number}")
        
        # Add the callback request to Google Sheets
        result = sheets_service.add_callback_request(request)
        
        if result["success"]:
            return CallbackResponse(
                success=True,
                message=result["message"]
            )
        else:
            # Return success even if Google Sheets fails, but log the issue
            logger.warning(f"Google Sheets error: {result['message']}")
            return CallbackResponse(
                success=True,
                message="Callback request received. We'll contact you soon."
            )
            
    except Exception as e:
        logger.error(f"Error processing callback request: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing callback request"
        )


@router.get("/requests")
async def get_callback_requests():
    """
    Get all callback requests from Google Sheets.
    
    This endpoint retrieves all recorded callback requests for administrative purposes.
    """
    try:
        result = sheets_service.get_all_callback_requests()
        
        if result["success"]:
            return {
                "success": True,
                "data": result["data"],
                "message": result["message"]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result["message"]
            )
            
    except Exception as e:
        logger.error(f"Error retrieving callback requests: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving callback requests"
        )
