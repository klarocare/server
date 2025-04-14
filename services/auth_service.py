from fastapi import HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta
from secrets import token_urlsafe
import logging

from models.user import User
from schemas.auth_schema import RegisterRequest, LoginRequest, TokenSchema
from core.auth import AuthHandler
from services.email_service import EmailService


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.email_service = EmailService()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    async def register(self, data: RegisterRequest) -> dict:
        if data.password != data.password_confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords don't match"
            )
        
        logging.info(f"Step 1: Checking if email is already registered")
        if await User.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        logging.info(f"Step 2: Generating verification token")
        # Generate verification token
        verification_token = token_urlsafe(32)
        token_expires = datetime.now() + timedelta(hours=24)
        
        user = User(
            email=data.email,
            hashed_password=self.get_password_hash(data.password),
            username=data.name,
            language=data.language,
            verification_token=verification_token,
            verification_token_expires=token_expires,
            is_verified=False
        )
        logging.info(f"Step 3: Inserting user into database")
        await user.insert()
        
        # Send verification email
        logging.info(f"Step 4: Sending verification email")
        await self.email_service.send_verification_email(data.email, verification_token)
        
        return {
            "message": "Registration successful. Please check your email to verify your account.",
            "email": data.email
        }

    async def verify_email(self, token: str) -> dict:
        user = await User.get_by_verification_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )

        # Check if token is expired
        if user.verification_token_expires < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired"
            )

        # Update user verification status
        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires = None
        await user.save()

        return {
            "email": user.email
        }

    async def login(self, data: LoginRequest) -> TokenSchema:
        user = await User.get_by_email(data.email)
        if not user or not self.verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please verify your email before logging in"
            )
            
        return TokenSchema(
            access_token=AuthHandler.create_access_token(str(user.id))
        ) 