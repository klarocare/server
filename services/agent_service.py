import json
import os
import logging
import threading
import urllib.parse
from typing import List, Dict, TypedDict

import bs4
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, BaseMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition
from langchain_core.tools import tool
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.vectorstores import VectorStore
from langchain_community.document_loaders import PyPDFDirectoryLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore

from services import llm
from utils.constants import AGENT_CONFIG, GENERATION_FAILED_RESPONSE
from schemas.rag_schema import RAGResponse


# Type for managing conversation state
class MessagesState(TypedDict):
    messages: List[BaseMessage]
    chat_history: List[Dict]
    context: List[Document]


class AgentService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """Control the instantiation process."""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        logging.info("NEW VERSION ;)")
        self.config = AGENT_CONFIG
        self.video_store = self._load_video_store()
        self.vectorstore = self._setup_vectorstore()
        self.graph = self._create_graph()
        
    def _load_video_store(self) -> List[Dict]:
        """Load video information from JSON file."""
        with open(os.path.join(self.config['db_path'], 'videos.json')) as file:
            return json.load(file)
    
    def _setup_vectorstore(self) -> VectorStore:
        """Initialize and populate the vector store with documents and video content."""
        # Load PDF documents
        if hasattr(self, 'vectorstore'):  # Return cached vector store if it exists
            return self.vectorstore
        logging.info("Loading the documents")
        loader = PyPDFDirectoryLoader(self.config['db_path'])
        docs = loader.load()

        # Load the website information
        loader = WebBaseLoader(
            web_paths=("https://www.pflege.de/pflegekasse-pflegefinanzierung/pflegeleistungen/pflegegeld/",),
            bs_kwargs=dict(
                parse_only=bs4.SoupStrainer(
                    class_=("article-content", "post-title", "article-head",)
                )
            ),
        )
        web = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs + web)
        
        # Create video documents
        video_documents = [
            Document(
                page_content=f"{video['title']} {video['description']} {' '.join(video['tags'])}",
                metadata={
                    "title": video["title"],
                    "description": video["description"],
                    "tags": video["tags"],
                    "source": video["provider"],
                    "url": video["url"],
                    "category": video["category"],
                    "type": "video"
                }
            )
            for video in self.video_store
        ]
        
        all_documents = splits + video_documents
        
        logging.info("Setting up the vector store")
        self.vectorstore = InMemoryVectorStore.from_documents(
            documents=all_documents,
            embedding=AzureOpenAIEmbeddings(
                model=self.config['embedding_model'],
                api_version=self.config['api_version']
            )
        )
        return self.vectorstore

    def _create_retrieve_tool(self):
        """Create the retrieval tool."""
        logging.info("Creating the retriever tool")
        @tool(response_format="content_and_artifact")
        def retrieve(query: str):
            """Retrieve information related to a query."""
            retrieved_docs = self.vectorstore.similarity_search(query, k=self.config.get('k', 4))
            
            # Format the documents for the prompt
            serialized = "\n\n".join(
                (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
                for doc in retrieved_docs
            )
            
            return serialized, retrieved_docs
        
        return retrieve
    
    def _create_tools(self):
        """Create and return all tools used in the graph."""
        return [self._create_retrieve_tool()]
    
    def _extract_tool_messages(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """Extract recent tool messages from the state."""
        recent_tool_messages = []
        for message in reversed(messages):
            if message.type == "tool":
                recent_tool_messages.append(message)
            else:
                break
        return recent_tool_messages[::-1]
    
    def _construct_prompt(self, system_message: SystemMessage, chat_history: List[Dict], conversation_messages: List[BaseMessage]) -> List[BaseMessage]:
        """Construct the final prompt for the LLM."""
        logging.info("Constructing the prompt and iterating over the chat_history")
        logging.info(chat_history)
        logging.info("Conversation messages")
        logging.info(conversation_messages)
        chat_history_messages = [
            HumanMessage(content=msg["content"]) if msg["role"] == "user" else AIMessage(content=msg["content"])
            for msg in chat_history
        ]
        return [system_message] + chat_history_messages + conversation_messages

    def _create_graph(self):
        """Create the LangGraph workflow."""

        def query_or_respond(state: MessagesState):
            """Generate tool call for retrieval or respond."""
            # Include chat history in the messages
            messages_with_history = state["chat_history"] + state["messages"]

            llm_with_tools = llm.bind_tools(self._create_tools())
            response = llm_with_tools.invoke(messages_with_history)
            logging.info(f"Response of the query_and_respond: {response}")
            return {"messages": [response]}

        def generate(state: MessagesState):
            """Generate final answer using retrieved content."""
            # Get recent tool messages
            logging.info(f"Messages so far in generate function: {state['messages']}")
            tool_messages = self._extract_tool_messages(state["messages"])
            logging.info(tool_messages)

            # Format prompt with retrieved context
            docs_content = "\n\n".join(doc.content for doc in tool_messages)
            
            # Create system message with context
            system_message = SystemMessage(content=self.config['qa_system_prompt'].format(
                context=docs_content
            ))
            
            # Get conversation messages excluding tool messages
            conversation_messages = [
                message
                for message in state["messages"]
                if message.type in ("human", "system")
                or (message.type == "ai" and not message.tool_calls)
            ]

            # Include chat history in the final prompt
            prompt = self._construct_prompt(system_message, state["chat_history"], conversation_messages)
            logging.info(f"Prompt of the generate function: {prompt}")
            
            # Generate response
            response = llm.invoke(prompt)
            logging.info(f"Response of the generate: {response}")
            
            return {"messages": [response], "context": [artifact for message in state["messages"] for artifact in message.artifact]}

        # Create the graph
        graph_builder = StateGraph(MessagesState)
        
        # Create tool node
        tools = ToolNode(self._create_tools())
        
        # Add nodes
        graph_builder.add_node("query_or_respond", query_or_respond)
        graph_builder.add_node("tools", tools)
        graph_builder.add_node("generate", generate)
        
        # Set up the flow
        graph_builder.set_entry_point("query_or_respond")
        graph_builder.add_conditional_edges(
            "query_or_respond",
            tools_condition,
            {END: END, "tools": "tools"},
        )
        graph_builder.add_edge("tools", "generate")
        graph_builder.add_edge("generate", END)
        
        return graph_builder.compile()

    async def query(self, message: str, chat_history: List[Dict]) -> RAGResponse:
        """Process a query through the RAG system."""
        # Initialize state with message and chat history
        state = MessagesState(
            messages=[HumanMessage(content=message)],
            chat_history=chat_history,
            context=[]
        )
        
        # Run the graph
        try:
            final_state = await self.graph.ainvoke(state)
            logging.info(f"Final state in query function: {final_state}")
            # Get the final AI message
            for message in reversed(final_state["messages"]):
                if isinstance(message, AIMessage):
                    answer = message.content
                    break
            
            # Process video information
            video_sources = [
                {
                    "title": doc.metadata.get("title"),
                    "description": doc.metadata.get("description"),
                    "url": doc.metadata.get("url"),
                }
                for doc in final_state["context"]
                if doc.metadata.get("type") == "video"
            ]

            return RAGResponse(
                answer=answer,
                sources=list({doc.metadata['source'].replace("utils/db/", "").replace(".pdf", "") 
                            for doc in final_state["context"]}),
                thumbnails=[
                    f"https://img.youtube.com/vi/{urllib.parse.parse_qs(urllib.parse.urlparse(video['url']).query).get('v', [None])[0]}/0.jpg"
                    for video in video_sources if video['url']
                ],
                video_URLs=[video["url"] for video in video_sources]
            )

        except Exception as e:
            logging.error(f"Error invoking RAG: {e}", exc_info=True)

            return RAGResponse(
                answer=GENERATION_FAILED_RESPONSE,
                sources=[],
                thumbnails=[],
                video_URLs=[]
            )
