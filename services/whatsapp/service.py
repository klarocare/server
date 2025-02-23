import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Tuple

from services.base_chat_service import BaseChatService
from services.whatsapp.message_handler import WhatsAppMessageHandler
from services.whatsapp.message_formatter import WhatsAppMessageFormatter
from services.whatsapp.api_client import WhatsAppAPIClient
from models.chat import UserSession, ChatMessage
from schemas.rag_schema import Language


class WhatsappService(BaseChatService):
    """Main WhatsApp service class"""
    
    def __init__(self):
        super().__init__()
        self.api_client = WhatsAppAPIClient()
        self.message_handler = WhatsAppMessageHandler()
        self.message_formatter = WhatsAppMessageFormatter()

    def verify(self, mode: str, token: str, challenge: str) -> str:
        """Verify the webhook token."""
        if mode == "subscribe" and token == os.environ.get("WHATSAPP_VERIFY_TOKEN"):
            logging.info("WEBHOOK_VERIFIED")
            return challenge
        logging.info("VERIFICATION_FAILED")
        raise ValueError("Verification failed")

    async def handle_message(self, body: Dict[str, Any], background_tasks) -> Tuple[str, int]:
        """Handle incoming webhook events."""
        logging.info(f"Received webhook payload: {body}")

        if self.message_handler.is_status_update(body):
            logging.info("Received a WhatsApp status update.")
            return json.dumps({"status": "ok"}), 200

        if self.message_handler.is_valid_message(body):
            background_tasks.add_task(self.process_message_background, body)
            return json.dumps({"status": "accepted"}), 200

        return json.dumps({"status": "error", "message": "Not a WhatsApp API event"}), 404

    async def process_message_background(self, body: Dict[str, Any]) -> None:
        """Process message in background."""
        wa_id, object_id = self.message_handler.get_message_metadata(body)
        
        try:
            self.api_client.mark_as_read(object_id)
            
            # Check for duplicate message
            if await self._is_duplicate_message(object_id):
                logging.info(f"Message with object id {object_id} already exists")
                return

            message_body = self.message_handler.extract_message_content(body)
            await self._handle_user_interaction(wa_id, object_id, message_body)
            
        except Exception as e:
            logging.error(f"Error processing message in background: {str(e)}")

    async def _handle_user_interaction(self, wa_id: str, object_id: str, message_body: str) -> None:
        """Handle user interaction and generate appropriate response."""
        user, is_new_user = await UserSession.get_or_create_session(wa_id)
        
        response_data = await self._determine_response(user, is_new_user, message_body, object_id)
        self.api_client.send_message(response_data)

    async def _determine_response(self, user: UserSession, is_new_user: bool, message_body: str, object_id: str) -> str:
        """Determine appropriate response based on user state and message content."""
        if not user.is_active:
            user.is_active = True
            await user.save()
            return self.message_formatter.get_template_message(user.whatsapp_id, "welcome_back_msg", user.language)
            
        if "privacy policy" in message_body.lower() or "datenschutzrichtlinie" in message_body.lower():
            return self.message_formatter.get_template_message(user.whatsapp_id, "privacy_policy", user.language)
            
        if "english" in message_body.lower():
            user.language = Language.ENGLISH
            await user.save()
            self.update_service_language(user.language)
            return self.message_formatter.get_template_message(user.whatsapp_id, "welcoming_msg", user.language)
            
        if is_new_user:
            return self.message_formatter.get_template_message(user.whatsapp_id, "welcoming_msg", user.language)
            
        # Handle regular chat message
        user.last_active = datetime.now()
        await user.save()
        
        response = await self.process_chat_message(user, object_id, message_body)
        formatted_answer = self.message_formatter.process_text_for_whatsapp(response.answer)
        return self.message_formatter.create_message_payload(
            user.whatsapp_id,
            formatted_answer,
            bool(response.video_URLs)
        )

    async def _is_duplicate_message(self, object_id: str) -> bool:
        """Check if message has already been processed."""
        msg = await ChatMessage.get_message_by_object_id(object_id)
        response_msg = await ChatMessage.get_message_by_object_id(f"response_{object_id}")
        return bool(msg or response_msg)

    async def end_user_session(self, user: UserSession) -> None:
        """End user session."""
        data = self.message_formatter.get_template_message(
            user.whatsapp_id,
            "goodbye_msg",
            user.language
        )
        self.api_client.send_message(data)
        user.is_active = False
        await user.save()