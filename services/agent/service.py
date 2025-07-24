import logging, os
from pathlib import Path
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader, TextLoader
from langchain_openai import AzureOpenAIEmbeddings
from schemas.rag_schema import Language, ChatResponse
from utils.constants import RAG_CONFIG
from core.config import settings

from services.agent.vector_store import VectorStoreManager
from services.agent.graph import build_graph

class AgenticRAGService:
    """Drop-in replacement for legacy RAGService.query(...)"""

    def __init__(self):
        cfg = RAG_CONFIG
        self.language = Language.GERMAN    # default
        self._prepare_docs(cfg)
        self.embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            model=cfg["embedding_model"],
            api_version=cfg["api_version"]
        )
        self.vs = VectorStoreManager(self.splits, self.embeddings,
                                     k=cfg["retriever_args"]["search_kwargs"]["k"])
        self.graph = build_graph(self.vs)

    def _prepare_docs(self, cfg):
        pdf_loader = PyPDFDirectoryLoader(Path(cfg['db_path']) / cfg['pdf_path'])
        pdf_docs = pdf_loader.load()
        txt_docs = []
        for fn in os.listdir(Path(cfg['db_path']) / cfg['text_path']):
            fp = Path(cfg['db_path']) / cfg['text_path'] / fn
            if fp.suffix == ".txt":
                txt_docs.extend(TextLoader(fp).load())
        docs = pdf_docs + txt_docs
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.splits = splitter.split_documents(docs)

    def update_language(self, language: Language):
        if language != self.language:
            self.language = language
            self.graph = build_graph(self.vs)

    def query(self, message: str, chat_history: list[dict], language: Language):
        # 1) refresh language ↔ prompt mapping
        self.update_language(language)

        logging.info("🔄  Agentic RAGService invoked")

        # 2) run the graph and ask it to return ONLY the keys we care about
        state = self.graph.invoke(
            {"chat_history": chat_history, "user_msg": message},
            output_keys=["result", "route"]
        )

        payload = state["result"]                   # summary OR RAG answer JSON

        # 3) map to ChatResponse (keeps your public API unchanged)
        if state["route"] == "CALLBACK":
            return ChatResponse(has_callback=True,  response=payload)

        return ChatResponse(has_callback=False, response=payload)
