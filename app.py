import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from beanie import init_beanie

from models.chat import ChatMessage, UserSession
from core.database import Database
from routes import care_task_api, rag_api, whatsapp_api


for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database connection
    await Database.initialize()
    await init_beanie(database=Database._instance.db_name, document_models=[ChatMessage, UserSession])
    yield
    # Close database connection
    await Database.close_db()

app = FastAPI(root_path="/api", lifespan=lifespan)

app.include_router(rag_api.router)
app.include_router(care_task_api.router)
app.include_router(whatsapp_api.router)

@app.get("/health-check")
async def root():
    return {"message": "ok"}
