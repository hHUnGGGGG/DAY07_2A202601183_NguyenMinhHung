# Spec — Lab 07 (K3): Knowledge Base Truy xuất Quy định VinUniversity

- **Ngày:** 2026-08-03
- **Lớp / biến thể:** K3 — Dịch vụ hoặc quy định đại học (`K3_VARIANT.md`)
- **Nhóm:** 5 thành viên
- **Trạng thái:** đã chốt, dùng làm căn cứ cho `docs/superpowers/plans/2026-08-03-lab07-k3-vinuni-plan.md`

---

## 1. Mục tiêu và phạm vi

Nhóm xây một knowledge base RAG trên **quy định và dịch vụ công khai của VinUniversity**, rồi so sánh 5 chiến lược chunking khác nhau trên **cùng một corpus** và **cùng một bộ 5 benchmark query**. Đầu ra chấm điểm gồm:

| Đầu ra | Ai nộp | Điểm |
|---|---|---|
| `src/` pass 42 test + `REPORT_CANHAN.md` | mỗi người một bản, trong repo riêng | 60 |
| Corpus + 5 query + `REPORT_NHOM.md` + demo | nhóm, 1 bản (copy vào cả 5 repo) | 40 |

**Ngoài phạm vi (YAGNI):** không dùng ChromaDB (`_use_chroma = False`, mọi method đi qua `_store`); không viết crawler mới; không fine-tune embedding; không xây UI.

## 2. Ràng buộc kiến trúc quan trọng nhất: 5 repo, 1 corpus

Quy ước nộp bài là **mỗi sinh viên một repo** `DAY07-<MSSV>-<HoTen>`. Do đó:

- **Dùng chung (phải byte-identical giữa 5 repo):** `data/k3_university/` (8 file + `sources.csv`), `bench_queries.py`, `report/REPORT_NHOM.md`.
- **Riêng từng người:** toàn bộ `src/` (tự code, đây là 30 điểm cá nhân), `report/REPORT_CANHAN.md`, và **đúng một dòng** chọn chunker trong `bench.py`.

Repo của Nguyễn Minh Hùng là **nguồn chuẩn (upstream)**. Bốn người còn lại copy 3 artifact dùng chung sang repo mình sau mỗi lần upstream cập nhật. Nếu ai đó tự sửa corpus hoặc query cục bộ, kết quả benchmark của nhóm mất tính so sánh được — đây là rủi ro số một của bài này.

**Bất biến cần giữ:** cùng corpus, cùng 5 query, cùng embedding backend (`EMBEDDING_PROVIDER`), cùng `top_k=3`. Biến duy nhất được phép thay đổi là chiến lược chunking.

## 3. Corpus

### 3.1 Nguồn

Cổng chính sách công khai của VinUniversity:

- `https://policy.vinuni.edu.vn/` — `robots.txt` là `User-agent: * / Disallow:` (không cấm mục nào), có `sitemap_index.xml`.
- `https://registrar.vinuni.edu.vn/` — thông báo học vụ công khai.

Cổng này **tự phân loại chính sách theo "Policy by Users: Student / Faculty and Staff"**, ánh xạ trực tiếp vào field `audience` bắt buộc của K3.

> **Ràng buộc kỹ thuật đã kiểm chứng (2026-08-03):** cả `vinuni.edu.vn` và `policy.vinuni.edu.vn` trả **HTTP 403 cho user-agent tự động**, kể cả với file PDF trong `wp-content`. Vì vậy `scripts/fetch_public_pages.py` **sẽ fail** trên nguồn này. Cách thu thập chính thức của nhóm là **mở trình duyệt, đọc, copy phần công khai, làm sạch thủ công** — đúng cách `docs/DATA_COLLECTION.md` mục 2.4 khuyến nghị ("với quy mô lab, copy/clean thủ công 5–10 trang là đủ"). Không tìm cách vượt 403.

### 3.2 Tám tài liệu

