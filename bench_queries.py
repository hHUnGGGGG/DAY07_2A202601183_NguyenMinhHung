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

BẢN CHỈNH 2026-08-03 — NẮN THEO CORPUS THỰC TẾ:
  Bản nháp đầu tiên viết theo `docs/CORPUS_PLAN.md` (8 tài liệu dự kiến, doc_id tiền
  tố `vinuni-`). Corpus thu thập được chỉ có 7 tài liệu và dùng tiền tố `k3-`, trong
  đó thiếu hẳn `scholarship-maintenance`, `student-code-of-conduct`,
  `employees-code-of-conduct` và `course-registration-announcement`. Vì corpus đã
  chốt và KHÔNG đổi, 5 query được nắn lại cho khớp:
    * doc_id: `vinuni-*` -> `k3-*`.
    * Q2 (điều kiện): bỏ "duy trì học bổng đầu vào" (không có tài liệu) -> chuyển
      sang điều kiện xét Special Sponsor Scholarship trong `k3-undergrad-scholarships`.
    * Q5 (ngoại lệ + filter): cặp đối chứng student-vs-staff không còn là hai bản quy
      tắc ứng xử, mà là hai văn bản THƯ VIỆN có sẵn trong corpus:
      `k3-library-access-services-policy` (audience=student, nghĩa vụ người mượn) vs
      `k3-library-management-regulation` (audience=staff, quy trình sửa chữa nội bộ).
      Cùng từ vựng "damage", khác hẳn đáp án -> bẫy filter vẫn nguyên giá trị.
  Mọi `must_contain` đã grep đối chiếu: mỗi chuỗi chỉ xuất hiện trong đúng tài liệu
  gold (riêng "academic advisor" còn nằm ở tài liệu tài chính nên Q3 dùng 2 needle).

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
        "gold_answer": (
            "Chậm nhất là hết ngày làm việc thứ 15 của học kỳ (no later than the close of the "
            "15th business day of the semester); với học kỳ Summer là ngày làm việc thứ 10. "
            "Thay đổi thực hiện trong thời hạn này không bị ghi vào học bạ."
        ),
        "gold_source": "k3-academic-regulations-undergrad § Article 12. Course Add, Drop, and Withdrawal",
        "must_contain": ["15th business day"],
        "expected_doc_ids": ["k3-academic-regulations-undergrad"],
        "metadata_filter": None,
        "ab_test": False,
        "verified": True,
        "notes": (
            "Kiểm khả năng lấy đúng con số. Cùng một đoạn văn còn nêu 10th business day (hạn ADD "
            "của học kỳ chính) và 10th business day của Summer, cộng 5th business day cho mini "
            "semester — chunk trả về phải là mốc DROP của học kỳ chính, không phải ba mốc kia."
        ),
    },
    {
        "id": "Q2",
        "kind": "điều kiện",
        "query": "Điều kiện để được xét Special Sponsor Scholarship từ quỹ tư nhân là gì?",
        "gold_answer": (
            "Dành cho ứng viên xuất sắc đã được cấp học bổng Merit-based từ 80% trở lên "
            "(a Merit-based Scholarship of 80% or higher) nhưng gặp rào cản tài chính; khoản này "
            "hỗ trợ thêm 10% học phí và được xét theo tiêu chí riêng của từng quỹ tài trợ."
        ),
        "gold_source": "k3-undergrad-scholarships § Special Sponsor Scholarships from Private Fund",
        "must_contain": ["80% or higher"],
        "expected_doc_ids": ["k3-undergrad-scholarships"],
        "metadata_filter": None,
        "ab_test": False,
        "verified": True,
        "notes": (
            "Câu hỏi điều kiện trên tài liệu dày đặc con số nhiễu (35% tuition subsidy, 50-100% "
            "merit, 5% WIT/Vinschool, 10% Dean Choi). Đo xem retrieval lấy đúng ĐIỀU KIỆN XÉT hay "
            "chỉ lấy bảng liệt kê mức học bổng."
        ),
    },
    {
        "id": "Q3",
        "kind": "quy trình",
        "query": "Sau khi hết hạn add/drop, muốn thêm một môn học thì phải làm thủ tục gì?",
        "gold_answer": (
            "Phải nộp đơn xin (petition) và được cố vấn học tập (academic advisor) hoặc Phòng Đào "
            "tạo (Office of Registrar) phê duyệt; giảng viên có toàn quyền quyết định có nhận thêm "
            "sinh viên vào lớp hay không."
        ),
        "gold_source": "k3-academic-regulations-undergrad § Article 12. Course Add, Drop, and Withdrawal",
        "must_contain": ["petition", "academic advisor"],
        "expected_doc_ids": ["k3-academic-regulations-undergrad"],
        "metadata_filter": None,
        "ab_test": False,
        "verified": True,
        "notes": (
            "Từ 'petition' xuất hiện ở ÍT NHẤT 4 ngữ cảnh khác nhau trong cùng tài liệu (gia hạn "
            "thời gian học, đăng ký vượt tín chỉ, chuyển đổi tín chỉ, thêm môn sau add/drop) nên "
            "một needle là không đủ — phải có cả 'academic advisor' trong CÙNG chunk. Đây là chỗ "
            "chunker cắt quá vụn sẽ lộ ra ngay."
        ),
    },
    {
        "id": "Q4",
        "kind": "liệt kê",
        "query": "Mỗi lượt đặt phòng chức năng ở thư viện tối đa bao lâu và tối đa mấy lượt một ngày?",
        "gold_answer": (
            "Tối đa 2 giờ mỗi lượt và 2 lượt mỗi ngày, tính gộp cho tất cả các phòng "
            "(Max: 2 hours/session, 2 sessions/day for all rooms combined). Chỉ dùng cho mục đích "
            "học thuật, đặt trước qua Microsoft Outlook trong vòng 1 tuần, quá 10 phút không đến "
            "thì lượt đặt bị huỷ."
        ),
        "gold_source": "k3-library-access-services-policy § 3.2 Using Library Functional Rooms",
        "must_contain": ["2 hours/session", "2 sessions/day"],
        "expected_doc_ids": ["k3-library-access-services-policy"],
        "metadata_filter": None,
        "ab_test": False,
        "verified": True,
        "notes": (
            "Hai mẩu thông tin nằm trên CÙNG một dòng trong nguồn. Nếu chunker cắt vào giữa dòng "
            "này, bench sẽ báo 'bằng chứng BỊ CHIA RỜI' — đó chính là failure case về chunk "
            "coherence để viết vào report. Lưu ý nhiễu: tài liệu còn có '2 hours' cho Course "
            "Reserve Books và '2 weeks' cho hạn mượn sách."
        ),
    },
    {
        "id": "Q5",
        "kind": "ngoại lệ + filter",
        "query": "Vi phạm quy định thư viện thì bị xử lý như thế nào?",
        "gold_answer": (
            "Theo góc nhìn SINH VIÊN: sinh viên vi phạm quy định thư viện có thể bị xử lý kỷ luật "
            "theo Student Code of Conduct của VinUni (students who break library rules may face "
            "penalties based on VinUni's Student Code of Conduct); ngoài ra bị phạt tiền khi trả "
            "muộn hoặc làm hỏng/mất tài liệu, thiết bị, mức phạt theo Financial Regulations and "
            "Tariff, chia hai mức Minor damage và Major damage/loss. Chỉ được miễn phạt trong "
            "trường hợp nghiêm trọng (ốm đau, nhập viện — có bằng chứng); khiếu nại gửi email cho "
            "thư viện, xét theo từng trường hợp."
        ),
        "gold_source": "k3-library-access-services-policy § 4. Library regulation violations (4.1 Consequences)",
        "must_contain": ["break library rules", "Student Code of Conduct"],
        "expected_doc_ids": ["k3-library-access-services-policy"],
        "metadata_filter": {FILTER_KEY: "student"},
        "ab_test": True,
        "verified": True,
        "notes": (
            "QUERY BẮT BUỘC FILTER của biến thể K3. Câu hỏi CỐ TÌNH không nêu người hỏi là ai. "
            "Cặp đối chứng: k3-library-access-services-policy (audience=student, §4.1 — sinh viên "
            "vi phạm bị xử lý theo Student Code of Conduct) vs k3-library-management-regulation "
            "(audience=staff, §3.3 — NHÂN VIÊN thư viện phải lập biên bản và đề xuất xử phạt sinh "
            "viên vi phạm, cũng viện dẫn 'Student code of conduct'). Hai văn bản gần như trùng chủ "
            "đề và từ vựng, nhưng một bên là NGHĨA VỤ CỦA SINH VIÊN, bên kia là QUY TRÌNH TÁC "
            "NGHIỆP CỦA NHÂN VIÊN — không filter thì agent dễ trả lời sinh viên bằng quy trình nội "
            "bộ. Cặp needle ['break library rules', 'Student Code of Conduct'] chỉ khớp bản dành "
            "cho sinh viên: cụm 'Student Code of Conduct' xuất hiện ở 4/7 tài liệu nên một mình nó "
            "KHÔNG đủ phân biệt. bench.py chạy câu này HAI LẦN (có/không filter), in hai bảng "
            "top-3 cạnh nhau. Ghi chú lịch sử: bản đầu neo vào bảng 'Minor damage / Major damage' "
            "§4.2, nhưng chunk đó chỉ ra top-3 khi câu hỏi lặp gần đúng từ khoá của bảng — thành "
            "ra đo trí nhớ từ vựng thay vì đo tác dụng của filter, nên đã đổi neo sang §4.1 TRƯỚC "
            "khi có ai chạy benchmark để lấy số báo cáo."
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
