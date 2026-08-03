# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Minh Hùng — 2A202601183
**Nhóm:** B4-E402 — vai trò: **Repo owner / Đồng bộ**
**Ngày:** 3/8/2026
**Chiến lược chunking của tôi:** `FixedSizeChunker(chunk_size=500, overlap=50)`

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> Hai đoạn văn bản có vector nhúng gần như cùng hướng trong không gian ngữ nghĩa cao chiều, tức là chúng nói về cùng một chủ đề hoặc có nội dung tương tự nhau. Cosine similarity đo lường góc giữa hai vector (bỏ qua độ lớn/độ dài của vector), do đó ngay cả khi hai câu dài ngắn khác nhau, miễn là ý nghĩa tương đồng thì độ tương tự vẫn cao.

**Ví dụ có độ tương tự CAO:**

- Câu A: "Sinh viên đăng ký học phần trên cổng học vụ theo lịch của từng học kỳ."
- Câu B: "Việc đăng ký môn học được thực hiện qua cổng thông tin học vụ theo lịch mỗi kỳ."
- Tại sao tương đồng: Ý nghĩa hoàn toàn giống nhau, chỉ sử dụng từ ngữ đồng nghĩa ("học phần" - "môn học", "cổng học vụ" - "cổng thông tin học vụ").

**Ví dụ có độ tương tự THẤP:**

- Câu A: "Thư viện mở cửa từ 7h30 đến 21h các ngày trong tuần."
- Câu B: "Hạn nộp học phí học kỳ 1 là ngày 30/9."
- Tại sao khác: Nội dung hoàn toàn khác biệt, một bên nói về thời gian hoạt động của thư viện, bên kia nói về thời hạn nộp học phí.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

> Khoảng cách Euclid bị ảnh hưởng rất lớn bởi độ dài của vector. Nếu một văn bản dài lặp lại nhiều lần một từ khóa, vector của nó sẽ dài hơn, khiến khoảng cách Euclid đến một văn bản ngắn (dù cùng nội dung) trở nên lớn. Ngược lại, Cosine similarity chỉ quan tâm đến hướng (tỷ lệ phân bố các đặc trưng ngữ nghĩa), không bị nhiễu bởi độ dài văn bản, rất phù hợp cho việc so sánh ngữ nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> *Trình bày phép tính:*
>
> - Bước nhảy (step) mỗi lần trượt: `chunk_size - overlap = 500 - 50 = 450` ký tự.
> - `số lượng chunk = ceil((10,000 - 50) / 450) = ceil(9,950 / 450) = ceil(22.11) = 23`
>
> *Đáp án:* **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> - Bước nhảy giảm còn: `500 - 100 = 400` ký tự.
> - `số lượng chunk = ceil((10,000 - 100) / 400) = ceil(9,900 / 400) = ceil(24.75) = 25`
> - **Thay đổi:** Số lượng chunk tăng lên thành 25 (tăng thêm 2 chunks).
> - **Lý do tăng overlap:** Việc tăng overlap giúp đảm bảo các câu dài hoặc các thông tin ngữ nghĩa nằm ở ranh giới giữa hai chunk không bị cắt đứt hoàn toàn, giúp tăng khả năng truy xuất (retrieval) chính xác vì LLM sẽ nhận được đầy đủ bối cảnh hơn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)
**`SentenceChunker` và `RecursiveChunker`** — hướng tiếp cận:
> Tôi triển khai `SentenceChunker` bằng cách sử dụng Regex với Lookbehind `(?<=[.!?])\s+` để tách câu mà không làm mất các dấu chấm câu kết thúc. Sau đó gom các câu lại dựa vào biến `max_sentences_per_chunk`.
> Với `RecursiveChunker`, thuật toán duyệt qua danh sách các `separators`. Nếu phân tách theo separator đầu tiên mà tạo ra mảnh lớn hơn `chunk_size`, thuật toán sẽ đệ quy cắt tiếp bằng các `remaining_separators`. Sau đó gom nhóm tham lam (greedy) các mảnh lại sao cho vừa khít `chunk_size` nhất. Nếu cạn separator, nó dùng fallback chia cứng (hard split).

### Lớp EmbeddingStore
**`add_documents` + `search` + `search_with_filter`** — hướng tiếp cận:
> Tôi tập trung xử lý nhánh in-memory bằng danh sách dictionaries. `add_documents` embed toàn bộ nội dung trong lúc nạp, chuẩn hoá các chunk chứa `doc_id` vào `metadata`. Hàm `search_with_filter` lọc các chunk bằng metadata trước, sau đó mới gọi `_search_records` để tính Cosine Similarity (`compute_similarity`), sort và lấy `top_k`. Việc lọc trước (pre-filtering) giúp đảm bảo top_k luôn chứa tài liệu hợp lệ. 

### Tác tử KnowledgeBaseAgent
**`answer`** — hướng tiếp cận:
> Phương thức `answer` thực hiện quy trình chuẩn RAG. Lấy `top_k` chunk từ `EmbeddingStore` rồi xây dựng prompt bằng `_build_prompt` với việc gắn nhãn theo cấu trúc: `[1] nguồn: <doc_id> | score=...` để LLM dễ dàng trích dẫn thông tin. System prompt được viết rất rõ nhằm giới hạn tác tử không được bịa thông tin và phải trả lời "không tìm thấy" nếu mảng context (ngữ cảnh) trả về kết quả rỗng.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết Quả Kiểm Thử (Test Results)

