"""
bench_queries.py — 5 benchmark query DÙNG CHUNG cho cả nhóm (Lab 07, biến thể K3).

QUY TẮC:
  * File này phải GIỐNG HỆT NHAU trong cả 5 repo cá nhân. Chủ trì: Hoàng Anh Quân
    (Benchmark owner). Ai muốn sửa phải báo, sửa ở repo nguồn, rồi cả 5 người sync lại.
  * KHÔNG đổi query sau khi đã có người chạy benchmark — kể cả khi kết quả xấu.
  * Gold answer phải TRÍCH ĐƯỢC từ corpus trong data/k3_university/, không suy đoán
    quy định của trường.

CHẤM Ở MỨC CHUNK, KHÔNG PHẢI MỨC DOC:
  Mỗi query khai báo `must_contain` — các chuỗi đặc trưng bắt buộc phải xuất hiện
  trong chunk truy xuất được. Lý do: một strategy có thể chiếm trọn cả 3 slot bằng
  đúng tài liệu gold mà KHÔNG chunk nào chứa câu trả lời (rất hay gặp với chunker
  theo heading, vì các section cùng tài liệu có score sát nhau).

  Ưu tiên chọn `must_contain` là SỐ hoặc THUẬT NGỮ TIẾNG ANH giữ nguyên trong bản
  dịch (ví dụ "15th business day", "35%") — chúng bất biến qua cách hành văn của
  người dịch, nên việc chấm không phụ thuộc bản dịch.

Chạy `py bench_queries.py` để kiểm tra file đã điền đủ chưa.
"""
from __future__ import annotations

# Field metadata bắt buộc của lớp K3 (K4 đổi thành "customer_role").
FILTER_KEY = "audience"

QUERIES: list[dict] = [
    {
        "id": "Q1",
        "kind": "số liệu",
        "query": "Hạn chót drop môn của học kỳ chính là ngày làm việc thứ mấy?",
        # TODO (Quân): trích nguyên văn câu trả lời từ tài liệu, ghi kèm section.
        "gold_answer": "TODO",
        "gold_source": "vinuni-academic-regulations-undergrad § Đăng ký học phần và thời hạn add/drop",
        "must_contain": ["15th business day"],
        "expected_doc_ids": ["vinuni-academic-regulations-undergrad"],
        "metadata_filter": None,
        "ab_test": False,
        "verified": False,  # đặt True sau khi đối chiếu văn bản gốc
        "notes": "Kiểm khả năng lấy đúng con số. Chú ý tài liệu còn nêu mốc 10th business day cho Summer — chunk trả về phải là mốc của học kỳ chính.",
    },
    {
        "id": "Q2",
        "kind": "điều kiện",
        "query": "Sinh viên phải đạt những điều kiện nào để tiếp tục được giữ học bổng đầu vào?",
        "gold_answer": "TODO",
        "gold_source": "vinuni-scholarship-maintenance § Điều kiện duy trì học bổng đầu vào",
        "must_contain": ["Level 3"],
        "expected_doc_ids": ["vinuni-scholarship-maintenance"],
        "metadata_filter": None,
        "ab_test": False,
        "verified": False,
        "notes": "Câu liệt-kê-điều-kiện: đo chunk coherence. Một chunk tốt phải giữ ĐỦ bộ điều kiện trong cùng ngữ cảnh, không cắt rời.",
    },
    {
        "id": "Q3",
        "kind": "quy trình",
        "query": "Sau khi hết hạn add/drop, muốn thêm một môn học thì phải làm thủ tục gì?",
        "gold_answer": "TODO",
        "gold_source": "vinuni-academic-regulations-undergrad § Rút môn (Withdrawal) và điểm W",
        "must_contain": ["petition"],
        "expected_doc_ids": [
            "vinuni-academic-regulations-undergrad",
            "vinuni-course-registration-announcement",
        ],
        "metadata_filter": None,
        "ab_test": False,
        "verified": False,
        "notes": "Hai tài liệu cùng nói về đăng ký học phần (quy chế vs thông báo thực thi). Xem chunker có phân biệt được không.",
    },
    {
        "id": "Q4",
        "kind": "liệt kê",
        "query": "Mỗi lượt mượn phòng học ở thư viện tối đa bao lâu và tối đa mấy lượt một ngày?",
        "gold_answer": "TODO",
        "gold_source": "vinuni-library-access-services § Đặt và sử dụng phòng học",
        "must_contain": ["2 hours", "2 sessions"],
        "expected_doc_ids": ["vinuni-library-access-services"],
        "metadata_filter": None,
        "ab_test": False,
        "verified": False,
        "notes": "Hai mẩu thông tin phải nằm CÙNG một chunk mới trả lời trọn vẹn. Nếu bench báo 'bằng chứng bị chia rời' thì đó chính là failure case về chunk coherence.",
    },
    {
        "id": "Q5",
        "kind": "ngoại lệ + filter",
        "query": "Vi phạm quy tắc ứng xử thì bị xử lý kỷ luật như thế nào?",
        "gold_answer": "TODO",
        "gold_source": "vinuni-student-code-of-conduct § Các mức kỷ luật và hậu quả",
        # TODO (Quân): thay bằng tên chính xác các mức kỷ luật của SINH VIÊN trong văn bản.
        "must_contain": ["TODO"],
        "expected_doc_ids": ["vinuni-student-code-of-conduct"],
        "metadata_filter": {FILTER_KEY: "student"},
        "ab_test": True,
        "verified": False,
        "notes": (
            "QUERY BẮT BUỘC FILTER của biến thể K3. Câu hỏi CỐ TÌNH không nêu người hỏi là ai. "
            "Corpus có hai văn bản cùng chủ đề, cùng từ vựng, khác audience và khác đáp án: "
            "vinuni-student-code-of-conduct (student) vs vinuni-employees-code-of-conduct (staff). "
            "Không filter, retrieval có thể trộn hai văn bản và agent trả lời theo quy trình kỷ luật nhân viên. "
            "bench.py chạy câu này HAI LẦN (có/không filter) và in hai bảng top-3 cạnh nhau."
        ),
    },
]


