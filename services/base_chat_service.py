from utils.constants import CHAT_HISTORY_LIMIT
from services.rag_service import RAGService
from models.chat import UserSession, ChatMessage


class BaseChatService:
    def __init__(self):
        self.rag_service = RAGService.get_instance()

    async def process_chat_message(self, user_id, wa_id: str, object_id, message_body: str) -> str:
        """
        Generic method to process a chat message, save it to the database,
        query the RAG service, and return a response.
        """
        msg = ChatMessage(
                session_id=user_id,
                whatsapp_id=wa_id,
                role="user",
                object_id=object_id,
                content=message_body,
            )
        # Save user message
        await msg.insert()

        # Get the recent messages as a list
        chat_history = await ChatMessage.get_recent_messages(whatsapp_id=wa_id, limit=CHAT_HISTORY_LIMIT)
        formatted_history = [{"role": msg.role, "content": msg.content} for msg in reversed(chat_history)]

        # Generate response using RAG service
        response = self.rag_service.query(message=message_body, chat_history=formatted_history)

        # Save assistant message
        response_msg = ChatMessage(
            session_id=user_id,
            whatsapp_id=wa_id,
            role="assistant",
            content=response.answer,
            )
        await response_msg.insert()

        return response.answer
