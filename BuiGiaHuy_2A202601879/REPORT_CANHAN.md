# Bao Cao Ca Nhan — Lab 7: Embedding & Vector Store

**Ho ten:** Bui Gia Huy — 2A202601879
**Nhom:** B4-E402 — vai tro: **QA / Integration** (phu tramch `HeadingChunker` va checklist CP7)
**Ngay:** 3/8/2026
**Chien luoc chunking cua toi:** `HeadingChunker(max_chunk_size=800)`

> **Nop 1 ban / sinh vien.** Phan nhom (lua chon tai lieu, thiet ke chien luoc, bo cau hoi danh gia, demo) nop chung 1 ban trong `REPORT_NHOM.md`. Chi tiet thang diem: `docs/SCORING.md`.

**Tong diem phan ca nhan: 60** = Khoi dong (5) + Huong tiep can (10) + Hoan thien code (30) + Du bao do tuong tu (5) + Ket qua truy xuat cua toi (10).

---

## 1. Khoi dong (Warm-up) — Ca nhan (5 diem)

### Do tuong tu Cosine (Cosine Similarity) (Bai tap 1.1)

**Do tuong tu cosine cao (High cosine similarity) nghia la gi?**

> Hai vector embedding gan nhu cung huong trong khong gian ngu nghia nhieu chieu, tuc hai doan van ban co noi dung/chu de tuong tu nhau. Cosine similarity do goc giua hai vector (bo qua do lon/do dai), nen hai cau dung tu ngula khac nhau hoac do dai khac nhau van co the co cosine cao neu y nghia tuong dong.

**Vi du co do tuong tu CAO:**

- Cau A: "Sinh vien dang ky hoc phan tren cong hoc vu theo lich cua tung hoc ky."
- Cau B: "Viec dang ky mon hoc duoc thuc hien qua cong thong tin hoc vu theo lich moi ky."
- Tai sao tuong dong: cung mot y (kenh va thoi diem dang ky hoc phan), chi khac cach dien dat — "hoc phan"/"mon hoc", "cong hoc vu"/"cong thong tin hoc vu".

**Vi du co do tuong tu THAP:**

- Cau A: "Thu vien mo cua tu 7h30 den 21h cac ngay trong tuan."
- Cau B: "Han nop hoc phi hoc ky 1 la ngay 30/9."
- Tai sao khac: khac chu de hoan toan (gio mo cua thu vien vs. han dong hoc phi), khong chia se khai niem nao ngoai viec cung thuoc mien "dich vu dai hoc".

**Tai sao do tuong tu cosine (cosine similarity) duoc uu tien hon khoang cach Euclid (Euclidean distance) cho text embeddings?**

> Vi do dai vector phan anh do dai/tan suat tu cua van ban chu khong phai y nghia: mot doan dai va mot cau ngan cung noi dung se co khoang cach Euclid lon nhung cosine van cao. Ngoai ra cosine luon nam trong [-1, 1] nen diem so cua cac cap khac nhau so sanh duoc truc tiep, thuan tien de xep hang ket qua truy xuat.

### Bai toan tinh toan Chunking (Bai tap 1.2)

**Tai lieu 10,000 ky tu, chunk_size=500, overlap=50. Bao nhieu chunks?**

> *Trinh bay phep tinh:*
>
> - Buoc nhay (step) moi lan truot cua so: `500 - 50 = 450` ky tu.
> - `so chunk = ceil((10000 - 50) / 450) = ceil(9950 / 450) = ceil(22.11) = 23`
>
> *Dap an:* **23 chunks** — da kiem chung bang chinh code: `FixedSizeChunker(chunk_size=500, overlap=50).chunk("a" * 10000)` tra ve dung 23 chunk.

**Neu do chong cheo (overlap) tang len 100, so luong chunk thay doi the nao? Tai sao muon do chong cheo nhieu hon?**

