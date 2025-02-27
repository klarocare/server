from services.rag_service import RAGService
from models.user import UserCredentials, UserProfile


class ChatService:
    
    def __init__(self):
        self.service = RAGService()
    
    def query(self, user_credentials: UserCredentials, message: str):
        user: UserProfile = user_credentials.get_user()
        return self.service.query(message=message, chat_history=[], language=user.language)
