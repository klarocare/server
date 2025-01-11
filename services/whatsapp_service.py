import logging
import json
import requests
import re
import os

class WhatsappService():

    def __init__(self):
        pass

    def handle_message(self, body):
        """
        Handle incoming webhook events from the WhatsApp API.

        This function processes incoming WhatsApp messages and other events,
        such as delivery statuses. If the event is a valid message, it gets
        processed. If the incoming payload is not a recognized WhatsApp event,
        an error is returned.

        Every message send will trigger 4 HTTP requests to your webhook: message, sent, delivered, read.

        Returns:
            response: A tuple containing a JSON response and an HTTP status code.
        """
        logging.info(f"request body: {body}")

        # Check if it's a WhatsApp status update
        if (
            body.get("entry", [{}])[0]
            .get("changes", [{}])[0]
            .get("value", {})
            .get("statuses")
        ):
            logging.info("Received a WhatsApp status update.")
            return json.dumps({"status": "ok"}), 200

        print(body)
        # Process valid WhatsApp messages
        if self._is_valid_whatsapp_message(body):
            self._process_whatsapp_message(body)
            return json.dumps({"status": "ok"}), 200
        else:
            return json.dumps({"status": "error", "message": "Not a WhatsApp API event"}), 404

    def verify(self, mode: str, token: str, challenge: str) -> str:
        """
        Verify the webhook token and return the challenge string
        """
        if mode == "subscribe" and token == os.environ.get("VERIFY_TOKEN"):
            logging.info("WEBHOOK_VERIFIED")
            return challenge
        logging.info("VERIFICATION_FAILED")
        raise ValueError("Verification failed")


    def _log_http_response(self, response):
        logging.info(f"Status: {response.status_code}")
        logging.info(f"Content-type: {response.headers.get('content-type')}")
        logging.info(f"Body: {response.text}")


    def _get_text_message_input(self, recipient, text):
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "text",
                "text": {"preview_url": False, "body": text},
            }
        )


    def _generate_response(self, response):
        # Return text in uppercase
        return response.upper()


    def _send_message(self, data):
        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {os.environ.get('ACCESS_TOKEN')}",
        }

        url = f"https://graph.facebook.com/{os.environ.get('VERSION')}/{os.environ.get('PHONE_NUMBER_ID')}/messages"

        try:
            response = requests.post(
                url, data=data, headers=headers, timeout=10
            )  # 10 seconds timeout as an example
            response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        except requests.Timeout:
            logging.error("Timeout occurred while sending message")
            return json.dumps({"status": "error", "message": "Request timed out"}), 408
        except (
            requests.RequestException
        ) as e:  # This will catch any general request exception
            logging.error(f"Request failed due to: {e}")
            return json.dumps({"status": "error", "message": "Failed to send message"}), 500
        else:
            # Process the response as normal
            self._log_http_response(response)
            return response


    def _process_text_for_whatsapp(self, text):
        # Remove brackets
        pattern = r"\【.*?\】"
        # Substitute the pattern with an empty string
        text = re.sub(pattern, "", text).strip()

        # Pattern to find double asterisks including the word(s) in between
        pattern = r"\*\*(.*?)\*\*"

        # Replacement pattern with single asterisks
        replacement = r"*\1*"

        # Substitute occurrences of the pattern with the replacement
        whatsapp_style_text = re.sub(pattern, replacement, text)

        return whatsapp_style_text


    def _process_whatsapp_message(self, body):
        wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
        # TODO: We could also use the name here
        name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

        message = body["entry"][0]["changes"][0]["value"]["messages"][0]
        message_body = message["text"]["body"]

        # TODO: implement custom function here
        response = self._generate_response(message_body)

        # OpenAI Integration
        # response = generate_response(message_body, wa_id, name)
        # response = process_text_for_whatsapp(response)

        data = self._get_text_message_input(wa_id, response)
        self._send_message(data)


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
            and body["entry"][0]["changes"][0]["value"]["messages"][0]
        )