| # | `doc_id` | `audience` | `department` | `category` | Trang nguồn |
|---|---|---|---|---|---|
| 1 | `vinuni-library-access-services` | student | library | library-services | `policy.vinuni.edu.vn/all-policies/library-policies-for-users/` |
| 2 | `vinuni-academic-regulations-undergrad` | student | registrar | academic-regulations | `.../academic-regulations-for-full-time-undergraduate-programs/` |
| 3 | `vinuni-student-code-of-conduct` | student | student-affairs | code-of-conduct | `.../student-affairs-regulations-code-of-conduct/` |
| 4 | `vinuni-financial-regulations-student` | student | finance | tuition-fees | `.../financial-regulations-and-tariff-for-student-2/` |
| 5 | `vinuni-scholarship-maintenance` | student | finance | scholarship | `.../criteria-to-maintain-the-entry-scholarship-and-financial-aid-support/` |
| 6 | `vinuni-employees-code-of-conduct` | staff | hr | code-of-conduct | `.../code-of-conduct/` |
| 7 | `vinuni-faculty-appointment-promotion` | faculty | hr | faculty-affairs | `.../faculty-appointment-and-promotion-policy-and-procedures/` |
| 8 | `vinuni-course-registration-announcement` | student | registrar | course-registration | `registrar.vinuni.edu.vn/.../official-announcement-spring-2026-course-registration/` |

Chi tiết từng tài liệu (URL đầy đủ, phần cần lấy, anchor fact cần xác minh) nằm ở `docs/CORPUS_PLAN.md`.

