from pydantic import BaseModel, Field


class CallbackRequest(BaseModel):
    topic: str = Field(..., description="The topic or subject of the callback request")
    phone_number: str = Field(..., description="The phone number to call back")


class CallbackResponse(BaseModel):
    success: bool = Field(description="Whether the callback request was successfully recorded")
    message: str = Field(description="A message confirming the callback request") 