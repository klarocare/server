import re
import json
import os

from schemas.rag_schema import Language


class WhatsAppMessageFormatter:
    """Handles message formatting and template management for WhatsApp"""
    
    @staticmethod
    def process_text_for_whatsapp(text: str) -> str:
        """Format text for WhatsApp by replacing styling markers."""
        text = re.sub(r"【.*?】", "", text).strip()
        text = re.sub(r"\*\*(.*?)\*\*", r"*\1*", text)
        return text

    @staticmethod
    def create_message_payload(recipient: str, text: str, preview_url: bool = False) -> str:
        """Generate the payload for sending a WhatsApp text message."""
        return json.dumps({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": preview_url, "body": text},
        })

    @staticmethod
    def get_template_message(recipient: str, template_name: str, language: Language = Language.GERMAN) -> str:
        """Generate message payload from template file."""
        template_path = os.path.join(f'utils/templates/{template_name}_{language.value}.txt')
        with open(template_path, 'r') as file:
            text = file.read()
        return WhatsAppMessageFormatter.create_message_payload(recipient, text)