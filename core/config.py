import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
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
    
    # SMTP Settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SMTP_SENDER: str = os.getenv("SMTP_SENDER")
    BASE_URL: str = os.getenv("BASE_URL")
    
    # Google Sheets Settings
    GOOGLE_SHEETS_CREDENTIALS: str | None = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    GOOGLE_SHEETS_CREDENTIALS_FILE: str | None = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE")
    GOOGLE_SHEETS_SPREADSHEET_ID: str | None = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
    
    @classmethod
    def reload_env(cls):
        """Force reload environment variables"""
        # Clear existing environment variables
        env_vars = [
            "JWT_SECRET_KEY", "ALGORITHM", "MONGODB_URI", "DATABASE_NAME",
            "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_DEPLOYMENT", "WHATSAPP_ACCESS_TOKEN", "WHATSAPP_ID",
            "WHATSAPP_SECRET", "RECIPIENT_WAID", "WHATSAPP_VERSION",
            "WHATSAPP_PHONE_NUMBER_ID", "WHATSAPP_VERIFY_TOKEN", "SMTP_HOST",
            "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_SENDER", "BASE_URL",
            "GOOGLE_SHEETS_CREDENTIALS", "GOOGLE_SHEETS_CREDENTIALS_FILE", "GOOGLE_SHEETS_SPREADSHEET_ID"
        ]
        
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
        
        # Reload from .env file
        load_dotenv(override=True)
        
        # Return new instance with fresh values
        return cls()
    
    class Config:
        env_file = ".env"

# Initialize settings with fresh environment
settings = Settings() 