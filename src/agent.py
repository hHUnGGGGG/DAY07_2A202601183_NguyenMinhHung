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

    NO_CONTEXT = "(Không tìm thấy đoạn tài liệu liên quan trong cơ sở tri thức.)"

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        return str(self.llm_fn(self._build_prompt(question, results)))

    def _build_prompt(self, question: str, results: list[dict]) -> str:
        context = self._format_context(results)
        return (
            "Bạn là trợ lý trả lời câu hỏi về dịch vụ và quy định đại học.\n"
            "Chỉ dùng NGỮ CẢNH bên dưới để trả lời. Nếu ngữ cảnh không đủ thông tin, "
            "hãy nói rõ là không tìm thấy thay vì suy đoán.\n"
            "Trích dẫn số hiệu đoạn ([1], [2]...) cho thông tin bạn dùng.\n\n"
            f"NGỮ CẢNH:\n{context}\n\n"
            f"CÂU HỎI: {question}\n\n"
            "TRẢ LỜI:"
        )

    def _format_context(self, results: list[dict]) -> str:
        if not results:
            return self.NO_CONTEXT

        blocks = []
        for position, result in enumerate(results, start=1):
            metadata = result.get("metadata") or {}
            # Prefer the traceable K3 source fields, then fall back to the doc id.
            source = metadata.get("source_url") or metadata.get("source") or metadata.get("doc_id", "unknown")
            blocks.append(
                f"[{position}] nguồn: {source} | score={result.get('score', 0.0):.3f}\n{result.get('content', '')}"
            )
        return "\n\n".join(blocks)
