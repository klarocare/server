from typing import Any
from bson import ObjectId
from pydantic_core import CoreSchema
from pydantic import GetJsonSchemaHandler

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, *args):  # Modified to accept variable arguments
        if not isinstance(value, ObjectId):
            if not ObjectId.is_valid(value):
                raise ValueError('Invalid ObjectId')
            value = ObjectId(value)
        return value

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Any,
    ) -> CoreSchema:
        return CoreSchema.json_or_python_schema(
            json_schema=CoreSchema.str_schema(),
            python_schema=CoreSchema.union_schema([
                CoreSchema.is_instance_schema(ObjectId),
                CoreSchema.str_schema(),
            ]),
            serialization=CoreSchema.plain_serializer_function_schema(
                lambda x: str(x)
            ),
        )