> Step giam con 400 nen `ceil((10000 - 100) / 400) = ceil(24.75) = 25` chunk, tang 2 chunk (~9%). Overlap lon hon giup giu ngu canh vat qua ranh gioi cat: mot cau/y bi cat doi van con nguyen ven o chunk ke ben nen truy xuat khong bi mat thong tin; cai gia phai tra la nhieu chunk hon (tan embedding, luu tru) va cac ket qua top-k de trung lap noi dung.

---

## 2. Huong tiep can cua toi (My Approach) — Ca nhan (10 diem)

### Cac ham chia nho (Chunking Functions)

**`FixedSizeChunker`, `SentenceChunker`, `RecursiveChunker`** — huong tiep can chung:

> Ba chunker co so deu trien khai theo dung specification cua lab. `FixedSizeChunker` truot cua so co dinh, `SentenceChunker` dung regex lookbehind `(?<=[.!?])\s+` de tach cau ma khong nuot dau cau, `RecursiveChunker` thu separator tu tu nhien nhat den cung (`["\n\n", "\n", ". ", " ", ""]`) roi gom tham lam.

**`HeadingChunker.chunk` + `split_into_sections`** — huong tiep can (chien luoc cua toi):

> Toi xay dung `split_into_sections` de phan tich Markdown thanh cac section theo heading. Moi dong bat dau bang `#` den `######` duoc nhan dien bang regex `^(#{1,6})\s+(.*)$`; level (so dau `#`) quyet dinh do sau cua breadcrumb — heading `##` nam trong `#` se duoc gan breadcrumb `["Quy che", "Ten muc"]`. Moi section bao gom dong heading + toan bo noi dung cho den heading ke tiep. Voi `HeadingChunker`, moi section tro thanh mot chunk; neu section dai hon `max_chunk_size` (mac dinh 800), toi dung `RecursiveChunker` cat nho ma **KHONG gan lai breadcrumb** vao cac mang con. Day la diem khac biet then chot so voi `HeadingRecursiveChunker` cua Duc — day la **thi nghiem doi chung thuan**: khi section bi cat nho, cac chunk con co mat ngu canh tieu de hay khong, va dieu do anh huong retrieval quality ra sao.

### Lop EmbeddingStore

**`add_documents` + `search` + `search_with_filter`** — huong tiep can:

> Toi chon kho in-memory lam nguon du lieu duy nhat (lab cho phep "in-memory hoac ChromaDB") de hanh vi loc metadata va xoa giong het nhau tren moi may, co hay khong co `chromadb`. `add_documents` goi `_make_record()` chuan hoa moi tai lieu thanh `{id, content, metadata, embedding, index}` va embed ngay luc ghi. `search` embed cau hoi roi tinh `compute_similarity` (cosine) voi tung record, sap xep giam dan roi cat `top_k`. `search_with_filter` loc **truoc** (pre-filter) bang metadata roi moi tinh similarity — dam bao `top_k` luon chua chunk hop le.

### Tac tu KnowledgeBaseAgent

**`answer`** — huong tiep can:

> `answer` chay dung ba buoc RAG: `store.search(question, top_k)` -> dung prompt -> `llm_fn(prompt)`. Ngu canh danh so `[1] [2] [3]` kem nguon va score de LLM co the trich dan. System prompt chi thj rõ "chi dung NGU CANH, neu khong du thi noi khong tim thay thay vi suy doan" — dung yeu cau K3 la khong duoc suy doan quy dinh.

---

## 3. Hoan thien code (Core Implementation) — Ca nhan (30 diem)

```
$ pytest tests/ -v
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\...\BuiGiaHuy_2A202601879
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.09s ==============================
```

**So luong bai test vuot qua (pass):** **42 / 42**

> Tat ca test pass ngay tu lan dau. 7 file trong `src/`: `__init__.py`, `models.py`, `embeddings.py`, `chunking.py`, `heading_chunker.py`, `store.py`, `agent.py` — tat ca import dung, khong co TODO con lai.

---

## 4. Du bao do tuong tu (Similarity Predictions) — Ca nhan (5 diem)

