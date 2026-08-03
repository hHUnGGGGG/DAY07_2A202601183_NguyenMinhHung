from __future__ import annotations

from typing import Any, Callable

from .chunking import compute_similarity
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            self._chroma_available = True
        except Exception:
            self._chroma_available = False
            # The lab allows either backend ("in-memory hoac ChromaDB"). This store keeps
            # the in-memory list as the single source of truth.
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        metadata = dict(doc.metadata or {})
        metadata.setdefault("doc_id", doc.id)

        record = {
            "id": doc.id,
            "content": doc.content,
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content),
            "index": self._next_index,
        }
        self._next_index += 1
        return record

    def _search_records(
        self, query: str, records: list[dict[str, Any]], top_k: int
    ) -> list[dict[str, Any]]:
        if not records or top_k <= 0:
            return []

        query_embedding = self._embedding_fn(query)
        results = [
            {
                "id": record["id"],
                "content": record["content"],
                "metadata": record["metadata"],
                "score": compute_similarity(query_embedding, record["embedding"]),
            }
            for record in records
        ]
        # Stable sort: equal scores keep insertion order.
        results.sort(key=lambda result: result["score"], reverse=True)
        return results[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        for doc in docs or []:
            self._store.append(self._make_record(doc))

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        return len(self._store)

    def search_with_filter(
        self,
        query: str,
        top_k: int = 3,
        metadata_filter: dict | None = None,
    ) -> list[dict[str, Any]]:
        if not metadata_filter:
            candidates = self._store
        else:
            candidates = [
                record
                for record in self._store
                if all(
                    record["metadata"].get(key) == value
                    for key, value in metadata_filter.items()
                )
            ]
        return self._search_records(query, candidates, top_k)

    def delete_document(self, doc_id: str) -> bool:
        size_before = len(self._store)
        self._store = [
            record
            for record in self._store
            if record["metadata"].get("doc_id") != doc_id
        ]
        return len(self._store) < size_before
