# Plan thực hiện — Lab 07 (K3) VinUniversity

Căn cứ: `docs/superpowers/specs/2026-08-03-lab07-k3-vinuni-design.md`
Phân công chi tiết theo người: `PHAN_CONG_NHOM.xlsx`

Mốc thời gian ghi theo **T+** tính từ lúc bắt đầu buổi lab, để nhóm map sang giờ thật.

| Ký hiệu | Thành viên | Strategy |
|---|---|---|
| **TV1** | Nguyễn Minh Hùng | `FixedSizeChunker(500, 50)` |
| **TV2** | Hoàng Anh Quân | `SentenceChunker(3)` |
| **TV3** | Phạm Hải Đăng | `RecursiveChunker(400)` |
| **TV4** | Bùi Gia Huy | `HeadingChunker` |
| **TV5** | Nguyễn Huy Đức | `HeadingRecursiveChunker` (breadcrumb) |

---

## Giai đoạn 0 — Khởi tạo (T+0:00 → T+0:20)

### 0.1 Mỗi người tạo repo riêng

```powershell
# Từ repo nguồn của TV1 (hoặc fork repo gốc của lớp)
git clone <repo-nguon> DAY07-<MSSV>-<HoTen>
cd DAY07-<MSSV>-<HoTen>
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Kiểm tra `.gitignore` đã có `.venv/`, `.env`, `__pycache__/`, `*.xlsx#` trước khi commit lần đầu.

### 0.2 Chạy thử pipeline có sẵn (chưa cần code gì)

```powershell
py ingest.py
```

**Verify:** in ra `ingest self-check OK: parse được N khóa metadata, tạo M chunk...`. Nếu fail thì môi trường sai, dừng lại sửa trước khi làm tiếp.

### 0.3 Đồng bộ artifact dùng chung

TV1 push 3 artifact lên nhánh `main` của repo nguồn; 4 người còn lại copy sang repo mình:

- `data/k3_university/` (toàn bộ)
- `bench_queries.py`
- `report/REPORT_NHOM.md`

**Không ai được sửa 3 thứ này cục bộ.** Muốn đổi thì báo TV1/TV2, sửa ở nguồn, rồi cả 5 sync lại.

---

## Giai đoạn 1 — Corpus (T+0:20 → T+1:20) → **CHECKPOINT 2**

Chủ trì: **TV3 Phạm Hải Đăng (Data curator)**. Cả 5 người cùng dịch để kịp giờ.

### 1.1 Đọc yêu cầu chính thức trước khi lấy dữ liệu

`docs/DATA_COLLECTION.md` (mục 1–6) và `K3_VARIANT.md`. Không bỏ qua bước này — cấu trúc thư mục, tên field, header `sources.csv` đều là yêu cầu chấm điểm.

### 1.2 Thu thập 8 tài liệu

Danh sách URL, phần cần lấy và anchor fact cần xác minh: **`docs/CORPUS_PLAN.md`**.

Quy trình cho mỗi tài liệu:

1. Mở URL bằng trình duyệt, đọc điều khoản trang.
2. Copy **phần nội dung chính**; bỏ menu, breadcrumb, footer, nút chia sẻ, tin liên quan.
3. Dịch sang tiếng Việt theo quy tắc mục 3.3 của spec: **giữ nguyên mọi con số**, thuật ngữ gốc để trong ngoặc ở lần đầu, không thêm thông tin.
4. Dán vào file scaffold tương ứng trong `data/k3_university/`, thay mọi marker `TODO`.
5. Điền `retrieved_at` = ngày thật lấy dữ liệu, `document_version` = mã văn bản (ví dụ `POL-LLR-001-V4.0`) hoặc `not-stated`.
6. Thêm một dòng vào `sources.csv`.

> **Không** chạy `scripts/fetch_public_pages.py` trên vinuni.edu.vn — site trả 403 cho bot. Đã kiểm chứng. Copy thủ công là cách được `docs/DATA_COLLECTION.md` chấp nhận.

**Chia việc dịch (mỗi người ~1.6 file):**

| Người | File |
|---|---|
| TV1 | #1 library-access-services, #8 course-registration-announcement |
| TV2 | #2 academic-regulations-undergrad |
| TV3 | #3 student-code-of-conduct, `sources.csv` |
| TV4 | #6 employees-code-of-conduct (cặp đối chứng — **phải cùng người với #3 đọc lại**) |
| TV5 | #4 financial-regulations-student, #5 scholarship-maintenance, #7 faculty-appointment-promotion |