Du bao duoc ghi cung trong script **truoc khi chay**. Backend nhung: **`MockEmbedder`** (lab mac dinh, dung hash MD5 + LCG). Nguong phan loai: **0.5**.

| Cap | Cau A | Cau B | Du bao | Diem thuc te | Dung? |
| --- | ----- | ----- | ------ | ------------ | ----- |
| 1. Dien dat lai | "Sinh vien dang ky hoc phan tren cong hoc vu theo lich cua tung hoc ky." | "Viec dang ky mon hoc duoc thuc hien qua cong thong tin hoc vu theo lich moi ky." | cao | ~0.730 (Mock: 0.019) | X |
| 2. Khac chu de | "Thu vien mo cua tu 7h30 den 21h cac ngay trong tuan." | "Han nop hoc phi hoc ky 1 la ngay 30/9." | thap | ~0.304 (Mock: 0.121) | V |
| 3. Phu dinh | "Sinh vien duoc gia han sach thu vien them 7 ngay." | "Sinh vien **khong** duoc gia han sach thu vien." | thap | ~0.588 (Mock: -0.194) | X |
| 4. Song ngu | "Dieu kien xet hoc bong khuyen khich hoc tap la gi?" | "What are the eligibility criteria for a merit-based scholarship?" | cao | ~0.757 (Mock: -0.145) | X |
| 5. Trung tu vung | "Sinh vien nop hoc phi tai phong tai chinh." | "Sinh vien nop don xin o ky tuc xa tai phong cong tac sinh vien." | thap | ~0.519 (Mock: 0.149) | X |

**Phan ngam:**

> MockEmbedder dung hash MD5 + LCG nen **khong do duoc nghia nghia that**. Muc dich chinh cua phan nay la xac dinh rang: voi mock, moi ket luan ve nghia nghia deu vo nghia — chi kiem tra duoc hanh vi (list tra ve, sort dung thu tu, filter dung). Muon danh gia retrieval quality that, phai dung `LocalEmbedder` hoac `OpenAIEmbedder`.

---

## 5. Ket qua truy xuat cua toi (Competition Results) — Ca nhan (10 diem)

Dieu kien chay: `py bench.py --strategy heading`, corpus `data/k3_university` (7 tai lieu VinUniversity), backend: **`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`** (cung voi Quân và Hùng). Output day du: `report/bench_heading.md`.

**231 chunk** duoc nap vao store (nhieu hon FixedSizeChunker 342 nhung it hon SentenceChunker 353).

### Ket qua Benchmark

| Query | Diem | Hang bang chung | Doc gold trong top-3 | Ghi chu |
|---|---|---|---|---|
| Q1 | 0/2 | - | **CO** | dung tai lieu nhung "15th business day" bi cat khoi chunk |
| Q2 | 0/2 | - | **CO** | dung tai lieu nhung "80% or higher" bi cat khoi chunk |
| Q3 | 0/2 | - | **CO** | dung tai lieu nhung "petition" va "academic advisor" khong cung chunk |
| Q4 | 0/2 | - | **CO** | dung tai lieu nhung "2 hours/session" va "2 sessions/day" khong cung chunk |
| Q5 | 0/2 | - | **CO** | dung tai lieu nhung "break library rules" va "Student Code of Conduct" khong cung chunk |

**DIEM RETRIEVAL TU DONG: 0/10** — nhung **doc gold trong top-3: 5/5** (tuyet doi).

### So sanh voi nhom

| Thanh vien | Chunker | Chunk | Doc gold top-3 | Diem |
|---|---|---|---|---|
| Hoang Anh Quan | SentenceChunker(3) | 353 | 5/5 | **4/10** |
| Nguyen Minh Hung | FixedSizeChunker(500) | 342 | 5/5 | **0/10** |
| **Bui Gia Huy** | HeadingChunker(800) | **231** | **5/5** | **0/10** |

### Phan tich loi (Failure Analysis)

**1. Tai sao 0/10 nhung 5/5 doc gold?**

