from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT Settings
    JWT_SECRET_KEY: str = "your-secret-key" # TODO: Change this to a secret key environment variable
    JWT_REFRESH_SECRET_KEY: str = "your-refresh-secret-key" # TODO: Change this to a secret key environment variable
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database Settings
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "klarocare"
    
    # Azure OpenAI Settings
    AZURE_OPENAI_API_KEY: str | None = None
    AZURE_OPENAI_ENDPOINT: str | None = None
    AZURE_OPENAI_API_VERSION: str | None = None
    
    # Server Settings
    PORT: str | None = "8000"
    HOST: str | None = "0.0.0.0"
    
    class Config:
        env_file = ".env"

settings = Settings() 