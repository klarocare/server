from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langfuse import get_client
from dotenv import load_dotenv


load_dotenv()
langfuse = get_client()

chat_prompt = langfuse.get_prompt("chat").prompt
chat_no_context_prompt = langfuse.get_prompt("chat_no_context").prompt
classifier_prompt = langfuse.get_prompt("classifier").prompt
summary_prompt = ChatPromptTemplate.from_messages([
    ("system", langfuse.get_prompt("summary").prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")]
)
