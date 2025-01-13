from repositories.chat import MessageRepository, SessionRepository
from schemas.chat_schema import ChatMessage
from utils.constants import CHAT_HISTORY_LIMIT
from services.rag_service import RAGService


class BaseChatService:
    def __init__(self, rag_service: RAGService):
        self.session_repo = SessionRepository()
        self.message_repo = MessageRepository()
        self.rag_service = rag_service

    async def process_chat_message(self, user_id: str, message_body: str) -> str:
        """
        Generic method to process a chat message, save it to the database,
        query the RAG service, and return a response.
        """
        # Get or create user session
        session = await self.session_repo.get_or_create_session(user_id)

        # Save user message
        await self.message_repo.create(
            ChatMessage(
                session_id=session.id,
                whatsapp_id=user_id,
                role="user",
                content=message_body,
            )
        )

        # Retrieve chat history
        chat_history = await self.message_repo.get_recent_messages(
            whatsapp_id=user_id,
            limit=CHAT_HISTORY_LIMIT
        )
        formatted_history = [{"role": msg.role, "content": msg.content} for msg in reversed(chat_history)]

        # Generate response using RAG service
        response = await self.rag_service.query(message=message_body, chat_history=formatted_history)

        # Save assistant message
        await self.message_repo.create(
            ChatMessage(
                session_id=session.id,
                whatsapp_id=user_id,
                role="assistant",
                content=response.answer,
            )
        )

        return response.answer
