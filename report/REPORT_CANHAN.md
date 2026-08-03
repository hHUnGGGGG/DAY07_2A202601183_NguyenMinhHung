# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding gần như cùng hướng trong không gian ngữ nghĩa, tức hai đoạn văn bản nói về cùng một nội dung/chủ đề. Điều này đúng kể cả khi hai câu dùng từ ngữ khác nhau hoặc độ dài khác nhau, vì cosine chỉ quan tâm hướng chứ không quan tâm độ lớn vector.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên đăng ký học phần trên cổng học vụ theo lịch của từng học kỳ."
- Câu B: "Việc đăng ký môn học được thực hiện qua cổng thông tin học vụ theo lịch mỗi kỳ."
- Tại sao tương đồng: cùng một ý (kênh và thời điểm đăng ký học phần), chỉ khác cách diễn đạt — "học phần"/"môn học", "cổng học vụ"/"cổng thông tin học vụ". Embedding mã hóa ý nghĩa nên hai vector gần như trùng hướng dù không trùng từ.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Thư viện mở cửa từ 7h30 đến 21h các ngày trong tuần."
- Câu B: "Hạn nộp học phí học kỳ 1 là ngày 30/9."
- Tại sao khác: khác chủ đề hoàn toàn (giờ mở cửa thư viện vs. hạn đóng học phí), không chia sẻ khái niệm nào ngoài việc cùng thuộc miền "dịch vụ đại học", nên hai vector gần như vuông góc.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Vì độ dài vector thường phản ánh độ dài/tần suất từ của văn bản chứ không phải ý nghĩa: một đoạn dài và một câu ngắn cùng nội dung sẽ có khoảng cách Euclid lớn nhưng cosine vẫn cao. Ngoài ra cosine luôn nằm trong [-1, 1] nên điểm số của các cặp khác nhau so sánh được trực tiếp, thuận tiện để xếp hạng kết quả truy xuất.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> - Bước nhảy (step) mỗi lần trượt cửa sổ: `500 - 50 = 450` ký tự.
> - `số chunk = ceil((10000 - 50) / 450) = ceil(9950 / 450) = ceil(22.11) = 23`
>
> *Đáp án:* **23 chunks** — đã kiểm chứng bằng chính code: `FixedSizeChunker(chunk_size=500, overlap=50).chunk("a" * 10000)` trả về đúng 23 chunk (chunk cuối dài 100 ký tự).

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Step giảm còn 400 nên `ceil((10000 - 100) / 400) = ceil(24.75) = 25` chunk, tăng 2 chunk (~9%) — code chạy thực tế cũng cho 25. Overlap lớn hơn giúp giữ ngữ cảnh vắt qua ranh giới cắt: một câu/ý bị cắt đôi vẫn còn nguyên vẹn ở chunk kế bên nên truy xuất không bị mất thông tin; cái giá phải trả là nhiều chunk hơn (tốn embedding, lưu trữ) và các kết quả top-k dễ trùng lặp nội dung.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])\s+` — lookbehind giúp **giữ lại dấu câu** ở cuối câu thay vì nuốt mất như khi `split(". ")`, và `\s+` bao trọn cả `". "`, `"! "`, `"? "` lẫn `".\n"` chỉ bằng một biểu thức. Sau khi tách, tôi `strip()` từng câu và **loại bỏ câu rỗng** để nhiều khoảng trắng/xuống dòng liên tiếp không sinh ra chunk rỗng; text rỗng hoặc toàn khoảng trắng trả về `[]`. Cuối cùng gom câu theo bước nhảy `max_sentences_per_chunk` (đã ép `max(1, ...)` trong `__init__` để tránh chia cho 0). Hạn chế đã biết: các viết tắt như "TS." hay "v.v." vẫn bị hiểu nhầm là hết câu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử từng dấu phân cách theo thứ tự "tự nhiên giảm dần" `["\n\n", "\n", ". ", " ", ""]`: cắt theo separator hiện tại rồi **gom tham lam (greedy)** các mảnh liền kề vào một buffer chừng nào tổng độ dài còn ≤ `chunk_size`, nhờ vậy chunk vừa không vượt ngưỡng vừa không bị vụn. Có **hai base case**: (1) `len(text) <= chunk_size` → trả `[text]` ngay; (2) hết separator hoặc separator là `""` → `_hard_split()` cắt cứng theo kích thước. Hai nhánh xử lý riêng: nếu separator không xuất hiện trong text (split ra đúng 1 mảnh) thì thử separator kế tiếp, còn nếu một mảnh đơn lẻ vẫn quá dài thì **đệ quy** với danh sách separator còn lại — đây chính là chỗ "recursive" của chiến lược.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Tôi chọn kho **in-memory làm nguồn dữ liệu duy nhất** (lab cho phép "in-memory hoặc ChromaDB") để hành vi lọc metadata và xóa giống hệt nhau trên mọi máy, có hay không có `chromadb`. `add_documents` gọi `_make_record()` chuẩn hóa mỗi tài liệu thành `{id, content, metadata, embedding, index}` và **embed ngay lúc ghi** — chi phí embedding trả một lần, mỗi truy vấn sau đó chỉ còn phép nhân vector. `search` embed câu hỏi rồi tính `compute_similarity` (cosine, dùng lại chính hàm ở Phần 1) với từng record, sắp xếp giảm dần rồi cắt `top_k`; vì `list.sort` của Python là **sort ổn định (stable)** nên các chunk bằng điểm vẫn giữ nguyên thứ tự nạp, kết quả tái lập được giữa các lần chạy.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Tôi **lọc TRƯỚC rồi mới tính similarity** (pre-filter): như vậy không tốn công chấm điểm cho các chunk sai đối tượng, và quan trọng hơn là `top_k` được lấp đầy bằng chunk **hợp lệ** — nếu lọc sau khi lấy top-k thì một truy vấn `audience=student` có thể trả về rỗng chỉ vì top-k toàn tài liệu dành cho `faculty`. `metadata_filter` là `None`/rỗng thì dùng toàn bộ store nên `search_with_filter` suy biến đúng thành `search`. `delete_document` lọc bỏ mọi record có `metadata['doc_id']` trùng và trả `True` nếu kích thước giảm; để một tài liệu thô (metadata rỗng) cũng xóa được, `_make_record` đã `setdefault("doc_id", doc.id)` — nhờ đó cả tài liệu đơn lẻ lẫn nhiều chunk do `ingest.py` sinh ra đều xóa được bằng một `doc_id` duy nhất.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `answer` chạy đúng ba bước RAG: `store.search(question, top_k)` → dựng prompt → `llm_fn(prompt)`. Ngữ cảnh được đưa vào dưới dạng các khối **đánh số `[1] [2] [3]` kèm nguồn (`source_url`/`source`/`doc_id`) và điểm số**, để câu trả lời có thể trích dẫn và tôi kiểm tra được chunk nào đã nuôi câu trả lời (grounding). Prompt ra chỉ thị rõ "chỉ dùng NGỮ CẢNH, nếu không đủ thông tin thì nói không tìm thấy thay vì suy đoán" — đúng yêu cầu K3 là không được suy đoán quy định của trường; khi store trả về rỗng, phần ngữ cảnh được thay bằng một câu báo không tìm thấy tài liệu liên quan.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$ pytest tests/ -v
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\AI-Action\DAY07_2A202601183_NguyenMinhHung
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
... (38 test còn lại: SentenceChunker, RecursiveChunker, EmbeddingStore,
     KnowledgeBaseAgent, compute_similarity, ChunkingStrategyComparator,
     search_with_filter, delete_document — tất cả PASSED)
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.05s ==============================
```