```text
$ pytest tests/ -v
============================= test session starts =============================
platform win32 -- Python 3.13.0, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\AI_Thuc_Chien\Lab07\DAY07_2A202601183_NguyenMinhHung
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
...
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.07s ==============================
```

**Số lượng bài test vượt qua (pass):** **42** / 42

> Tất cả các Unit Tests bao gồm store, chunker, similarity, filter metadata đều passed 100%.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Dưới đây là dự đoán độ tương tự trên mô hình `paraphrase-multilingual-MiniLM-L12-v2`:

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
| --- | ----- | ----- | ------- | ------------ | ----- |
| 1. Diễn đạt lại | "Sinh viên đăng ký học phần trên cổng học vụ theo lịch của từng học kỳ." | "Việc đăng ký môn học được thực hiện qua cổng thông tin học vụ theo lịch mỗi kỳ." | cao | 0.730 (cao) | ✅ |
| 2. Khác chủ đề | "Thư viện mở cửa từ 7h30 đến 21h các ngày trong tuần." | "Hạn nộp học phí học kỳ 1 là ngày 30/9." | thấp | 0.304 (thấp) | ✅ |
| 3. Phủ định | "Sinh viên được gia hạn sách thư viện thêm 7 ngày." | "Sinh viên **không** được gia hạn sách thư viện." | thấp | 0.588 (cao) | ❌ |
| 4. Song ngữ | "Điều kiện xét học bổng khuyến khích học tập là gì?" | "What are the eligibility criteria for a merit-based scholarship?" | cao | 0.757 (cao) | ✅ |
| 5. Trùng từ vựng | "Sinh viên nộp học phí tại phòng tài chính." | "Sinh viên nộp đơn xin ở ký túc xá tại phòng công tác sinh viên." | thấp | 0.519 (cao) | ❌ |

**Phản ngẫm:**
> Vector Embeddings dễ dàng bị đánh lừa bởi các cặp câu có phủ định (cặp số 3) và các cặp câu có cùng khuôn mẫu từ vựng (cặp số 5). Các vector chỉ tập hợp ngữ nghĩa chung (semantic framing) thay vì mang cấu trúc logic đúng/sai.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Điều kiện chạy: `py bench.py --strategy fixed`, corpus `data/k3_university`, `EMBEDDING_PROVIDER=local` (`paraphrase-multilingual-MiniLM-L12-v2`), `top_k=3`. 
Chiến lược: **FixedSizeChunker(chunk_size=500, overlap=50)**. Có **342 chunk** được nạp vào store.

### Kết quả Benchmark 

| # | Câu hỏi (Query) | Điểm | Hạng bằng chứng | Doc gold trong top-3 | Ghi chú |
|---|---|---|---|---|---|
| Q1 | Hạn chót drop môn của học kỳ chính... | 0/2 | - | CÓ | không tìm thấy bằng chứng trong top-3 |
| Q2 | Điều kiện xét Special Sponsor... | 0/2 | - | CÓ | không tìm thấy bằng chứng trong top-3 |
| Q3 | Sau khi hết hạn add/drop, muốn thêm môn... | 0/2 | - | CÓ | không tìm thấy bằng chứng trong top-3 |
| Q4 | Lượt đặt phòng chức năng ở thư viện... | 0/2 | - | CÓ | không tìm thấy bằng chứng trong top-3 |
| Q5 | Vi phạm quy định thư viện xử lý thế nào? | 0/2 | - | CÓ | không tìm thấy bằng chứng trong top-3 |

**Điểm Retrieval tự động: 0/10.**

### Phân Tích Lỗi (Failure Analysis)

**1. Vấn đề gì đã xảy ra?**
Chiến lược của tôi đạt **0/10** điểm truy xuất tự động. Thú vị thay, đối với tất cả 5 câu hỏi, tài liệu đúng (Gold Document) **đều xuất hiện trong top-3**, nhưng đoạn chunk chứa câu trả lời (Gold Chunk) lại **không lọt vào top-3**.

**2. Nguyên nhân (từ góc độ Chunk Coherence):**
`FixedSizeChunker(500, 50)` là một chiến lược cắt cứng (blind splitting). Với 500 ký tự (chưa tới 100 từ), một đoạn thông tin hữu ích thường bị băm vụn bất chấp ranh giới câu. Chunk chứa câu trả lời (ví dụ: con số `15th business day` của Q1 hoặc `2 hours` của Q4) bị chia tách ra thành các mảnh nhỏ, và mảnh chứa đáp án lại thiếu vắng hoàn toàn các từ khoá bối cảnh (như "registration", "drop", "library").
Do đó, khi tính toán độ tương tự (Cosine Similarity) với câu hỏi, chunk chứa câu trả lời thực sự bị lu mờ bởi các chunk "nhiễu" có chứa nhiều từ khóa trùng lặp nhưng lại không có lời giải.

**3. Đề xuất cải thiện:**
Việc cắt cứng kích thước là một chiến lược kém hiệu quả cho hệ thống RAG yêu cầu độ chính xác cao về chi tiết. 
Nên chuyển sang dùng `SentenceChunker` (cắt theo câu) hoặc `RecursiveChunker` (cắt theo ngữ nghĩa xuống dòng/dấu chấm). Nếu vẫn muốn dùng FixedSizeChunker, phải tăng overlap lên rất cao (vd: 200 ký tự) để hạn chế rủi ro chia cắt từ khóa khỏi ngữ cảnh, dù phải đánh đổi chi phí số lượng token lớn.
