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

    NO_CONTEXT = "(Khong tim thay doan tai lieu lien quan trong co so tri thuc.)"

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        return str(self.llm_fn(self._build_prompt(question, results)))

    def _build_prompt(self, question: str, results: list[dict]) -> str:
        context = self._format_context(results)
        return (
            "Ban la tro ly tra loi cau hoi ve dich vu va quy dinh dai hoc.\n"
            "Chi dung NGU CANH ben duoi de tra loi. Neu ngu canh khong du thong tin, "
            "hay noi ro la khong tim thay thay vi suy dien.\n"
            "Trich dan so hieu doan ([1], [2]...) cho thong tin ban dung.\n\n"
            f"NGU CANH:\n{context}\n\n"
            f"CAU HOI: {question}\n\n"
            "TRA LOI:"
        )

    def _format_context(self, results: list[dict]) -> str:
        if not results:
            return self.NO_CONTEXT

        blocks = []
        for position, result in enumerate(results, start=1):
            metadata = result.get("metadata") or {}
            # Prefer the traceable K3 source fields, then fall back to the doc id.
            source = (
                metadata.get("source_url")
                or metadata.get("source")
                or metadata.get("doc_id", "unknown")
            )
            blocks.append(
                f"[{position}] nguon: {source} | score={result.get('score', 0.0):.3f}\n"
                f"{result.get('content', '')}"
            )
        return "\n\n".join(blocks)
