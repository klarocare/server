from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from models.user import User
from core.config import settings
from schemas.auth_schema import TokenPayload


class AuthHandler:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    
    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
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
            
        user = await User.get(user_id)
        if user is None:
            raise credentials_exception
        return user

    @staticmethod
    def create_access_token(user_id: str) -> str:
        expires_delta = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {"sub": str(user_id), "exp": expires_delta.timestamp()}
        return jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