**Cặp đối chứng (#3 và #6)** là trục thiết kế của cả bài: hai văn bản *cùng chủ đề "code of conduct / kỷ luật", cùng từ vựng, khác `audience`, khác đáp án*. Không có cặp này thì query filter ở mục 4 không chứng minh được gì.

`audience` có 3 giá trị (`student` ×6, `staff` ×1, `faculty` ×1) — vượt yêu cầu "ít nhất 2 giá trị khác nhau" của CHECKPOINT 2.

### 3.3 Ngôn ngữ và việc dịch

VinUni publish policy bằng tiếng Anh. Nhóm **dịch phần thân sang tiếng Việt** theo quy tắc:

1. **Không đổi số**: mọi con số, mốc thời gian, phần trăm, mã văn bản giữ nguyên.
2. **Giữ thuật ngữ gốc trong ngoặc** ở lần xuất hiện đầu: `ngày làm việc thứ 15 (the 15th business day)`.
3. Khai báo trong front matter: `language: vi`, `source_language: en`, `translation: manual-vi`.
4. Không thêm thông tin không có trong nguồn. Chỗ nào không hiểu thì trích nguyên câu tiếng Anh, không đoán.

Hệ quả có lợi cho benchmark: các chuỗi `must_contain` nên chọn **số hoặc thuật ngữ tiếng Anh giữ nguyên** (`15th business day`, `35%`, `2 hours`) — chúng bất biến qua bản dịch nên việc chấm không phụ thuộc cách hành văn của người dịch.

### 3.4 Schema metadata

```yaml
---
doc_id: vinuni-library-access-services      # bắt buộc, trùng tên file, không dấu
title: Chính sách Truy cập và Dịch vụ Thư viện
source_url: https://policy.vinuni.edu.vn/all-policies/library-policies-for-users/
retrieved_at: 2026-08-03                    # bắt buộc, YYYY-MM-DD
document_version: POL-LLR-001-V4.0          # bắt buộc, mã/ngày hiệu lực, hoặc not-stated
audience: student                           # bắt buộc K3: student | faculty | staff | all
department: library                         # trường lọc phụ
category: library-services                  # trường lọc phụ
effective_date: 2025-07-09
language: vi
source_language: en
translation: manual-vi
---
```

Ba field cuối tồn tại vì mục 3.3, không phải để trang trí. `department` và `category` được chọn vì chúng là hai chiều lọc **thực sự phân biệt** trong corpus này (library/registrar/finance/hr/student-affairs; và cặp `code-of-conduct` xuất hiện ở đúng 2 doc khác audience). Không thêm field nào không phục vụ một query cụ thể.

`sources.csv` giữ đúng header của `docs/DATA_COLLECTION.md` mục 5 và khớp 1–1 với 8 file.

## 4. Năm benchmark query

Nguyên tắc: đủ 5 kiểu (số liệu / điều kiện / quy trình / liệt kê / ngoại lệ+filter), gold answer trích được từ corpus, **chốt xong là không đổi**.

| # | Kiểu | Query (tiếng Việt) | Doc gold | `must_contain` (dự kiến) | Filter |
|---|---|---|---|---|---|
| Q1 | Số liệu | Hạn chót drop môn của học kỳ chính là ngày làm việc thứ mấy? | #2 | `15th business day` | — |
| Q2 | Điều kiện | Sinh viên phải đạt những điều kiện nào để tiếp tục được giữ học bổng đầu vào? | #5 | (mã tiêu chí trong văn bản) | — |
| Q3 | Quy trình | Sau khi hết hạn add/drop, muốn thêm một môn học thì phải làm thủ tục gì? | #2, #8 | `petition` | — |
| Q4 | Liệt kê | Mỗi lượt mượn phòng học ở thư viện tối đa bao lâu và tối đa mấy lượt một ngày? | #1 | `2 hours`, `2 sessions` | — |
| Q5 | Ngoại lệ + filter | **"Vi phạm quy tắc ứng xử thì bị xử lý kỷ luật như thế nào?"** | #3 (student) vs #6 (staff) | (mức kỷ luật trong #3) | `{"audience": "student"}` |

**Thiết kế Q5.** Câu hỏi cố tình *không nêu người hỏi là ai*. Không filter, retrieval sẽ trộn #3 và #6 vì hai văn bản dùng gần như cùng bộ từ vựng, và agent có thể trả lời theo quy trình kỷ luật nhân viên. Có `metadata_filter={"audience": "student"}` thì #6 bị loại **trước khi** xếp hạng. `bench.py` chạy Q5 **hai lần (A/B)** và in cả hai bảng top-3 cạnh nhau — đây là bằng chứng cho mục "Metadata Utility" của `docs/EVALUATION.md`.

**Chấm ở mức chunk, không phải mức doc.** Mỗi query khai báo một `must_contain` — chuỗi đặc trưng bắt buộc phải xuất hiện trong context top-3. Lý do: một strategy có thể chiếm cả 3 slot bằng đúng doc gold mà không chunk nào chứa câu trả lời (hay gặp với chunker theo heading, vì các section trong cùng văn bản có score sát nhau). Điểm tự động:

| Điều kiện | Điểm |
|---|---|
| `must_contain` nằm trong chunk **top-1** | 2 |
| `must_contain` nằm trong chunk top-2 hoặc top-3 | 1 |
| không thấy trong top-3 | 0 |

Đây là **điểm retrieval tự động**, là cận trên của điểm rubric. Điểm cuối cùng còn cần người đọc kiểm câu trả lời của agent (rubric: 2 điểm = top-3 có chunk liên quan **và** agent trả lời đúng). `bench.py` in cả hai và ghi rõ phần nào cần chấm tay.

## 5. Năm chiến lược chunking

| Thành viên | Strategy | Tham số | Vì sao khác biệt này đáng đo |
|---|---|---|---|
| Nguyễn Minh Hùng | `FixedSizeChunker` | `chunk_size=500, overlap=50` | Đường cơ sở có overlap. Overlap cho mỗi thông tin hai cơ hội lọt top-k. |
| Hoàng Anh Quân | `SentenceChunker` | `max_sentences_per_chunk=3` | Không bao giờ cắt giữa câu, nhưng chunk ngắn → điều kiện và ngoại lệ dễ bị tách rời. |
| Phạm Hải Đăng | `RecursiveChunker` | `chunk_size=400` | Tôn trọng ranh giới đoạn trước, chỉ hạ cấp khi cần. |
| Bùi Gia Huy | `HeadingChunker` | `max_chunk_size=800`, fallback recursive | Văn bản quy định biên soạn theo mục; mỗi mục đã là đơn vị ngữ nghĩa trọn vẹn. |
| Nguyễn Huy Đức | `HeadingRecursiveChunker` | như trên + **gắn lại breadcrumb tiêu đề** vào từng mảnh con | Cặp đối chứng của Huy: đo đúng một biến — mảnh thứ hai trở đi của một section dài có mất ngữ cảnh tiêu đề hay không. |

Cặp Huy/Đức là thí nghiệm được thiết kế: hai người dùng **cùng thuật toán, khác đúng một chi tiết**, nên chênh lệch kết quả giữa họ quy được về nguyên nhân duy nhất. Đây là nội dung có giá trị nhất cho mục "So sánh giữa các thành viên" (15 điểm Strategy Design).

`HeadingChunker` và `HeadingRecursiveChunker` đặt ở **file mới `src/heading_chunker.py`**, không sửa `src/chunking.py`, để 42 test hiện có không bị ảnh hưởng.

## 6. Kiến trúc code

```
tài liệu .md ──▶ ingest.load_documents()      # parse front matter (ĐÃ CÓ SẴN)
                        │
                        ▼
              ingest.chunk_document(doc, chunker)   # chunker RIÊNG của từng người
                        │  metadata trải xuống mọi chunk, id = doc_id::chunk_N
                        ▼
              EmbeddingStore.add_documents()   # TỰ CODE (Task 4)
                        │
      ┌─────────────────┴──────────────────┐
      ▼                                    ▼
  search(q, top_k)                search_with_filter(q, top_k, filter)
      │                                    │     (lọc TRƯỚC, xếp hạng SAU)
      └─────────────┬──────────────────────┘
                    ▼
        KnowledgeBaseAgent.answer()   # TỰ CODE (Task 6), context đánh số [1][2][3]
```

### 6.1 File phải viết

| File | Ai viết | Trạng thái | Ghi chú |
|---|---|---|---|
| `src/chunking.py` | **cả 5 người, mỗi người trong repo mình** | 4 TODO | `SentenceChunker.chunk`, `RecursiveChunker.chunk`/`._split`, `compute_similarity`, `ChunkingStrategyComparator.compare` |
| `src/store.py` | **cả 5 người** | 5 TODO | `_make_record`, `_search_records`, `add_documents`, `search`, `get_collection_size`, `search_with_filter`, `delete_document` |
| `src/agent.py` | **cả 5 người** | 2 TODO | `__init__`, `answer` |
| `src/heading_chunker.py` | Huy (`HeadingChunker`), Đức (`HeadingRecursiveChunker`) | mới, skeleton | không đụng `src/chunking.py` |
| `bench_queries.py` | Quân | mới, dùng chung | 5 query + gold + `must_contain` + filter |
| `bench.py` | Hùng viết, cả 5 dùng | mới | chỉ **dòng chọn chunker** là khác nhau giữa các repo |
| `scripts/check_corpus.py` | Huy | mới | tự động hoá CHECKPOINT 2 |
| `data/k3_university/*.md` + `sources.csv` | Đăng (curator), cả nhóm dịch | scaffold sẵn | |

### 6.2 Ràng buộc thiết kế bắt buộc

- `EmbeddingStore._make_record` phải **copy** metadata (`dict(doc.metadata)`), không giữ tham chiếu của caller.
- `search()` và `search_with_filter()` **dùng chung** `_search_records()`. Nhờ vậy `metadata_filter=None` cho kết quả y hệt `search()` — nếu viết hai đường code riêng, hai hàm sẽ lệch nhau lúc nào không biết.
- `search_with_filter` **lọc trước, xếp hạng sau**. Làm ngược lại (lấy top-k rồi bỏ record không khớp) có thể trả 0 kết quả dù store vẫn còn tài liệu hợp lệ. Report hỏi thẳng câu này.
- `delete_document(doc_id)` xoá theo `metadata['doc_id']` (trỏ về **file gốc**), không theo `Document.id` của chunk (`doc_id::chunk_3`).
- `KnowledgeBaseAgent.answer` đánh số context `[1] [2] [3]` kèm `doc_id` — đây là tiêu chí Source Traceability của `docs/EVALUATION.md`.
- Store rỗng → trả thông báo rõ ràng, không gọi `llm_fn`.
- `self._use_chroma = False`.

## 7. Embedding backend

- **Unit test (42 test):** luôn `MockEmbedder` — deterministic, không mạng, không API key.
- **Benchmark (mục 6–7 của đề):** `EMBEDDING_PROVIDER=local` với `paraphrase-multilingual-MiniLM-L12-v2` (`requirements-local.txt`). Bắt buộc dùng bản local vì corpus là **tiếng Việt đã dịch từ tiếng Anh** và một số `must_contain` là thuật ngữ tiếng Anh — chỉ model đa ngữ mới cho kết quả retrieval có ý nghĩa.
- Nếu máy nào không cài được: người đó ghi rõ hạn chế trong `REPORT_CANHAN.md` và **cả nhóm phải cùng dùng mock** cho bảng so sánh chung, nếu không bảng đó trộn hai backend và vô nghĩa.
- Cả 5 người **phải cùng một backend**. Đây là biến phải giữ cố định.

## 8. Rủi ro và cách xử lý

| Rủi ro | Dấu hiệu | Xử lý |
|---|---|---|
| VinUni chặn 403 | crawler fail | Đã lường trước: copy-clean thủ công từ trình duyệt. Không né 403. |
| Bản dịch làm sai lệch đáp án | gold answer không khớp văn bản | `must_contain` chọn số/thuật ngữ tiếng Anh giữ nguyên; người thứ hai đối chiếu bản dịch với bản gốc. |
| Corpus lệch giữa 5 repo | số chunk nạp khác nhau giữa các thành viên với cùng chunker | `scripts/check_corpus.py` in **hash của corpus**; 5 người phải cùng hash trước khi chạy bench. |
| #3 và #6 quá giống nhau về nội dung | filter A/B cho kết quả giống hệt | Chọn khía cạnh **khác nhau thật sự** giữa hai văn bản (thang kỷ luật sinh viên vs quy trình xử lý nhân viên). Nếu vẫn giống, ghi nhận và phân tích — đề bài chấp nhận kết quả âm nếu có phân tích. |
| Không kịp tiến độ | quá 2:30 mà `src/` còn đỏ | Ưu tiên `SentenceChunker` (comparator cần) và `compute_similarity` (ngắn); hoãn `RecursiveChunker`. Corpus rút về đúng 5 file, giữ cặp #3/#6. |
| Sát giờ vẫn thiếu tài liệu | | Lấy đủ 5 tài liệu rồi sang Giai đoạn 2 đúng giờ. Rubric chấm chất lượng, không chấm số lượng. |

## 9. Tiêu chí hoàn thành

- [ ] `python -m pytest tests -v` → **42 passed** trong cả 5 repo.
- [ ] `data/k3_university/` có 8 file, `audience` ≥ 2 giá trị, `sources.csv` khớp 1–1, không còn marker `TODO`.
- [ ] `scripts/check_corpus.py` mọi dòng OK và **5 repo cùng corpus hash**.
- [ ] `bench.py` chạy được với cả 5 strategy, in số chunk + top-3 + agent answer cho 5 query, có A/B filter ở Q5.
- [ ] `REPORT_NHOM.md` đủ Data Inventory, Metadata Schema, baseline comparator, 5 strategy, bảng so sánh giữa các thành viên.
- [ ] Mỗi `REPORT_CANHAN.md` có output pytest thật, 5 kết quả retrieval riêng, và ≥1 failure case có bằng chứng từ top-k.
- [ ] Không commit `.venv/`, `.env`, API key, cache dữ liệu.
