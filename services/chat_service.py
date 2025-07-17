from services.rag_service import RAGService
from models.user import User
from models.chat import ChatMessage
from schemas.rag_schema import PublicChatRequest, RAGMessage


class ChatService:
    
    def __init__(self):
        self.service = RAGService()
    
    async def query(self, user: User, message: str):
        chat_history = await user.get_recent_messages()
        formatted_history = [{"role": msg.role, "content": msg.content} for msg in chat_history]

        response = self.service.query(message=message, chat_history=formatted_history, language=user.language)
        
        # Save user message
        msg = ChatMessage(
            user_id=user.id,
            role="user",
            content=message,
        )
        await msg.insert()

        # Save assistant message
        response_msg = ChatMessage(
            user_id=user.id,
            role="assistant",
            content=response.answer,
        )
        await response_msg.insert()

        return response

    async def public_query(self, request: PublicChatRequest):
        """Handle public chat requests without authentication"""
        # Convert client chat history to the format expected by RAG service
        formatted_history = [{"role": msg.role, "content": msg.content} for msg in request.chat_history]

        response = self.service.query(
            message=request.message, 
            chat_history=formatted_history, 
            language=request.language
        )

        return response
