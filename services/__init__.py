from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()


llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini", 
    api_version="2024-08-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
    )