**Số lượng bài test vượt qua (pass):** **42** / 42

> Trước khi lập trình: 31 failed, 11 passed. Sau khi hoàn thành 13 TODO: 42/42.
> Ngoài pytest, tôi còn chạy `python ingest.py` (self-check pipeline: parse 4 khóa metadata, tạo 18 chunk giữ nguyên `doc_id`) và `python main.py "..."` (demo end-to-end: nạp store → search top-3 → agent trả lời) — cả hai đều chạy trơn.
>
> *Ghi chú môi trường:* chuẩn lab là Python 3.11; máy tôi chạy **Python 3.14.6** trong venv với đúng `requirements.txt` (pytest 9.1.1, python-dotenv 1.2.2). Không cài `chromadb` nên `EmbeddingStore` đi nhánh in-memory — đây cũng là nhánh mà toàn bộ 14 test của store kiểm tra.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Backend nhúng: **`text-embedding-3-small`** (gọi qua endpoint tương thích OpenAI). Ngưỡng phân loại cao/thấp: **0.5**. Dự đoán được ghi cứng trong script **trước khi chạy**.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1. Diễn đạt lại cùng một quy định | "Sinh viên đăng ký học phần trên cổng học vụ theo lịch của từng học kỳ." | "Việc đăng ký môn học được thực hiện qua cổng thông tin học vụ theo lịch mỗi kỳ." | cao | **0.754** (cao) | ✅ |
| 2. Hai dịch vụ khác nhau | "Thư viện mở cửa từ 7h30 đến 21h các ngày trong tuần." | "Hạn nộp học phí học kỳ 1 là ngày 30/9." | thấp | **0.321** (thấp) | ✅ |
| 3. Khẳng định vs phủ định | "Sinh viên được gia hạn sách thư viện thêm 7 ngày." | "Sinh viên **không** được gia hạn sách thư viện." | thấp | **0.792** (cao) | ❌ |
| 4. Song ngữ Việt – Anh | "Điều kiện xét học bổng khuyến khích học tập là gì?" | "What are the eligibility criteria for a merit-based scholarship?" | cao | **0.302** (thấp) | ❌ |
| 5. Trùng từ vựng nhưng khác việc | "Sinh viên nộp học phí tại phòng tài chính." | "Sinh viên nộp đơn xin ở ký túc xá tại phòng công tác sinh viên." | thấp | **0.738** (cao) | ❌ |

