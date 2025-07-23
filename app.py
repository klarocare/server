import logging
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from beanie import init_beanie
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi.middleware.cors import CORSMiddleware

from models.inbox import InboxItem
from models.whatsapp import WhatsappChatMessage, WhatsappUser
from models.user import User, ChatMessage
from core.database import Database
from core.migrations.run_migrations import run_migrations
from routes import chat_api, whatsapp_api, auth_api, profile_api, care_level_api, callback_api
from routes.whatsapp_api import create_session_checker, service as whatsapp_service
from routes import inbox_api


scheduler = AsyncIOScheduler()

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Clear environment cache and reload
def clear_env_cache():
    """Clear environment variables that might be cached"""
    # Remove any existing .env variables from os.environ
    env_vars_to_clear = [
        "JWT_SECRET_KEY", "ALGORITHM", "MONGODB_URI", "DATABASE_NAME",
        "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_DEPLOYMENT", "WHATSAPP_ACCESS_TOKEN", "WHATSAPP_ID",
        "WHATSAPP_SECRET", "RECIPIENT_WAID", "WHATSAPP_VERSION",
        "WHATSAPP_PHONE_NUMBER_ID", "WHATSAPP_VERIFY_TOKEN", "SMTP_HOST",
        "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_SENDER", "BASE_URL",
        "GOOGLE_SHEETS_CREDENTIALS", "GOOGLE_SHEETS_CREDENTIALS_FILE", "GOOGLE_SHEETS_SPREADSHEET_ID"
    ]
    
    for var in env_vars_to_clear:
        if var in os.environ:
            del os.environ[var]
    
    # Reload environment variables
    load_dotenv(override=True)
    logger.info("Environment cache cleared and reloaded")

# Clear environment cache on startup
clear_env_cache()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database connection
    await Database.initialize()
    await init_beanie(
        database=Database._instance.db_name,
        document_models=[WhatsappChatMessage, WhatsappUser, User, ChatMessage, InboxItem]
        )
    # await run_migrations()

    # Initialize the clean-up scheduler
    try:
        check_sessions = create_session_checker(whatsapp_service)
        scheduler.add_job(
            check_sessions,
            CronTrigger(minute='*/15'),
            id="check_user_sessions",
            replace_existing=True
        )
        scheduler.start()
        logger.info("Started background scheduler for user session checking")
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
    
    yield
    # Close database connection
    await Database.close_db()

    # Shut down the scheduler
    scheduler.shutdown()
    logger.info("Shut down background scheduler")

app = FastAPI(root_path="/api", lifespan=lifespan)

app.include_router(chat_api.router)
#app.include_router(whatsapp_api.router)
#app.include_router(auth_api.router)
#app.include_router(profile_api.router)
#app.include_router(care_level_api.router)
app.include_router(callback_api.router)
app.include_router(inbox_api.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health-check")
async def root():
    return {"message": "ok"}
