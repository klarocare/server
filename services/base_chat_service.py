import logging

from utils.constants import CHAT_HISTORY_LIMIT
from services.rag_service import RAGService
from models.chat import UserSession, ChatMessage
from schemas.rag_schema import Language


class BaseChatService:
    def __init__(self):
        # this easily can be changed to RAGService as well
        self.service = RAGService()

    def update_service_language(self):
        self.service.update_language(Language.ENGLISH) # TODO: Generalize this to other languages

    async def process_chat_message(self, user: UserSession, object_id: str, message_body: str) -> str:
        # Get chat history
        chat_history = await ChatMessage.get_recent_messages(whatsapp_id=user.whatsapp_id, limit=CHAT_HISTORY_LIMIT)
        formatted_history = [{"role": msg.role, "content": msg.content} for msg in chat_history]

        # Generate response
        response = self.service.query(message=message_body, chat_history=formatted_history)
        logging.info(f"Response of the RAG: {response.answer}")

        # Save user message with object_id
        msg = ChatMessage(
            session_id=user.id,
            whatsapp_id=user.whatsapp_id,
            role="user",
            object_id=object_id,
            content=message_body,
        )
        await msg.insert()

        # Save assistant message with reference to original message
        response_msg = ChatMessage(
            session_id=user.id,
            whatsapp_id=user.whatsapp_id,
            role="assistant",
            object_id=f"response_{object_id}",  # Link response to original message
            content=response.answer,
        )
        await response_msg.insert()

        return response
