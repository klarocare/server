from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

from core.config import settings

load_dotenv()


llm = AzureChatOpenAI(
    azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT, 
    api_version=settings.AZURE_OPENAI_API_VERSION,
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
    )