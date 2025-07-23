import logging
import os
import threading
from typing import List, Dict, Tuple, Union

from langchain import hub
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader, TextLoader
from langchain_core.documents import Document

from utils.constants import RAG_CONFIG
from schemas.rag_schema import Language, RAGOutput, ChatResponse
from core.config import settings
from services import llm

class RAGService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.initialized = True
            self.language = Language.GERMAN
            self.config = RAG_CONFIG
            self._setup_components()

    def _setup_components(self):
        """Initialize all components separately"""
        logging.info("Setting up RAG components")
        
        # Load the pdf files
        pdf_loader = PyPDFDirectoryLoader(self.config['db_path'] + self.config['pdf_path'])
        pdf_docs = pdf_loader.load()

        # Load text files
        all_text_docs = []

        # Iterate through each file in the folder
        for filename in os.listdir(self.config['db_path'] + self.config['text_path']):
            file_path = os.path.join(self.config['db_path'] + self.config['text_path'], filename)
            
            # Ensure it's a text file before loading
            if os.path.isfile(file_path) and filename.endswith(".txt"):
                text_loader = TextLoader(file_path)
                text_docs = text_loader.load()
                all_text_docs.extend(text_docs) 
        
        docs = pdf_docs + all_text_docs
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )
        self.splits = self.text_splitter.split_documents(docs)
        logging.info(f"Created {len(self.splits)} splits")

        # Setup embeddings and vector store with fresh settings
        self.embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            model=self.config['embedding_model'],
            api_version=self.config['api_version']
        )
        
        self.vectorstore = InMemoryVectorStore.from_documents(
            documents=self.splits,
            embedding=self.embeddings
        )
        logging.info("Vector store initialized")

        # Setup the QA prompt
        self._setup_prompt()
        
        # Load question rephrase prompt
        self.rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")
        logging.info("All components initialized")
    
    def _setup_prompt(self):
        # Load prompt template
        with open(os.path.join(self.config['prompt_path'], f'prompt_klaro.txt'), 'r') as file:
            self.system_prompt = file.read()
        
        with open(os.path.join(self.config['prompt_path'], f'prompt_summary.txt'), 'r') as file:
            self.summary_prompt = file.read()

        self.system_prompt = self.system_prompt.replace("{preferred_language}", self.language.get_prompt_language())
        
        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
    
    def _rephrase_question(self, input: str, chat_history: List) -> str:
        """Rephrase the question using chat history context"""
        messages = self.rephrase_prompt.format(
            input=input,
            chat_history=chat_history
        )
        rephrased = llm.invoke(messages).content
        logging.info(f"Rephrased question: {rephrased}")
        return rephrased

    def _retrieve_documents(self, question: str, **kwargs) -> List[Document]:
        """Retrieve relevant documents for the question"""
        k = kwargs.get('k', self.config['retriever_args'].get('search_kwargs', {}).get('k', 4))
        docs = self.vectorstore.similarity_search_with_score(question, k=k)
        return [doc[0] for doc in docs]
    
    def _summarise_history(self, history: list[dict]) -> str:
        # keep only user & assistant turns
        lines = [
            f"{m['role'].capitalize()}: {m['content'].strip()}"
            for m in history
            if m["role"] in ("user", "assistant")
        ]
        chat_transcript = "\n".join(lines)
        logging.info(f"Chat transcript: {chat_transcript}")
        prompt = self.summary_prompt.format(chat_history=chat_transcript)
        logging.info(f"Summary prompt: {prompt}")
        summary = llm.invoke(prompt).content
        logging.info(f"Summary: {summary}")
        return summary  

    def _generate_answer(self, question: str, docs: List[Document], chat_history: List) -> RAGOutput:
        """Generate answer using retrieved documents"""
        # Format prompt with documents and chat history
        context = "\n\n".join([doc.page_content for doc in docs])
        
        messages = self.qa_prompt.format(
            context=context,
            chat_history=chat_history,
            input=question
        )
        
        # Generate response
        response: RAGOutput = llm.with_structured_output(RAGOutput).invoke(messages)
        return response
    
    def _check_for_callback(self, message: str, chat_history: List[Dict]) -> bool:
        """Check if the user wants a callback"""
        logging.info(f"Checking for callback")
        logging.info(f"Chat history: {chat_history}")
        logging.info(f"Message: {message}")
        ai_msg = llm.invoke(chat_history + [{"role": "user", "content": message}])
        logging.info(f"AI message: {ai_msg}")
        if ai_msg.tool_calls:
            logging.info(f"Tool calls: {ai_msg.tool_calls}")
            summary = self._summarise_history(chat_history)
            logging.info(f"Summary: {summary}")

            return True, summary
        return False, None

    def update_language(self, language: Language):
        self.language = language
        self._setup_prompt()

    def query(self, message: str, chat_history: List[Dict], language: Language) -> ChatResponse:
        """Process a query through the complete RAG pipeline"""
        logging.info(f"Processing query: {message}")

        has_callback, callback_summary = self._check_for_callback(message, chat_history)
        if has_callback:
            return ChatResponse(has_callback=True, response=callback_summary)
        
        # Step 0: Setup the prompt for the language
        self.update_language(language)

        # Step 1: Rephrase question using chat history
        rephrased_question = self._rephrase_question(message, chat_history)
        
        # Step 2: Retrieve relevant documents
        retrieved_docs = self._retrieve_documents(rephrased_question)
        
        # Step 3: Generate answer
        answer: RAGOutput = self._generate_answer(message, retrieved_docs, chat_history)
        
        # Extract sources from retrieved documents
        sources = list({
            doc.metadata['source'].replace("utils/db/", "").replace(".pdf", "")
            for doc in retrieved_docs
        })
        
        response = ChatResponse(has_callback=False, response=answer)
        logging.info(f"Response: {response}")
        return response

