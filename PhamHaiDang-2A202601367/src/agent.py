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
        # 1. Retrieve
        results = self.store.search(question, top_k=top_k)

        # 2. Build a grounded prompt from the retrieved chunks
        if results:
            context = "\n\n".join(
                f"[{i + 1}] {r['content']}" for i, r in enumerate(results)
            )
        else:
            context = "(khong tim thay ngu canh lien quan)"

        prompt = (
            "Ban la tro ly tra loi cau hoi dua tren ngu canh duoc cung cap.\n"
            "Chi su dung thong tin trong ngu canh; neu ngu canh khong du, hay noi ro la khong biet.\n\n"
            f"Ngu canh:\n{context}\n\n"
            f"Cau hoi: {question}\n"
            "Tra loi:"
        )

        # 3. Generate
        return self.llm_fn(prompt)