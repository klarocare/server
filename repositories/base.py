from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from bson import ObjectId
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from models.base import MongoModel
from core.database import Database


T = TypeVar('T', bound=MongoModel)

class MongoRepository(Generic[T]):
    """
    Generic MongoDB repository with singleton database connection
    """
    collection_name: str
    model: Type[T]
    
    def __init__(self, model: Type[T], collection_name: str):
        self.model = model
        self.collection_name = collection_name
    
    @property
    def db(self) -> AsyncIOMotorDatabase:
        """Get the database instance"""
        return Database.get_db()
    
    # TODO: Not so sure about these generated functions
    @property
    def collection(self) -> AsyncIOMotorCollection:
        """Get the collection for this repository"""
        return self.db[self.collection_name]

    async def create(self, model_in: T) -> T:
        """Create a new document"""
        model_dict = model_in.model_dump(by_alias=True)
        if "created_at" not in model_dict:
            model_dict["created_at"] = datetime.now()
        model_dict["updated_at"] = datetime.now()
        
        result = await self.collection.insert_one(model_dict)
        return await self.get_by_id(str(result.inserted_id))

    async def get_by_id(self, id: str) -> Optional[T]:
        """Get a document by ID"""
        if not ObjectId.is_valid(id):
            return None
        result = await self.collection.find_one({"_id": ObjectId(id)})
        return self.model.model_validate(result) if result else None

    async def get_by_field(self, field: str, value: Any) -> Optional[T]:
        """Get a document by any field"""
        result = await self.collection.find_one({field: value})
        return self.model.model_validate(result) if result else None

    async def update(self, id: str, update_data: Dict[str, Any]) -> Optional[T]:
        """Update a document"""
        if not ObjectId.is_valid(id):
            return None
        
        update_data["updated_at"] = datetime.now()
        result = await self.collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )
        if result.modified_count:
            return await self.get_by_id(id)
        return None

    async def delete(self, id: str) -> bool:
        """Delete a document"""
        if not ObjectId.is_valid(id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