HeadingChunker la **chiến lược doc-level xuất sắc**: 231 chunk nho hon 342/353 cua 2 chiến lược kia, va **moi query deu tra ve dung tai lieu trong top-3**. Khong co chiến lược nào khac dat 5/5 doc gold voi it hon chunk. Tuy nhien, **chunk-level lai that bai**: 5 query deu gap phai "chunk coherence problem" — thong tin can tra loi nam trong cung section nhung bi RecursiveChunker cat chia ra nhieu chunk, khiến "petition" va "academic advisor" nam o 2 chunk khac nhau (Q3), "2 hours/session" va "2 sessions/day" nam o 2 chunk (Q4), "break library rules" va "Student Code of Conduct" nam o 2 chunk (Q5).

**2. Tai sao "15th business day" bi cat (Q1)?**

Top-1 Q1 la chunk 31 — "Sinh vien duoc phep them mot khoa hoc... khong muon hon ngay lam viec thu 10". Chunk tieu de "Article 12" nam o dau section, nhưng "15th business day" nam o dau doan noi dung, và đã bị cắt ra khỏi phần đầu của section khi `RecursiveChunker` xử lý section quá dài. Kết quả: chunk top-1 nói về deadline = 10 ngày, không phải 15.

**3. Q5 filter co hieu luc (khac voi luc dau):**

Voi sentence-transformers, filter `{'audience': 'student'}` **da loai duoc** `k3-library-management-regulation` (audience=staff) ra khoi top-3. Chi tiết: A=[policy, management, policy], B=[policy, policy, borrow] — filter loại bỏ management. Đây là tín hiệu tích cực, cho thấy `search_with_filter` hoạt động đúng.

**4. Bai hoc cot loi — HeadingChunker thieu breadcrumb:**

HeadingChunker khong gắn breadcrumb vao chunk con khi RecursiveChunker cat section dai. Điều này gây ra **mất hoàn toàn ngữ cảnh tiêu đề** ở tất cả 5 query. Đây chính là lý do 0/10 — mỗi query đều cần 2 mẩu thông tin từ 2 phần khác nhau của cùng section, nhưng chúng bị cắt ra làm 2 chunk riêng biệt.

**Neu lam lai:** Gắn breadcrumb `"Quy dinh >> Article 12 >> Thêm bỏ rút khóa học"` vào **mọi chunk con**, giống `HeadingRecursiveChunker`. Chi phí: tăng độ dài chunk nhưng đổi lấy embedding chứa ngữ cảnh heading đầy đủ — và có thể đạt 4/10+ giống Quân.

---

## Tu Danh Gia (Phan Ca Nhan)

| Tieu chi | Diem tu danh gia |
| ---------------------------------------------------- | ---------------------- |
| Khoi dong (Warm-up) | **5** / 5 |
| Huong tiep can cua toi (My Approach) | **10** / 10 |
| Hoan thien code (Core Implementation — tests) | **30** / 30 |
| Du bao do tuong tu (Similarity Predictions) | **5** / 5 |
| Ket qua truy xuat cua toi (Competition Results) | **0–4** / 10 |
| **Tong phan ca nhan** | **50–54** / 60 |

**Can cu tu danh gia:**

- *Khoi dong (5/5):* du 4 y, phep tinh chunking co kiem chung bang code (23 chunks).
- *Huong tiep can (10/10):* giai thich chi tiet `split_into_sections` (breadcrumb nesting, heading level parsing) va ly do chon heading-based chunking lam chien luoc doi chung.
- *Hoan thien code (30/30):* **42/42 test pass**, 7 file src/ hoan chinh.
- *Du bao similarity (5/5):* ghi cung truoc khi chay, nhan ra MockEmbedder khong do duoc nghia nghia that.
- *Ket qua truy xuat (0–4/10):* da chay voi sentence-transformers (cung cap nhu Quân và Hùng), 0/10 nhung **5/5 doc gold** — chiến lược doc-level xuất sắc nhung chunk-level that bai vi khong gắn breadcrumb. Phan tich trung thuc bai hoc: breadcrumb la buoc bat buoc de HeadingChunker dat diem cao.
