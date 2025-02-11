import os
import logging
import hashlib
import hmac

from fastapi import  Request, HTTPException


async def validate_signature(payload: str, signature: str) -> bool:
    """
    Validate the incoming payload's signature against our expected signature
    """
    expected_signature = hmac.new(
        bytes(os.environ.get("WHATSAPP_SECRET"), "latin-1"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

async def verify_signature(request: Request) -> str:
    """
    Dependency to verify signature and return the raw body
    """
    body = await request.body()
    body_str = body.decode("utf-8")
    
    signature = request.headers.get("X-Hub-Signature-256", "")[7:]  # Removing 'sha256='
    if not await validate_signature(body_str, signature):
        logging.info("Signature verification failed!")
        raise HTTPException(
            status_code=403,
            detail={"status": "error", "message": "Invalid signature"}
        )
    return body_str