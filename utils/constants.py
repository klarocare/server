CHAT_HISTORY_LIMIT = 30

# RAG config, could be explicitely given by a config file as well
RAG_CONFIG = {
    "db_path": "utils/db/",
    "embedding_model": "text-embedding-ada-002",
    "api_version": "2023-05-15",
    "retriever_args": {
        "search_type":"mmr", 
        "search_kwargs": {'k': 5, 'fetch_k': 100, "score_threshold": 0.8}},
    "prompt_path": "utils/prompts/"
}