from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

from core.config import settings
from services.callback_service import request_callback

load_dotenv()

llm = AzureChatOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT, 
        api_version=settings.AZURE_OPENAI_API_VERSION,
        api_key=settings.AZURE_OPENAI_API_KEY,
        model=settings.AZURE_OPENAI_DEPLOYMENT,
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
    ).bind_tools([request_callback])
