from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langfuse.langchain import CallbackHandler

from core.config import settings


load_dotenv(override=True)

langfuse_handler = CallbackHandler()

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
    )
