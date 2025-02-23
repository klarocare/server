from typing import Tuple, Dict, Any


class WhatsAppMessageHandler:
    """Handles message processing and validation for WhatsApp service"""
    
    @staticmethod
    def is_status_update(body: Dict[str, Any]) -> bool:
        """Check if the webhook payload contains a status update."""
        return bool(
            body.get("entry", [{}])[0]
            .get("changes", [{}])[0]
            .get("value", {})
            .get("statuses")
        )

    @staticmethod
    def is_valid_message(body: Dict[str, Any]) -> bool:
        """Validate WhatsApp message structure."""
        return bool(
            body.get("object")
            and body.get("entry")
            and body["entry"][0].get("changes")
            and body["entry"][0]["changes"][0].get("value")
            and body["entry"][0]["changes"][0]["value"].get("messages")
        )

    @staticmethod
    def extract_message_content(body: Dict[str, Any]) -> str:
        """Extract message content based on message type."""
        message = body["entry"][0]["changes"][0]["value"]["messages"][0]
        msg_type = message["type"]
        
        if msg_type == "button":
            return message["button"]["text"]
        elif msg_type == "text":
            return message["text"]["body"]
        return "Error handling the message"

    @staticmethod
    def get_message_metadata(body: Dict[str, Any]) -> Tuple[str, str]:
        """Extract message metadata."""
        wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
        object_id = body["entry"][0]["changes"][0]["value"]["messages"][0]["id"]
        return wa_id, object_id