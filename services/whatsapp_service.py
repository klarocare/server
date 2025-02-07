import logging
import json
import requests
import re
import os

from services.base_chat_service import BaseChatService
from models.chat import UserSession, ChatMessage


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

    async def handle_message(self, body, background_tasks):
        """
        Handle incoming webhook events from the WhatsApp API.
        """
        logging.info(f"Received webhook payload: {body}")

        if self._is_status_update(body):
            logging.info("Received a WhatsApp status update.")
            return json.dumps({"status": "ok"}), 200

        if self._is_valid_whatsapp_message(body):
            background_tasks.add_task(self.process_message_background, body)
            return json.dumps({"status": "accepted"}), 200
        else:
            return json.dumps({"status": "error", "message": "Not a WhatsApp API event"}), 404
    
    async def process_message_background(self, body):
        """
        Process message in background
        """
        self._send_read_message(body)
        try:
            # Check for duplicate message
            object_id, is_existing = await self._check_if_existing_message(body)
            
            if is_existing:
                logging.info(f"Message with object id {object_id} already exists")
                return

            await self._process_whatsapp_message(body)
        except Exception as e:
            logging.error(f"Error processing message in background: {str(e)}")

    def _send_read_message(self, body):
        """
        Send a read request using the WhatsApp Cloud API.
        """
        message_id = body["entry"][0]["changes"][0]["value"]["messages"][0]["id"]
        data = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        headers = {
            "Content-type": "application/json", 
            "Authorization": f"Bearer {os.environ.get('ACCESS_TOKEN')}",
        }
        url = f"https://graph.facebook.com/{os.environ.get('VERSION')}/{os.environ.get('PHONE_NUMBER_ID')}/messages"
        logging.info(f"Sending read request for message: {message_id}")

        response = requests.post(url, data=data, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an exception for non-2xx responses
        logging.info(f"Read request sent successfully: {response.json()}")

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
        and if the message has already been received befored, if so ignore the message.
        """
        return (
            body.get("object")
            and body.get("entry")
            and body["entry"][0].get("changes")
            and body["entry"][0]["changes"][0].get("value")
            and body["entry"][0]["changes"][0]["value"].get("messages")
        )

    def _send_message(self, data):
        """
        Send a message using the WhatsApp Cloud API with retry logic.
        """
        headers = {
            "Content-type": "application/json", 
            "Authorization": f"Bearer {os.environ.get('ACCESS_TOKEN')}",
        }
        url = f"https://graph.facebook.com/{os.environ.get('VERSION')}/{os.environ.get('PHONE_NUMBER_ID')}/messages"
        logging.info(f"Sending message with data : {data}")

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

    def _extract_whatsapp_message(self, body):
        msg_type = body["entry"][0]["changes"][0]["value"]["messages"][0]["type"]
        match msg_type:
            case 'button':
                return body["entry"][0]["changes"][0]["value"]["messages"][0]["button"]["text"]
            case 'text':
                return body["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
            case _:
                return "Error handling the message"
    
    async def _check_if_existing_message(self, body):
        object_id = body["entry"][0]["changes"][0]["value"]["messages"][0]["id"]

        # Check for original message's response
        msg = await ChatMessage.get_message_by_object_id(object_id)
        response_msg = await ChatMessage.get_message_by_object_id(f"response_{object_id}")
        
        if msg or response_msg:
            return object_id, True
        return object_id, False


    async def _process_whatsapp_message(self, body):
        """
        Process a valid WhatsApp message and generate a response using RAG.
        """
        wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
        object_id = body["entry"][0]["changes"][0]["value"]["messages"][0]["id"]

        message_body = self._extract_whatsapp_message(body)
        
        # Get user session
        user, is_new_user = await UserSession.get_or_create_session(wa_id)

        # Prepare a welcoming template message if the user is new, else from RAG pipeline
        if is_new_user:
            data = self._get_welcoming_message_input(wa_id)
        else:
            response = await self.process_chat_message(user, object_id, message_body)
            formatted_answer = self._process_text_for_whatsapp(response.answer)
            is_preview_url = True if response.video_URLs else False
            # Format response for WhatsApp
            data = self._get_text_message_input(wa_id, formatted_answer, is_preview_url)
        
        self._send_message(data)

    def _get_text_message_input(self, recipient, text, is_preview_url):
        """
        Generate the payload for sending a WhatsApp text message.
        """
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "text",
                "text": {"preview_url": is_preview_url, "body": text},
            }
        )

    def _get_welcoming_message_input(self, recipient):
        """
        Generate the payload for sending a welcoming WhatsApp text message.
        """
        with open(os.path.join('utils/templates/welcoming_msg.txt'), 'r') as file:
            text = file.read()
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "text",
                "text": {"preview_url": False, "body": text},
            }
        )