def validate() -> list[str]:
    """Trả về danh sách vấn đề còn tồn tại. Rỗng = sẵn sàng chạy benchmark."""
    problems: list[str] = []

    if len(QUERIES) != 5:
        problems.append(f"phải có ĐÚNG 5 query, đang có {len(QUERIES)}")

    ids = [q["id"] for q in QUERIES]
    if len(set(ids)) != len(ids):
        problems.append("id query bị trùng")

    kinds = {q["kind"] for q in QUERIES}
    if len(kinds) < 5:
        problems.append(f"5 query phải đa dạng kiểu, đang có {len(kinds)} kiểu: {sorted(kinds)}")

    filtered = [q for q in QUERIES if q["metadata_filter"]]
    if not filtered:
        problems.append(f"cần ít nhất 1 query dùng metadata_filter theo '{FILTER_KEY}'")
    for query in filtered:
        if FILTER_KEY not in query["metadata_filter"]:
            problems.append(f"{query['id']}: metadata_filter phải lọc theo '{FILTER_KEY}'")

    for query in QUERIES:
        prefix = f"{query['id']}"
        if query["gold_answer"].strip().upper().startswith("TODO"):
            problems.append(f"{prefix}: gold_answer chưa điền")
        if not query["must_contain"]:
            problems.append(f"{prefix}: must_contain rỗng")
        for needle in query["must_contain"]:
            if needle.strip().upper().startswith("TODO"):
                problems.append(f"{prefix}: must_contain còn marker TODO")
        if not query["expected_doc_ids"]:
            problems.append(f"{prefix}: chưa khai báo expected_doc_ids")
        if not query["verified"]:
            problems.append(f"{prefix}: chưa đối chiếu văn bản gốc (verified=False)")

    return problems


def main() -> int:
    print(f"=== {len(QUERIES)} benchmark query (field lọc bắt buộc: {FILTER_KEY}) ===\n")
    for query in QUERIES:
        flag = "OK " if query["verified"] else "TODO"
        print(f"[{flag}] {query['id']} ({query['kind']})")
        print(f"       query        : {query['query']}")
        print(f"       gold_answer  : {query['gold_answer'][:100]}")
        print(f"       gold_source  : {query['gold_source']}")
        print(f"       must_contain : {query['must_contain']}")
        print(f"       filter       : {query['metadata_filter']}")
        print()

    problems = validate()
    if problems:
        print(f"--- CÒN {len(problems)} VẤN ĐỀ ---")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print("--- OK: 5 query đã sẵn sàng cho benchmark ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