TV3 và TV4 ngồi cùng nhau khi làm #3/#6: hai văn bản này phải **giữ được điểm khác biệt thật** về xử lý kỷ luật, nếu không Q5 vô nghĩa.

### 1.3 ✅ CHECKPOINT 2

```powershell
py scripts/check_corpus.py
```

**Verify — mọi dòng phải OK:**

- 8 file (nằm trong khoảng 5–10), `doc_id` không trùng, `doc_id` == tên file
- mọi file đủ `doc_id, title, source_url, retrieved_at, document_version, audience`
- `sources.csv` khớp 1–1 với các `.md`
- `audience` có ≥ 2 giá trị khác nhau (kỳ vọng: `student` 6, `staff` 1, `faculty` 1)
- không còn marker `TODO` trong file nào
- in ra **corpus hash** — ghi lại, 5 repo phải giống nhau

Sau khi OK: điền ngay bảng **Data Inventory** và **Metadata Schema** vào `report/REPORT_NHOM.md` mục 1.

> **Nếu chậm tiến độ:** lấy đủ 5 tài liệu (bắt buộc gồm #1, #2, #3, #5, #6 — giữ cặp đối chứng #3/#6) rồi sang Giai đoạn 2 đúng giờ.

---

## Giai đoạn 2 — Warm-up + `src/chunking.py` (T+1:20 → T+2:30) → **CHECKPOINT 3**

**Mỗi người tự làm trong repo của mình.** Đây là 30 điểm cá nhân, không ai code hộ ai.

### 2.1 Warm-up (điền `REPORT_CANHAN.md` TRƯỚC khi code)

Hai câu, trả lời rồi mới kiểm lại bằng code:

1. Cosine similarity cao nghĩa là gì? Cho 1 cặp câu khác từ nhưng cùng nghĩa, 1 cặp ít liên quan, giải thích vì sao cosine hợp với text embedding hơn khoảng cách Euclid.
2. Text 10.000 ký tự, `chunk_size=500`, `overlap=50` → `ceil((10000-50)/(500-50))` = **23 chunk**. Overlap tăng lên 100 thì số chunk tăng hay giảm, đánh đổi là gì?

Tự kiểm hiểu bài: `chunk_size=10, overlap=2` trên `abcdefghijklmnopqrst` → hai chunk đầu phải chia sẻ `ij`. Chưa thấy vì sao thì đọc vòng lặp `start` trong `FixedSizeChunker` (`src/chunking.py:28-35`) trước khi viết tiếp.

### 2.2 TASK 1 — `SentenceChunker.chunk`

Thứ tự: text rỗng → `[]`; `re.split` tại khoảng trắng sau `.`/`!`/`?` (giữ dấu câu ở cuối phần trước); `strip()` từng câu, bỏ rỗng; gộp theo nhóm `max_sentences_per_chunk`, nối bằng một dấu cách; trả `list[str]`.

```powershell
py -m pytest tests/test_solution.py -k SentenceChunker -v
```
**Verify:** 4 test pass.

### 2.3 TASK 2 — `RecursiveChunker.chunk` + `._split`

Tách hai hàm. `chunk()` xử lý text rỗng, gọi `_split(text, self.separators)`, strip/bỏ chunk rỗng. `_split()` là phần đệ quy:

- Base case 1: `len(current_text) <= chunk_size` → `[current_text]`
- Base case 2: hết separator **hoặc** separator là chuỗi rỗng → cắt fixed-size theo `chunk_size`
- Separator hiện tại không xuất hiện → gọi lại với `remaining_separators[1:]`
- Split được → gộp các phần liền nhau đến trước khi vượt `chunk_size`; phần vẫn quá dài **phải đệ quy với separator ưu tiên thấp hơn**

Lỗi thường gặp nhất: gọi lại với **đúng input và đúng separator** → đệ quy vô hạn.

```powershell
py -m pytest tests/test_solution.py -k RecursiveChunker -v
```
**Verify:** 4 test pass, gồm cả `separators=[]`.

### 2.4 TASK 3 — `compute_similarity` + `ChunkingStrategyComparator.compare`

`compute_similarity`: `_dot(a,b) / (sqrt(_dot(a,a)) * sqrt(_dot(b,b)))`, norm = 0 → `return 0.0` **trước khi chia**. Kiểm nhanh: vector giống nhau → 1, vuông góc → 0, ngược hướng → -1.

`compare(text, chunk_size)`: chạy cả 3 chunker, trả dict đúng 3 key `fixed_size`, `by_sentences`, `recursive`; mỗi key có `count`, `avg_length`, `chunks`. Text rỗng **không được chia cho 0**.

```powershell
py -m pytest tests/test_solution.py -k "ComputeSimilarity or CompareChunkingStrategies" -v
```

### 2.5 ✅ CHECKPOINT 3

```powershell
py -m pytest tests -k "Chunker or Similarity or Compare" -v
```
**Verify: 23 passed** (7 test `FixedSizeChunker` có sẵn + 16 test vừa viết).

> **Nếu chậm:** ưu tiên `SentenceChunker` (comparator cần) và `compute_similarity` (ngắn). Hoãn `RecursiveChunker` — `EmbeddingStore` ở bước sau mới là phần nhiều test nhất.

---

## Giai đoạn 3 — `src/store.py` + `src/agent.py` (T+2:30 → T+3:30) → **CHECKPOINT 4**

### 3.1 TASK 4 — `EmbeddingStore` (viết helper trước, method công khai sau)

Thứ tự bắt buộc, làm ngược lại sẽ lặp cùng logic 4 lần:

1. `_make_record(doc)` → dict `{id, content, metadata (bản COPY), embedding}`. `metadata` phải có `doc_id`. `id` ghép `doc.id` với `self._next_index` để không trùng.
2. `_search_records(query, records, top_k)` → embed query **một lần** ngoài vòng lặp, tính `_dot`, tạo result `{id, content, metadata, score}`, sort giảm dần, cắt `top_k`.
3. `add_documents(docs)` → duyệt, `_make_record`, tăng `_next_index`, append `_store`. `docs` rỗng → return bình thường, không lỗi.
4. `get_collection_size()` → `len(self._store)`.

Giữ `self._use_chroma = False`.

### 3.2 TASK 5 — `search_with_filter` + `delete_document`

- `search_with_filter`: **lọc trước, xếp hạng sau**. `metadata_filter=None` → hành vi y hệt `search` cùng `top_k`. Record đi tiếp chỉ khi **mọi** cặp key/value yêu cầu đều khớp. Lọc xong mới đưa vào `_search_records`.
- `delete_document(doc_id)`: xoá mọi record có `metadata['doc_id'] == doc_id`; `True` nếu xoá được ≥1, `False` nếu không khớp.

```powershell
py -m pytest tests -k "EmbeddingStore or SearchWithFilter or DeleteDocument" -v
```
**Verify:** toàn bộ 14 test store pass. Chỉ khi đạt mốc này mới sang phần RAG.

### 3.3 TASK 6 — `KnowledgeBaseAgent`

`__init__` lưu `store`, `llm_fn`. `answer(question, top_k)`:

1. `self.store.search(question, top_k=top_k)`
2. Store rỗng → trả thông báo rõ ràng, **không gọi** `llm_fn`
3. Ghép context, đánh số `[1] [2] [3]` kèm `doc_id` → đây là tiêu chí grounding/traceability
4. Prompt: hướng dẫn *chỉ dùng context, nói rõ khi context không đủ* → context → question → nhãn `Answer:`
5. `return self.llm_fn(prompt)`

### 3.4 ✅ CHECKPOINT 4

```powershell
py -m pytest tests -v
py main.py "Chunking là gì?"
```
**Verify: 42 passed** và `main.py` chạy hết không lỗi. **Dán output pytest vào `REPORT_CANHAN.md` — đó là 30 điểm.**

---

## Giai đoạn 4 — Strategy riêng + benchmark (T+3:30 → T+4:30) → **CHECKPOINT 5**

Hai luồng chạy song song.

### 4.1 Luồng A — TV2 chốt 5 query (`bench_queries.py`)

Với mỗi query điền: `query`, `gold_answer` (trích trực tiếp từ corpus, ghi kèm doc_id + section), `must_contain` (chuỗi đặc trưng, **ưu tiên số hoặc thuật ngữ tiếng Anh giữ nguyên**), `expected_doc_ids`.

**Verify:**
```powershell
py bench_queries.py
```
in ra 5 query, không còn `TODO`, đúng 1 query có `metadata_filter`, mọi `must_contain` không rỗng.

> Chốt xong **không đổi query**, kể cả khi thấy kết quả xấu. Đổi query sau khi xem kết quả là vi phạm quy tắc bài lab.

### 4.2 Luồng B — TV4 & TV5 viết `src/heading_chunker.py`

- **TV4 `HeadingChunker`:** tách trước mỗi dòng heading Markdown (`^#{1,6}\s`), mỗi section là một chunk; section dài hơn `max_chunk_size` thì hạ xuống `RecursiveChunker`.
- **TV5 `HeadingRecursiveChunker`:** như trên, nhưng khi cắt nhỏ một section dài thì **gắn lại breadcrumb tiêu đề** (`H1 > H2`) vào đầu từng mảnh con, để mảnh thứ hai trở đi không mất ngữ cảnh.

**Verify:**
```powershell
py -m src.heading_chunker      # self-check nội bộ
py -m pytest tests -v          # vẫn phải 42 passed, không được đổi
```

### 4.3 Baseline comparator (TV1)

Chạy `ChunkingStrategyComparator().compare()` trên 2–3 tài liệu, điền bảng baseline vào `REPORT_NHOM.md` mục 2.

> **Bỏ front matter trước khi so sánh**, nếu không là đang đo cả khối YAML. Dùng `ingest.parse_front_matter(text)[1]` để lấy phần body.

### 4.4 Mỗi người chạy `bench.py` với strategy của mình

```powershell
$env:EMBEDDING_PROVIDER="local"    # cả 5 người phải giống nhau
py bench.py --strategy fixed              # TV1
py bench.py --strategy sentence           # TV2
py bench.py --strategy recursive          # TV3
py bench.py --strategy heading            # TV4
py bench.py --strategy heading_recursive  # TV5
```

Chỉ **dòng chọn chunker** khác nhau. Corpus, query, embedder, `top_k` giữ nguyên.

### 4.5 ✅ CHECKPOINT 5

**Verify:** `bench.py` in được số chunk đã nạp và top-3 cho cả 5 query; nhóm có đủ 5 query + gold answer đã chốt; mỗi người đã đổi sang strategy riêng. Chưa xét kết quả tốt/xấu.

---

## Giai đoạn 5 — Phân tích & failure case (T+4:30 → T+5:30) → **CHECKPOINT 6**

### 5.1 A/B metadata filter (Q5)

`bench.py` tự chạy Q5 hai lần và in hai bảng top-3 cạnh nhau. Mỗi người ghi vào `REPORT_CANHAN.md`: filter đã loại doc nào, thứ hạng thay đổi ra sao, agent trả lời khác đi không.

> Nếu hai kết quả **giống hệt nhau**: ghi nhận đúng như vậy và phân tích tại sao — có thể corpus chưa đủ nhiễu, hoặc query đã đủ đặc thù để không cần filter. Kết quả âm có phân tích vẫn được điểm; bịa ra khác biệt thì không.

### 5.2 Ghi nhận theo 5 câu hỏi phân tích

Với **mỗi query**, ghi tối thiểu: top-3 chunk (score, `doc_id`, `chunk_index`, preview), có/không liên quan, câu trả lời agent, và lý do.

| Câu hỏi phân tích | Dấu hiệu cần ghi |
|---|---|
| Precision | Top-3 có chunk chứa đáp án không? |
| Chunk coherence | Chunk có giữ điều kiện và ngoại lệ trong cùng ngữ cảnh không? |
| Metadata utility | Filter giảm nhiễu hay loại nhầm đáp án? |
| Grounding | Câu trả lời có dựa trên context đã retrieve không? |
| Failure case | Query nào sai rõ ràng, vì sao, sửa gì? |

### 5.3 So sánh mức doc vs mức chunk

`bench.py` in **cả hai** cột điểm: "doc gold có trong top-3?" và "`must_contain` có trong top-3?". Chênh lệch giữa hai cột này thường là phát hiện đáng giá nhất của buổi lab — đặc biệt ở TV4/TV5, vì các section cùng văn bản có score sát nhau nên section nào lọt top-3 gần như ngẫu nhiên.

### 5.4 Failure case (mỗi người ≥ 1)

Phải nêu đủ 4 phần: **query → bằng chứng từ top-k → nguyên nhân → thay đổi đề xuất**. Không viết "model sai". Vài hướng hay gặp:

- Chunk đúng chủ đề nhưng không chứa số liệu lại thắng chunk có đáp án (cosine đo độ giống chủ đề, không đo mật độ thông tin trả lời được).
- Top-3 đúng tài liệu nhưng sai section (chunk không overlap → mỗi thông tin chỉ có một cơ hội lọt top-k).
- Filter loại nhầm tài liệu chứa thông tin cần (đánh đổi precision lấy recall).

### 5.5 ✅ CHECKPOINT 6

**Verify:** nhóm có **một bảng so sánh chung** giữa 5 thành viên trong `REPORT_NHOM.md`; mỗi người có kết quả benchmark riêng, nhận xét riêng, và ≥1 failure case có bằng chứng từ top-k.

---

## Giai đoạn 6 — Report, demo, nộp (T+5:30 → T+6:00) → **CHECKPOINT 7**

### 6.1 Hoàn thiện hai report

| File | Ai | Nội dung |
|---|---|---|
| `report/REPORT_NHOM.md` | 1 bản/nhóm, TV5 chủ trì gom | corpus + metadata schema, baseline, 5 strategy, 5 query + gold, bảng so sánh, demo |
| `report/REPORT_CANHAN.md` | mỗi người 1 bản | warm-up, hướng tiếp cận code, **output pytest thật**, dự đoán similarity, 5 kết quả retrieval riêng, failure case |

### 6.2 Demo 6–8 phút (TV5 điều phối)

1. Phạm vi, nguồn, metadata schema — 1 phút
2. Mỗi thành viên giải thích strategy của mình — 2 phút
3. So sánh kết quả, gồm A/B metadata filter và một failure case — 3 phút
4. Chạy một query live hoặc trình bày output đã chuẩn bị — 1–2 phút

Mở sẵn terminal đã `bench.py` chạy được. Chuẩn bị trả lời: strategy nào tái dùng được khi đổi domain, filter giảm nhiễu ở đâu, đánh đổi recall thế nào.

### 6.3 Nộp bài

```powershell
py -m pytest tests -v   # phải 42 passed
git status              # không được thấy .venv/ hay .env

git add .
git commit -m "Nộp bài Lab 07"
git branch -M main
git remote add origin https://github.com/<tai-khoan>/DAY07-<MSSV>-<HoVaTen>.git
git push -u origin main
```

Nộp **link repo GitHub** trên vlearn, không nộp zip. Tên repo `DAY07-MSSV-HoVaTen`, họ tên viết liền không dấu.

### 6.4 ✅ CHECKPOINT 7 — checklist cuối

- [ ] `py -m pytest tests -v` pass toàn bộ 42 test
- [ ] `src/` giữ nguyên public interface của starter code, không còn `NotImplementedError`
- [ ] Corpus 8 tài liệu chỉ từ nguồn công khai; đủ `source_url`, `retrieved_at`, `document_version`; không có dữ liệu cá nhân
- [ ] `sources.csv` khớp 1–1 với corpus
- [ ] Đúng 5 query + gold answer, có 1 query dùng `metadata_filter={"audience": "student"}`
- [ ] TV4 và TV5 đã chunk theo heading/section
- [ ] Hai report điền đủ, có output thật và ≥1 failure case có bằng chứng từ top-k
- [ ] 5 người chung corpus và query (cùng corpus hash), nhưng strategy, kết quả và phản ánh **không trùng nhau**
- [ ] Không commit `.env`, API key, `.venv/`, database local
- [ ] Đã nộp link repo vào vlearn

---

## Đường găng (critical path)

```
Corpus (CP2) ──▶ bench_queries (4.1) ──▶ bench.py (4.4) ──▶ phân tích (CP6) ──▶ report
     │                                        ▲
     └─ song song ─▶ src/ (CP3, CP4) ─────────┘
```

Corpus và `src/` chạy song song được. Nhưng **không ai chạy được `bench.py` nếu `src/store.py` còn đỏ** — vì vậy CP4 là mốc cứng: quá **T+3:30** mà `src/` chưa xanh thì người đó phải bỏ dở việc dịch tài liệu để tập trung code, và nhờ người đã xong gánh phần dịch.
