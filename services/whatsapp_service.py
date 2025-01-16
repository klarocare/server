import logging
import json
import requests
import re
import os

from tenacity import retry, stop_after_attempt, wait_fixed

from services.rag_service import RAGService
from services.base_chat_service import BaseChatService

class WhatsappService(BaseChatService):
    def __init__(self):
        super().__init__()

    def verify(self, mode: str, token: str, challenge: str) -> str:
        """
        Verify the webhook token and return the challenge string.
        """
        if mode == "subscribe" and token == os.environ.get("VERIFY_TOKEN"):
            logging.info("WEBHOOK_VERIFIED")
            return challenge
        logging.info("VERIFICATION_FAILED")
        raise ValueError("Verification failed")

    async def handle_message(self, body):
        """
        Handle incoming webhook events from the WhatsApp API.
        """
        logging.info(f"Received webhook payload: {body}")

        if self._is_status_update(body):
            logging.info("Received a WhatsApp status update.")
            return json.dumps({"status": "ok"}), 200

        if self._is_valid_whatsapp_message(body):
            response = await self._process_whatsapp_message(body)
            return response, 200
        else:
            return json.dumps({"status": "error", "message": "Not a WhatsApp API event"}), 404

    def _is_status_update(self, body):
        """
        Check if the webhook payload contains a status update.
        """
        return (
            body.get("entry", [{}])[0]
            .get("changes", [{}])[0]
            .get("value", {})
            .get("statuses")
        )

    def _is_valid_whatsapp_message(self, body):
        """
        Check if the incoming webhook event has a valid WhatsApp message structure.
        """
        return (
            body.get("object")
            and body.get("entry")
            and body["entry"][0].get("changes")
            and body["entry"][0]["changes"][0].get("value")
            and body["entry"][0]["changes"][0]["value"].get("messages")
        )

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _send_message(self, data):
        """
        Send a message using the WhatsApp Cloud API with retry logic.
        """
        headers = {
            "Content-type": "application/json", 
            "Authorization": f"Bearer {os.environ.get('ACCESS_TOKEN')}",
        }
        url = f"https://graph.facebook.com/{os.environ.get('VERSION')}/{os.environ.get('PHONE_NUMBER_ID')}/messages"

        response = requests.post(url, data=data, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an exception for non-2xx responses
        logging.info(f"Message sent successfully: {response.json()}")
        return response

    def _process_text_for_whatsapp(self, text):
        """
        Format text for WhatsApp by replacing styling markers.
        """
        # Remove brackets
        text = re.sub(r"【.*?】", "", text).strip()
        
        # Replace bold (**word**) with WhatsApp bold (*word*)
        # Fixed pattern to properly handle the bold syntax
        text = re.sub(r"\*\*(.*?)\*\*", r"*\1*", text)
        return text

    async def _process_whatsapp_message(self, body):
        """
        Process a valid WhatsApp message and generate a response using RAG.
        """
        wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
        message_body = body["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

        response_answer = await self.process_chat_message(user_id=wa_id, message_body=message_body)

        # Format response for WhatsApp
        formatted_response = self._process_text_for_whatsapp(response_answer)
        data = self._get_text_message_input(wa_id, formatted_response)
        self._send_message(data)
        return data

    def _get_text_message_input(self, recipient, text):
        """
        Generate the payload for sending a WhatsApp text message.
        """
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "text",
                "text": {"preview_url": False, "body": text},
            }
        )
