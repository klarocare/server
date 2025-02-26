from services.rag_service import RAGService
from models.user import UserCredentials
from schemas.rag_schema import Language


class ChatService:
    
    def __init__(self):
        self.service = RAGService()
    
    def query(self, user: UserCredentials, message: str):
        # TODO: Get the language and the chat history from the user instance
        lang = Language.ENGLISH
        chat_history = []
        return self.service.query(message, chat_history, lang)
