from fastapi import HTTPException, status
from passlib.context import CryptContext

from models.user import UserCredentials
from schemas.auth_schema import RegisterRequest, LoginRequest, TokenSchema
from core.auth import AuthHandler


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    async def register(self, data: RegisterRequest) -> TokenSchema:
        if data.password != data.password_confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords don't match"
            )
            
        if await UserCredentials.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
            
        user = UserCredentials(
            email=data.email,
            hashed_password=self.get_password_hash(data.password),
        )
        await user.insert()
        
        return TokenSchema(
            access_token=AuthHandler.create_access_token(str(user.id))
        )

    async def login(self, data: LoginRequest) -> TokenSchema:
        user = await UserCredentials.get_by_email(data.email)
        if not user or not self.verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
            
        return TokenSchema(
            access_token=AuthHandler.create_access_token(str(user.id))
        ) 