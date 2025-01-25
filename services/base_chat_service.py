import logging

from utils.constants import CHAT_HISTORY_LIMIT
from services.rag_service import RAGService
from models.chat import UserSession, ChatMessage


class BaseChatService:
    def __init__(self):
        self.rag_service = RAGService.get_instance()

    async def process_chat_message(self, user_id, wa_id: str, object_id, message_body: str) -> str:
        # Get chat history
        chat_history = await ChatMessage.get_recent_messages(whatsapp_id=wa_id, limit=CHAT_HISTORY_LIMIT)
        formatted_history = [{"role": msg.role, "content": msg.content} for msg in reversed(chat_history)]

        logging.info(formatted_history)

        # Generate response
        response = self.rag_service.query(message=message_body, chat_history=formatted_history)

        # Save user message with object_id
        msg = ChatMessage(
            session_id=user_id,
            whatsapp_id=wa_id,
            role="user",
            object_id=object_id,
            content=message_body,
        )
        await msg.insert()

        # Save assistant message with reference to original message
        response_msg = ChatMessage(
            session_id=user_id,
            whatsapp_id=wa_id,
            role="assistant",
            object_id=f"response_{object_id}",  # Link response to original message
            content=response.answer,
        )
        await response_msg.insert()

        return response.answer
