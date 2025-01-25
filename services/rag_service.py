import json
import urllib.parse
import logging
import os
import threading

from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_core.documents import Document

from schemas.rag_schema import RAGResponse, Language
from services import llm
from utils.constants import RAG_CONFIG



class RAGService:
    _instance = None
    _lock = threading.Lock()  # To ensure thread safety

    def __new__(cls, *args, **kwargs):
        """Control the instantiation process."""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):  # Avoid reinitialization
            self.initialized = True
            self.video_store = []
            self.lang = Language.ENGLISH
            self.config = RAG_CONFIG
            self._setup_video_store()
            self._setup_retriever()
            self._setup_rag_chain(self.lang)

    @classmethod
    def get_instance(cls):
        """Return the singleton instance of RAGService."""
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
    
    def _setup_video_store(self):
        with open(os.path.join(self.config['db_path'], 'videos.json')) as file:
            self.video_store = json.load(file)

    def _setup_retriever(self):
        logging.info("Setting up the retriever")

        loader = PyPDFDirectoryLoader(self.config['db_path'])
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)

        # Add video metadata as documents
        video_documents = [
            Document(
                page_content=f"{video['title']} {video['description']} {' '.join(video['tags'])}",
                metadata={
                    "title": video["title"],
                    "description": video["description"],
                    "tags": video["tags"],
                    "source": video["provider"],
                    "url": video["url"],
                    "category": video["category"]
                }
            )
            for video in self.video_store
        ]

        all_documents = splits + video_documents

        logging.info("Setting up the vector store")
        vectorstore = InMemoryVectorStore.from_documents(
            documents=all_documents, 
            embedding=AzureOpenAIEmbeddings(
                model=self.config['embedding_model'],
                api_version=self.config['api_version']
            )
        )

        # Retriever takes a question as an input, and returns the related Documents to that question
        retriever = vectorstore.as_retriever(
            **self.config['retriever_args']
        )

        contextualize_q_system_prompt = (
            """
            Given the user's question and related context, rewrite the question in a way 
            that maximizes its clarity and semantic meaning. 
            Ensure no ambiguity remains.
            """
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        self.history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )
        logging.info("Retriever setup is complete")

    def _setup_rag_chain(self, lang):
        logging.info("Setting up the RAG chain")
        with open(os.path.join(self.config['prompt_path'], f'prompt_klaro_{lang.value}.txt'), 'r') as file:
            system_prompt = file.read()
                
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        self.rag_chain = create_retrieval_chain(self.history_aware_retriever, question_answer_chain)
        logging.info("RAG setup is complete")

    def _extract_context(self, response):
        video_sources = [
            {
                "title": item.metadata.get("title"),
                "description": item.metadata.get("description"),
                "url": item.metadata.get("url"),
            }
            for item in response["context"]
            if item.metadata.get("url")
        ]

        unified_context = {
            "videos": video_sources,
            "original_context": response["context"],
        }

        return unified_context

    def query(self, message, chat_history) -> RAGResponse:

        state = {
            "input": message,
            "chat_history": chat_history,
            "context": "",
        }

        response = self.rag_chain.invoke(state)  # Ensure async consistency

        unified_context = self._extract_context(response)

        final_prompt = (
            "Here is the retrieved context:\n"
            f"Videos: {unified_context['videos']}\n\n"
            "Based on this context, generate an accurate, brief (must fit a mobile screen chat format) and user-friendly response\n"
            "Keep the original language and the tone of voice:\n"
            f"{response['answer']}"
        )
        # TODO: Not sure about this invoke, but still we could use this for restricting the context as well - since we are making the call anyway
        final_response = llm.invoke(final_prompt)

        return RAGResponse(
            sources=list({item.metadata['source'].replace("utils/db/", "").replace(".pdf", "") for item in response["context"]}),
            thumbnails=[
                f"https://img.youtube.com/vi/{urllib.parse.parse_qs(urllib.parse.urlparse(video['url']).query).get('v', [None])[0]}/0.jpg"
                for video in unified_context["videos"] if video['url']
            ],
            video_URLs=[video["url"] for video in unified_context["videos"]],
            answer=final_response.content,
        )
