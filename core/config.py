import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_REFRESH_SECRET_KEY: str = os.getenv("JWT_REFRESH_SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database Settings
    MONGODB_URI: str = os.getenv("MONGODB_URI")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME")
    
    # Azure OpenAI Settings
    AZURE_OPENAI_API_KEY: str | None = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: str | None = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION: str | None = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_DEPLOYMENT: str | None = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    # WhatsApp Settings
    WHATSAPP_ACCESS_TOKEN: str | None = os.getenv("WHATSAPP_ACCESS_TOKEN")
    WHATSAPP_ID: str | None = os.getenv("WHATSAPP_ID")
    WHATSAPP_SECRET: str | None = os.getenv("WHATSAPP_SECRET")
    RECIPIENT_WAID: str | None = os.getenv("RECIPIENT_WAID")
    WHATSAPP_VERSION: str | None = os.getenv("WHATSAPP_VERSION")
    WHATSAPP_PHONE_NUMBER_ID: str | None = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    WHATSAPP_VERIFY_TOKEN: str | None = os.getenv("WHATSAPP_VERIFY_TOKEN")
    
    
    class Config:
        env_file = ".env"

settings = Settings() 