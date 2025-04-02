import logging
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from fastapi import FastAPI
from beanie import init_beanie
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from models.whatsapp import WhatsappChatMessage, WhatsappUser
from models.user import User, ChatMessage
from models.content import Article
from core.database import Database
from core.migrations.run_migrations import run_migrations
from routes import chat_api, whatsapp_api, auth_api, profile_api, content_api, care_level_api
from routes.whatsapp_api import create_session_checker, service as whatsapp_service


scheduler = AsyncIOScheduler()

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
load_dotenv(override=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database connection
    await Database.initialize()
    await init_beanie(
        database=Database._instance.db_name,
        document_models=[WhatsappChatMessage, WhatsappUser, User, ChatMessage, Article]
        )
    await run_migrations()

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
app.include_router(whatsapp_api.router)
app.include_router(auth_api.router)
app.include_router(profile_api.router)
app.include_router(content_api.router)
app.include_router(care_level_api.router)

@app.get("/health-check")
async def root():
    return {"message": "ok"}
