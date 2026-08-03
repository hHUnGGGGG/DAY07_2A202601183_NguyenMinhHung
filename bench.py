"""
bench.py — chạy 5 benchmark query của nhóm trên CHIẾN LƯỢC CHUNKING RIÊNG của bạn.

    py bench.py --strategy fixed              # Nguyễn Minh Hùng
    py bench.py --strategy sentence           # Hoàng Anh Quân
    py bench.py --strategy recursive          # Phạm Hải Đăng
    py bench.py --strategy heading            # Bùi Gia Huy
    py bench.py --strategy heading_recursive  # Nguyễn Huy Đức

CHỈ MỘT DÒNG khác nhau giữa các thành viên: lựa chọn trong STRATEGIES bên dưới.
Corpus, 5 query, embedding backend và top_k phải GIỮ NGUYÊN, nếu không bảng so sánh
của nhóm không còn là so sánh công bằng.

Trước khi chạy, cả nhóm đặt cùng backend:
    $env:EMBEDDING_PROVIDER="local"     # PowerShell
    export EMBEDDING_PROVIDER=local     # bash

Phần nạp dữ liệu KHÔNG viết lại: dùng ingest.build_knowledge_base() đã cung cấp sẵn
(parse front matter -> chunk -> gắn doc_id + metadata lên từng chunk -> nạp store).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bench_queries import FILTER_KEY, QUERIES, validate
from ingest import build_knowledge_base
from main import _select_embedder, demo_llm
from src.agent import KnowledgeBaseAgent
from src.chunking import FixedSizeChunker, RecursiveChunker, SentenceChunker

DATA_DIR = "data/k3_university"
TOP_K = 3

# --------------------------------------------------------------------------------------
# DÒNG DUY NHẤT KHÁC NHAU GIỮA CÁC THÀNH VIÊN
# --------------------------------------------------------------------------------------
STRATEGIES: dict[str, dict] = {
    "fixed": {
        "owner": "Nguyễn Minh Hùng",
        "label": "FixedSizeChunker(chunk_size=500, overlap=50)",
        "factory": lambda: FixedSizeChunker(chunk_size=500, overlap=50),
    },
    "sentence": {
        "owner": "Hoàng Anh Quân",
        "label": "SentenceChunker(max_sentences_per_chunk=3)",
        "factory": lambda: SentenceChunker(max_sentences_per_chunk=3),
    },
    "recursive": {
        "owner": "Phạm Hải Đăng",
        "label": "RecursiveChunker(chunk_size=400)",
        "factory": lambda: RecursiveChunker(chunk_size=400),
    },
    "heading": {
        "owner": "Bùi Gia Huy",
        "label": "HeadingChunker(max_chunk_size=800)",
        "factory": lambda: _load_heading_chunker("HeadingChunker")(max_chunk_size=800),
    },
    "heading_recursive": {
        "owner": "Nguyễn Huy Đức",
        "label": "HeadingRecursiveChunker(max_chunk_size=800, breadcrumb=True)",
        "factory": lambda: _load_heading_chunker("HeadingRecursiveChunker")(max_chunk_size=800),
    },
}


def _load_heading_chunker(class_name: str):
    """Import muộn để 3 strategy chuẩn vẫn chạy được khi src/heading_chunker.py chưa xong."""
    from src import heading_chunker

    return getattr(heading_chunker, class_name)


# --------------------------------------------------------------------------------------
# Chấm ở MỨC CHUNK (xem docs mục 7: đừng chỉ kiểm doc_id)
# --------------------------------------------------------------------------------------
def _rank_of_full_evidence(results: list[dict], needles: list[str]) -> int | None:
    """Thứ hạng (1-based) của chunk đầu tiên chứa ĐỦ mọi chuỗi trong needles."""
    for rank, result in enumerate(results, start=1):
        content = result["content"].lower()
        if all(needle.lower() in content for needle in needles):
            return rank
    return None


def _evidence_complete_across_topk(results: list[dict], needles: list[str]) -> bool:
    """Bằng chứng có mặt đầy đủ trong top-k GỘP LẠI (dù bị chia rời nhiều chunk)."""
    joined = " ".join(result["content"] for result in results).lower()
    return all(needle.lower() in joined for needle in needles)


def score_query(results: list[dict], query: dict) -> dict:
    """Điểm retrieval tự động — là CẬN TRÊN của điểm rubric, chưa xét agent answer."""
    needles = query["must_contain"]
    rank = _rank_of_full_evidence(results, needles)
    complete = _evidence_complete_across_topk(results, needles)
    gold_doc_in_topk = any(
        result["metadata"].get("doc_id") in query["expected_doc_ids"] for result in results
    )

    if rank == 1:
        score, reason = 2, "chunk chứa đủ bằng chứng ở top-1"
    elif rank is not None:
        score, reason = 1, f"chunk chứa đủ bằng chứng ở top-{rank}, không phải top-1"
    elif complete:
        score, reason = 1, "bằng chứng BỊ CHIA RỜI nhiều chunk (dấu hiệu chunk coherence kém)"
    else:
        score, reason = 0, "không tìm thấy bằng chứng trong top-3"

    return {
        "score": score,
        "reason": reason,
        "evidence_rank": rank,
        "evidence_complete": complete,
        "gold_doc_in_topk": gold_doc_in_topk,
        # Chênh lệch giữa hai cột này thường là phát hiện đáng giá nhất của buổi lab:
        "doc_level_vs_chunk_level_gap": gold_doc_in_topk and score == 0,
    }


# --------------------------------------------------------------------------------------
# In kết quả
# --------------------------------------------------------------------------------------
def _preview(text: str, width: int = 110) -> str:
    flat = " ".join(text.split())
    return flat[:width] + ("..." if len(flat) > width else "")


def format_results(results: list[dict]) -> list[str]:
    if not results:
        return ["   (không có kết quả nào)"]
    lines = []
    for rank, result in enumerate(results, start=1):
        meta = result["metadata"]
        lines.append(
            f"   {rank}. score={result['score']:.4f}  doc_id={meta.get('doc_id')}  "
            f"chunk={meta.get('chunk_index')}  {FILTER_KEY}={meta.get(FILTER_KEY)}"
        )
        lines.append(f"      {_preview(result['content'])}")
    return lines


def run_query(store, agent, query: dict, top_k: int) -> tuple[list[str], dict]:
    """Chạy một query; nếu ab_test thì chạy cả hai lần (không filter / có filter)."""
    lines: list[str] = []
    lines.append("")
    lines.append("-" * 100)
    lines.append(f"{query['id']} [{query['kind']}] {query['query']}")
    lines.append(f"   gold   : {query['gold_answer']}")
    lines.append(f"   nguồn  : {query['gold_source']}")
    lines.append(f"   bằng chứng cần có (must_contain): {query['must_contain']}")

    if query["ab_test"]:
        lines.append("")
        lines.append(f"   [A] KHÔNG filter — search(top_k={top_k})")
        results_a = store.search(query["query"], top_k=top_k)
        lines.extend(format_results(results_a))
        verdict_a = score_query(results_a, query)

        lines.append("")
        lines.append(f"   [B] CÓ filter {query['metadata_filter']} — search_with_filter(top_k={top_k})")
        results_b = store.search_with_filter(
            query["query"], top_k=top_k, metadata_filter=query["metadata_filter"]
        )
        lines.extend(format_results(results_b))
        verdict_b = score_query(results_b, query)

        docs_a = [r["metadata"].get("doc_id") for r in results_a]
        docs_b = [r["metadata"].get("doc_id") for r in results_b]
        lines.append("")
        lines.append(f"   A/B: điểm không filter={verdict_a['score']}  |  có filter={verdict_b['score']}")
        lines.append(f"        doc top-3 A: {docs_a}")
        lines.append(f"        doc top-3 B: {docs_b}")
        if docs_a == docs_b:
            lines.append(
                "        ⚠ Hai kết quả GIỐNG HỆT NHAU. Ghi nhận đúng như vậy trong report và phân tích "
                "vì sao query/corpus chưa thực sự đòi hỏi filter — đừng bịa ra khác biệt."
            )
        else:
            removed = sorted(set(docs_a) - set(docs_b))
            lines.append(f"        filter đã loại: {removed or '(không loại doc nào khỏi top-3)'}")

        results, verdict = results_b, verdict_b
    else:
        lines.append("")
        lines.append(f"   search(top_k={top_k})")
        results = store.search(query["query"], top_k=top_k)
        lines.extend(format_results(results))
        verdict = score_query(results, query)

    lines.append("")
    lines.append(f"   ĐIỂM RETRIEVAL (tự động): {verdict['score']}/2 — {verdict['reason']}")
    lines.append(
        f"   doc gold có trong top-3? {'CÓ' if verdict['gold_doc_in_topk'] else 'KHÔNG'}"
        + ("   ← doc đúng nhưng CHUNK SAI: đây là failure case đáng viết vào report"
           if verdict["doc_level_vs_chunk_level_gap"] else "")
    )
    lines.append("")
    lines.append("   Câu trả lời của agent:")
    lines.append(f"      {_preview(agent.answer(query['query'], top_k=top_k), 400)}")
    lines.append("   → Điểm rubric cuối cùng cần NGƯỜI đọc kiểm câu trả lời này (2 điểm = top-3 có chunk"
                 " liên quan VÀ agent trả lời đúng).")

    verdict["id"] = query["id"]
    return lines, verdict


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark 5 query trên chiến lược chunking riêng.")
    parser.add_argument("--strategy", required=True, choices=sorted(STRATEGIES))
    parser.add_argument("--data-dir", default=DATA_DIR)
    parser.add_argument("--top-k", type=int, default=TOP_K)
    parser.add_argument("--out", default=None, help="ghi kết quả ra file .md (mặc định report/bench_<strategy>.md)")
    args = parser.parse_args()

    problems = validate()
    if problems:
        print(f"⚠ bench_queries.py còn {len(problems)} vấn đề chưa xử lý:")
        for problem in problems:
            print(f"   - {problem}")
        print("  (vẫn chạy tiếp, nhưng điểm tự động chưa dùng để báo cáo được)\n")

    if not Path(args.data_dir).exists():
        print(f"Không tìm thấy thư mục dữ liệu: {args.data_dir}")
        return 1

    strategy = STRATEGIES[args.strategy]
    chunker = strategy["factory"]()
    embedder = _select_embedder()
    backend = getattr(embedder, "_backend_name", embedder.__class__.__name__)

    lines: list[str] = []
    lines.append("=" * 100)
    lines.append(f"BENCHMARK — strategy: {args.strategy}")
    lines.append(f"  Người chạy       : {strategy['owner']}")
    lines.append(f"  Chunker + tham số: {strategy['label']}")
    lines.append(f"  Corpus           : {args.data_dir}")
    lines.append(f"  Embedding backend: {backend}")
    lines.append(f"  top_k            : {args.top_k}")
    if backend == "mock embeddings fallback":
        lines.append("  ⚠ Mock embedding KHÔNG biểu diễn ngữ nghĩa. Benchmark bằng mock chỉ kiểm luồng kỹ")
        lines.append("    thuật; hãy ghi rõ hạn chế này trong report và tập trung vào số chunk, coherence,")
        lines.append("    provenance — các chỉ số không phụ thuộc embedding.")
    lines.append("=" * 100)

    store = build_knowledge_base(args.data_dir, embedding_fn=embedder, chunker=chunker)
    lines.append(f"Đã nạp {store.get_collection_size()} chunk vào EmbeddingStore.")

    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)

    verdicts = []
    for query in QUERIES:
        query_lines, verdict = run_query(store, agent, query, args.top_k)
        lines.extend(query_lines)
        verdicts.append(verdict)

    total = sum(verdict["score"] for verdict in verdicts)
    lines.append("")
    lines.append("=" * 100)
    lines.append(f"TỔNG HỢP — {args.strategy} ({strategy['label']})")
    lines.append(f"  Số chunk đã nạp: {store.get_collection_size()}")
    lines.append("")
    lines.append("  | Query | Điểm | Hạng bằng chứng | Doc gold trong top-3 | Ghi chú |")
    lines.append("  |-------|------|-----------------|----------------------|---------|")
    for verdict in verdicts:
        rank = verdict["evidence_rank"] or "-"
        lines.append(
            f"  | {verdict['id']} | {verdict['score']}/2 | {rank} | "
            f"{'có' if verdict['gold_doc_in_topk'] else 'không'} | {verdict['reason']} |"
        )
    lines.append("")
    lines.append(f"  ĐIỂM RETRIEVAL TỰ ĐỘNG: {total}/10")
    lines.append("  (cận trên — điểm rubric thật còn phải kiểm câu trả lời của agent bằng mắt)")
    lines.append("=" * 100)

    output = "\n".join(lines)
    print(output)

    out_path = Path(args.out or f"report/bench_{args.strategy}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(f"```text\n{output}\n```\n", encoding="utf-8")
    print(f"\nĐã ghi kết quả vào {out_path} — dán vào REPORT_CANHAN.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