**Dự đoán đúng: 2/5.**

### Đối chiếu 3 backend trên cùng 5 cặp câu

Tôi chạy lại đúng script với ba trình nhúng để tách bạch "embedding hiểu sai" và "backend không đủ tốt":

| Cặp | `text-embedding-3-small` | `paraphrase-multilingual-MiniLM-L12-v2` (local) | mock (hash MD5) |
|---|---|---|---|
| 1. Diễn đạt lại | 0.754 ✅ | 0.730 ✅ | 0.019 ❌ |
| 2. Khác chủ đề | 0.321 ✅ | 0.304 ✅ | 0.121 ✅ |
| 3. Phủ định | 0.792 ❌ | 0.588 ❌ | -0.194 ✅ |
| 4. Song ngữ | 0.302 ❌ | **0.757** ✅ | -0.145 ❌ |
| 5. Trùng từ vựng | 0.738 ❌ | 0.519 ❌ | 0.149 ✅ |
| **Đúng** | 2/5 | 3/5 | 3/5 (ăn may) |

Mock "đúng 3/5" nhưng chấm cặp **cùng nghĩa** chỉ 0.019 — thấp hơn cả cặp khác chủ đề (0.121). Nó không hiểu gì cả, chỉ là băm MD5, nên mọi kết luận từ mock đều vô nghĩa.

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là **cặp 3**: hai câu **ngược nghĩa hoàn toàn** lại được 0.792 — *cao hơn cả* cặp diễn đạt lại đúng nghĩa (0.754). Chữ "không" gần như không làm vector dịch chuyển, cho thấy embedding mã hóa **chủ đề và thành phần từ vựng** chứ không mã hóa **giá trị đúng/sai** của câu; cặp 5 củng cố điều đó — cùng khung "sinh viên nộp… tại phòng…" là đủ để được 0.738 dù hai thủ tục chẳng liên quan. Hệ quả trực tiếp cho RAG: hệ thống hoàn toàn có thể truy xuất đúng chunk nói **điều ngược lại** với đáp án, nên điểm số cao không phải bằng chứng câu trả lời đúng — phải đọc lại chunk và đối chiếu gold answer thay vì tin vào score.
>
> Phát hiện thứ hai quan trọng cho bài lab này: ở **cặp 4**, `text-embedding-3-small` chỉ cho 0.302 trong khi model đa ngữ local cho 0.757 — chênh nhau 0.45 trên cùng một cặp câu. Bộ tài liệu nhóm tôi thu thập từ VinUniversity **phần lớn bằng tiếng Anh**, còn câu hỏi đánh giá sẽ đặt bằng tiếng Việt, nên **lựa chọn model nhúng có thể quyết định thành bại của truy xuất nhiều hơn cả chiến lược chunking**. Đây là điều tôi sẽ kiểm chứng ở Phần 5.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
