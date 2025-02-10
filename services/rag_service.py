import logging
import os
import threading
from typing import List, Dict, Any

from langchain import hub
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader, TextLoader
from langchain_core.documents import Document

from utils.constants import RAG_CONFIG
from schemas.rag_schema import Language, RAGResponse
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
            self.video_store = []
            self.lang = Language.GERMAN
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

        # Setup embeddings and vector store
        self.embeddings = AzureOpenAIEmbeddings(
            model=self.config['embedding_model'],
            api_version=self.config['api_version']
        )
        
        self.vectorstore = InMemoryVectorStore.from_documents(
            documents=self.splits,
            embedding=self.embeddings
        )
        logging.info("Vector store initialized")

        # Load prompt template
        with open(os.path.join(self.config['prompt_path'], f'prompt_klaro_{self.lang.value}.txt'), 'r') as file:
            self.system_prompt = file.read()
        
        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        # Load question rephrase prompt
        self.rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")
        logging.info("All components initialized")
    
    def update_language(self, lang: Language):
        self.lang = lang

        # Load prompt template
        with open(os.path.join(self.config['prompt_path'], f'prompt_klaro_{self.lang.value}.txt'), 'r') as file:
            self.system_prompt = file.read()
        
        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

    def rephrase_question(self, input: str, chat_history: List) -> str:
        """Rephrase the question using chat history context"""
        messages = self.rephrase_prompt.format(
            input=input,
            chat_history=chat_history
        )
        rephrased = llm.invoke(messages).content
        logging.info(f"Rephrased question: {rephrased}")
        return rephrased

    def retrieve_documents(self, question: str, **kwargs) -> List[Document]:
        """Retrieve relevant documents for the question"""
        k = kwargs.get('k', self.config['retriever_args'].get('search_kwargs', {}).get('k', 4))
        docs = self.vectorstore.similarity_search_with_score(question, k=k)
        logging.info(f"Retrieved {len(docs)} documents")
        for i, (doc, score) in enumerate(docs):
            logging.info(f"Doc {i} score: {score:.3f}")
            logging.info(f"Doc {i} source: {doc.metadata.get('source')}")
            logging.info(f"Doc {i} preview: {doc.page_content[:200]}...")

        return [doc[0] for doc in docs]

    def generate_answer(self, question: str, docs: List[Document], chat_history: List) -> str:
        """Generate answer using retrieved documents"""
        # Format prompt with documents and chat history
        context = "\n\n".join([doc.page_content for doc in docs])
        
        messages = self.qa_prompt.format(
            context=context,
            chat_history=chat_history,
            input=question
        )
        
        # Generate response
        response = llm.invoke(messages).content
        logging.info(f"Generated response: {response}")
        return response

    def query(self, message: str, chat_history: List[Dict]) -> RAGResponse:
        """Process a query through the complete RAG pipeline"""
        logging.info(f"Processing query: {message}")
        
        # Step 1: Rephrase question using chat history
        rephrased_question = self.rephrase_question(message, chat_history)
        
        # Step 2: Retrieve relevant documents
        retrieved_docs = self.retrieve_documents(rephrased_question)
        
        # Step 3: Generate answer
        answer = self.generate_answer(message, retrieved_docs, chat_history)
        
        # Extract sources from retrieved documents
        sources = list({
            doc.metadata['source'].replace("utils/db/", "").replace(".pdf", "")
            for doc in retrieved_docs
        })
        
        return RAGResponse(
            sources=sources,
            thumbnails=[],
            video_URLs=[],
            answer=answer
        )

    def debug_pipeline(self, message: str, chat_history: List[Dict]) -> Dict[str, Any]:
        """Run the pipeline with full debug output"""
        debug_info = {}
        
        # Step 1: Question rephrasing
        debug_info['original_question'] = message
        debug_info['rephrased_question'] = self.rephrase_question(message, chat_history)
        
        # Step 2: Document retrieval
        retrieved_docs = self.retrieve_documents(debug_info['rephrased_question'])
        debug_info['retrieved_docs'] = [
            {
                'content': doc.page_content,
                'metadata': doc.metadata,
                'preview': doc.page_content[:200]
            }
            for doc in retrieved_docs
        ]
        
        # Step 3: Answer generation
        debug_info['final_answer'] = self.generate_answer(
            message,
            retrieved_docs,
            chat_history
        )
        
        return debug_info