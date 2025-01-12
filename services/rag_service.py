import json
import urllib.parse
from typing import List

from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_core.documents import Document

from schemas.chat_schema import ChatResponse, Language
from services import llm


class RAGService():

    def __init__(self):
        self.video_store = []
        self.lang = Language.ENGLISH
        self._setup_video_store()
        self._setup_retriever()
        self._setup_rag_chain(self.lang)
    
    def setup(self, request):
        self.__init__(lang=request.language)

    def _setup_video_store(self):
        with open('utils/db/videos.json') as file:
            self.video_store = json.load(file)

    def _setup_retriever(self):
        """
        Loads the reference documents, combines video json objects, creates a vector store, and a retriever.
        """
        # Load, split, and index documents
        loader = PyPDFDirectoryLoader("utils/db/")
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

        vectorstore = InMemoryVectorStore.from_documents(
            documents=all_documents, 
            embedding=AzureOpenAIEmbeddings(
                model="text-embedding-ada-002", # TODO: Config file to define these
                api_version="2023-05-15")
            )
        retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={'k': 5, 'fetch_k': 100, "score_threshold": 0.75})

        # Contextualize question 
        contextualize_q_system_prompt = (
            """
            Given the user's question and related context, rewrite the question in a way that maximizes its clarity and semantic meaning. 
            Ensure no ambiguity remains.
            """
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        self.history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
            )
        
    def _setup_rag_chain(self, lang):
        with open(f'utils/prompts/prompt_klaro_{lang.value}.txt', 'r') as file:
            system_prompt = file.read()
        
        system_prompt = system_prompt.replace("{location}", self.location)
        
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        self.rag_chain = create_retrieval_chain(self.history_aware_retriever, question_answer_chain)
    
    def _extract_cleaned_sources(self, context) -> List[str]:
        sources = []
        for item in context:
            if 'source' in item.metadata:
                # Get the source name and remove "utils/db/" and ".pdf"
                source = item.metadata['source'].replace("utils/db/", "").replace(".pdf", "")
                sources.append(source)
        return list(set(sources))

    def _fill_thumbnails(self, video_sources) -> List[str]:
        """
        Converts video URLs into thumbnail URL provided by YouTube.
        """
        thumbnails = []
        for video in video_sources:
            parsed_url = urllib.parse.urlparse(video['url'])
            query_params = urllib.parse.parse_qs(parsed_url.query)
            # Extract the video ID
            video_id = query_params.get("v", [None])[0]
            if  video_id:
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
                thumbnails.append(thumbnail_url)
        
        return thumbnails
        
    async def _extract_context(self, response):
        """
        Extract video and location data from the RAG chain response.
        Combine this data into a unified context for generating better responses.
        """

        # Extract video metadata
        video_sources = [
            {
                "title": item.metadata.get("title"),
                "description": item.metadata.get("description"),
                "url": item.metadata.get("url"),
            }
            for item in response["context"]
            if item.metadata.get("url")  # Check if the source is a video
        ]

        # Combine extracted context
        unified_context = {
            "videos": video_sources,
            "original_context": response["context"],
        }

        return unified_context


    async def query(self, message, chat_history) -> ChatResponse:
        """
        The flow of this method:
        1 - Generate an answer for the user's question using the RAG chain.
        2 - Extract locations and videos.
        3 - Use unified context for final output generation.
        """
        
        # Step 1: Generate initial answer with RAG chain
        state = {
            "input": message,
            "chat_history": chat_history,
            "context": "",
        }
        response = self.rag_chain.invoke(state)

        # Step 2: Extract unified context
        unified_context = await self._extract_context(response)

        # Step 3: Pass unified context into a secondary prompt for final refinement
        final_prompt = (
            "Here is the retrieved context:\n"
            f"Videos: {unified_context['videos']}\n\n"
            "Based on this context, generate an accurate, brief (must fit a mobile screen chat format) and user-friendly response\n"
            "Keep the original language and the tone of voice:\n"
            f"{response['answer']}"
        )

        final_response = llm.invoke(final_prompt)

        return ChatResponse(
            sources=self._extract_cleaned_sources(unified_context["original_context"]),
            thumbnails=self._fill_thumbnails(unified_context["videos"]),
            video_URLs=[video["url"] for video in unified_context["videos"]],
            answer=final_response.content,
        )

            