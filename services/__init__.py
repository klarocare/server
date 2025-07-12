from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

from core.config import settings

load_dotenv()


def get_llm():
    """Get a fresh LLM instance with current settings"""
    return AzureChatOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT, 
        api_version=settings.AZURE_OPENAI_API_VERSION,
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )

# Initialize with fresh settings
llm = get_llm()