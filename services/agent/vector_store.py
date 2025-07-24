from langchain_core.vectorstores import InMemoryVectorStore

# Bunu en azından yazdıralım bir yere, her seferinde olurşturmak amelelik

class VectorStoreManager:
    def __init__(self, docs, embeddings, k: int = 4):
        self.store = InMemoryVectorStore.from_documents(docs, embedding=embeddings)
        self.k = k

    def search(self, question: str, k: int | None = None):
        hits = self.store.similarity_search_with_score(question, k or self.k)
        return [doc for doc, _ in hits]
