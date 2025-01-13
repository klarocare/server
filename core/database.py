#core/database.py
import os
import logging
from typing import ClassVar

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure


logger = logging.getLogger(__name__)

class Database:
    _instance: ClassVar[AsyncIOMotorClient] = None
    
    @classmethod
    async def initialize(cls):
        if not cls._instance:
            try:
                cls._instance = AsyncIOMotorClient(os.getenv("MONGODB_URI"))

                # Verify connection
                await cls._instance.admin.command('ping')
                logger.info("Connected to MongoDB successfully")
            except ConnectionFailure as e:
                logger.error(f"Could not connect to MongoDB: {e}")
                raise
    
    @classmethod
    async def close_db(cls):
        if cls._instance is not None:
            cls._instance.close()
            logger.info("MongoDB connection closed")
    
    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        if cls._instance is not None:
            raise RuntimeError("Database not initialized")
        return cls._instance.chat_db
