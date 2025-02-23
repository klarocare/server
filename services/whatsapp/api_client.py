import logging
import os
import requests
from typing import Dict, Any


class WhatsAppAPIClient:
    """Handles API communication with WhatsApp Cloud API"""
    
    def __init__(self):
        self.base_url = f"https://graph.facebook.com/{os.environ.get('WHATSAPP_VERSION')}/{os.environ.get('WHATSAPP_PHONE_NUMBER_ID')}"
        self.headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {os.environ.get('WHATSAPP_ACCESS_TOKEN')}",
        }

    def send_message(self, data: str) -> Dict[str, Any]:
        """Send a message using the WhatsApp Cloud API."""
        logging.info(f"Sending message with data: {data}")
        response = requests.post(
            f"{self.base_url}/messages",
            data=data,
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        logging.info(f"Message sent successfully: {response.json()}")
        return response.json()

    def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark a message as read."""
        data = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        response = requests.post(
            f"{self.base_url}/messages",
            json=data,
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()