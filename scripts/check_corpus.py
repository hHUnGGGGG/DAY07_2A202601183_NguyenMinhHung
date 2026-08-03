"""
check_corpus.py — tự động hoá CHECKPOINT 2 (docs/DATA_COLLECTION.md mục 6).

    py scripts/check_corpus.py
    py scripts/check_corpus.py --data-dir data/k3_university

Kiểm:
  1. Số file trong khoảng 5-10
  2. Mỗi file đủ metadata bắt buộc; doc_id trùng tên file; doc_id không trùng nhau
  3. sources.csv khớp MỘT-MỘT với các file .md
  4. Field phân vai (audience) có ít nhất HAI giá trị khác nhau
  5. Không còn marker TODO
  6. In CORPUS HASH — cả 5 thành viên phải có cùng hash trước khi chạy benchmark

Exit code 0 = mọi dòng OK.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from pathlib import Path

REQUIRED_FIELDS = ["doc_id", "title", "source_url", "retrieved_at", "document_version"]
ROLE_KEY = "audience"  # K4 đổi thành "customer_role"
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_front_matter(text: str) -> dict:
    """Parser tối giản, cùng quy ước với ingest.parse_front_matter."""
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    closing = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if closing is None:
        return {}

    metadata: dict[str, str] = {}
    for raw in lines[1:closing]:
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.split(" #", 1)[0].strip().strip('"').strip("'")
        metadata[key.strip()] = value
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/k3_university")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"LỖI: không tìm thấy {data_dir}")
        return 1

    md_files = sorted(data_dir.glob("*.md"))
    if not md_files:
        print(f"LỖI: không có file .md nào trong {data_dir}")
        return 1

    problems: list[str] = []
    doc_ids: list[str] = []
    role_counts: dict[str, int] = {}

    print(f"=== Kiểm corpus: {data_dir} ===\n")
    for path in md_files:
        text = path.read_text(encoding="utf-8")
        metadata = parse_front_matter(text)
        issues: list[str] = []

        missing = [field for field in REQUIRED_FIELDS if field not in metadata]
        if missing:
            issues.append(f"thiếu {missing}")
        if ROLE_KEY not in metadata:
            issues.append(f"thiếu {ROLE_KEY}")
        if metadata.get("doc_id") != path.stem:
            issues.append(f"doc_id ({metadata.get('doc_id')}) != tên file ({path.stem})")
        if "TODO" in text:
            issues.append(f"còn {text.count('TODO')} marker TODO")
        retrieved_at = metadata.get("retrieved_at", "")
        if retrieved_at and not DATE_PATTERN.match(retrieved_at):
            issues.append(f"retrieved_at '{retrieved_at}' không đúng dạng YYYY-MM-DD")

        doc_ids.append(metadata.get("doc_id") or path.stem)
        role = metadata.get(ROLE_KEY, "(thiếu)")
        role_counts[role] = role_counts.get(role, 0) + 1

        status = "OK" if not issues else "LỖI: " + "; ".join(issues)
        print(f"{path.name:48} {status}")
        problems.extend(f"{path.name}: {issue}" for issue in issues)

    print()
    print(f"số file        : {len(md_files)} (cần 5-10)")
    if not 5 <= len(md_files) <= 10:
        problems.append(f"số file {len(md_files)} nằm ngoài khoảng 5-10")

    duplicates = {doc_id for doc_id in doc_ids if doc_ids.count(doc_id) > 1}
    if duplicates:
        problems.append(f"doc_id trùng: {sorted(duplicates)}")

    csv_path = data_dir / "sources.csv"
    if not csv_path.exists():
        print("sources.csv    : THIẾU FILE")
        problems.append("thiếu sources.csv")
    else:
        with csv_path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        csv_ids = sorted(row["doc_id"] for row in rows)
        matched = csv_ids == sorted(doc_ids)
        print(f"sources.csv    : {'khớp 1-1' if matched else 'LỆCH'} ({len(rows)} dòng)")
        if not matched:
            only_csv = sorted(set(csv_ids) - set(doc_ids))
            only_md = sorted(set(doc_ids) - set(csv_ids))
            problems.append(f"sources.csv lệch — chỉ có trong csv: {only_csv}; chỉ có trong .md: {only_md}")
        todo_rows = [row["doc_id"] for row in rows if "TODO" in ",".join(str(v) for v in row.values())]
        if todo_rows:
            problems.append(f"sources.csv còn TODO ở: {todo_rows}")

    print(f"{ROLE_KEY:15}: {role_counts}")
    distinct_roles = {role for role in role_counts if role != "(thiếu)"}
    if len(distinct_roles) < 2:
        problems.append(
            f"{ROLE_KEY} chỉ có {len(distinct_roles)} giá trị — filter sẽ không loại được document nào, "
            "và bạn không chứng minh được giá trị của metadata ở phần phân tích"
        )

    digest = hashlib.sha256()
    for path in md_files:
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    corpus_hash = digest.hexdigest()[:16]
    print(f"corpus hash    : {corpus_hash}  <- cả 5 thành viên phải giống nhau")

    print()
    if problems:
        print(f"--- CÒN {len(problems)} VẤN ĐỀ ---")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print("--- CHECKPOINT 2 ĐẠT: corpus sẵn sàng cho benchmark ---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
