import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure


logger = logging.getLogger(__name__)

class DatabaseConfig:
    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def connect_db(cls, mongodb_url: str):
        try:
            cls.client = AsyncIOMotorClient(mongodb_url)
            cls.db = cls.client.chatbot_db
            
            # Verify connection
            await cls.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
            
            return cls.db
        except ConnectionFailure as e:
            logger.error(f"Could not connect to MongoDB: {e}")
            raise

    @classmethod
    async def close_db(cls):
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")

    @classmethod
    async def get_db(cls):
        return cls.db