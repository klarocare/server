from datetime import datetime, timedelta, UTC

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from models.user import UserCredentials
from core.config import settings
from schemas.auth_schema import TokenPayload, TokenType


class AuthHandler:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    
    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserCredentials:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            token_data = TokenPayload(**payload)
            if datetime.fromtimestamp(token_data.exp) < datetime.now():
                raise credentials_exception
        except JWTError:
            raise credentials_exception
            
        user = await UserCredentials.get(user_id)
        if user is None:
            raise credentials_exception
        return user

    @staticmethod
    def create_access_token(user_id: str) -> str:
        expires_delta = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {"sub": str(user_id), "exp": expires_delta.timestamp(), "token_type": TokenType.ACCESS}
        return jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        expires_delta = datetime.now(UTC) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        to_encode = {"sub": str(user_id), "exp": expires_delta.timestamp(), "token_type": TokenType.REFRESH}
        return jwt.encode(
            to_encode, 
            settings.JWT_REFRESH_SECRET_KEY, 
            algorithm=settings.ALGORITHM
        ) 
    
    @staticmethod
    def verify_token(token: str, expected_token_type: TokenType) -> str | None:
        """Verify a JWT token."""
        try:
            secret_key = settings.JWT_SECRET_KEY if expected_token_type is TokenType.ACCESS else settings.JWT_REFRESH_SECRET_KEY

            payload = jwt.decode(token, secret_key, algorithm=settings.ALGORITHM)
            user_id: str = payload.get("sub")
            token_type: str = payload.get("token_type")
            
            if user_id is None or token_type != expected_token_type:
                return None
                
            return user_id

        except JWTError:
            return None
