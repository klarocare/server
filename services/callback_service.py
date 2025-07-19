from langchain_core.tools import tool             # LangChain ≥ 0.1.0
from pydantic import BaseModel, Field
import re

class CallbackPayload(BaseModel):
    """Information needed so the system can ring the user back."""
    conversation_summary: str = Field(..., description="A summary of the conversation that the user wants to discuss")


@tool(args_schema=CallbackPayload)
def request_callback(conversation_summary: str) -> str:
    """
    Queue a human callback to the user.
    Returns a short confirmation that will be shown to the end-user.
    The backend (outside the LLM) decides how to place the call.
    """
    # NOTE: the body of this function is *never* executed inside the LLM.
    # LangChain will hand the arguments back to YOUR Python code.
    # You’ll wire it up in step 4.
    raise NotImplementedError
