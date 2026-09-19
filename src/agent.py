from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        if self.store.get_collection_size() == 0:
            return "Knowledge base is empty."
            
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "No relevant context found."
            
        context_parts = []
        for i, res in enumerate(results, 1):
            source = res.get("metadata", {}).get("doc_id", "Unknown")
            content = res.get("content", "")
            context_parts.append(f"[{i}] Source: {source}\n{content}")
            
        context_str = "\n\n".join(context_parts)
        
        prompt = f"""You are a helpful assistant. Answer the user's question based ONLY on the provided context below.
If the answer cannot be found in the context, exactly say "I cannot answer this based on the provided context."
When answering, you must cite the source chunks using their numbers, e.g., [1] or [2].

Context:
{context_str}

Question: {question}
Answer:"""

        return self.llm_fn(prompt)
