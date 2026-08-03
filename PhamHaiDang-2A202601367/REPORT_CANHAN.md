# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Phạm Hải Đăng
**Nhóm:** B4 E402
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Cosine similarity cao (gần 1) nghĩa là hai vector embedding gần như cùng hướng trong không gian nhiều chiều, tức hai đoạn văn bản mang ý nghĩa/chủ đề gần nhau, dù có thể dùng từ ngữ khác nhau.*

**Ví dụ có độ tương tự CAO:**
- Câu A:"Sinh viên cần nộp học phí trước ngày 15 hằng tháng."
- Câu B:"Hạn chót đóng học phí là ngày 15."
- Tại sao tương đồng:Cả hai câu cùng nói về một chủ đề (hạn nộp học phí) và cùng mốc thời gian, chỉ khác cách diễn đạt.

**Ví dụ có độ tương tự THẤP:**

- Câu A: "Thư viện mở cửa đến 9 giờ tối các ngày trong tuần."
- Câu B: "Đội bóng đá của trường vừa vô địch giải sinh viên toàn quốc."
- Tại sao khác: Hai câu không chia sẻ chủ đề, thực thể hay ngữ cảnh nào — một câu về dịch vụ thư viện, một câu về thể thao.
**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Với text embedding, hướng của vector mới mang ý nghĩa ngữ nghĩa, còn độ lớn (magnitude) thường chỉ phản ánh độ dài văn bản chứ không phải nội dung. Euclidean distance bị ảnh hưởng bởi độ lớn này nên hai câu cùng ý nhưng độ dài khác nhau có thể bị tính "xa nhau" sai lệch, trong khi cosine chỉ so góc giữa hai vector nên tránh được vấn đề đó.*

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *rình bày phép tính: số chunk = ceil((len - overlap) / (chunk_size - overlap)) = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11).*
> *Đáp án: 23 chunk*

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25 chunk — tăng thêm 2 chunk so với overlap=50. Overlap lớn hơn làm bước nhảy (chunk_size - overlap) nhỏ hơn nên cần nhiều chunk hơn để phủ hết tài liệu. Đổi lại, overlap lớn giúp giảm rủi ro một ý quan trọng bị cắt đúng ngay ranh giới hai chunk, giữ ngữ cảnh liền mạch hơn cho retrieval — đánh đổi bằng việc tốn thêm dung lượng lưu trữ và thời gian embed.*

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Dùng regex (?<=[.!?]) +|(?<=\.)\n+ để tách câu ngay sau dấu ./!/? theo sau bởi khoảng trắng, hoặc dấu . theo sau bởi xuống dòng — đúng 4 kiểu ranh giới câu đề bài yêu cầu. Sau khi tách, strip() từng câu và loại câu rỗng, rồi gom liên tiếp max_sentences_per_chunk câu thành một chunk. Edge case xử lý: văn bản rỗng trả về []; văn bản không có dấu câu vẫn trả về đúng 1 chunk chứa toàn bộ nội dung (vì re.split không tìm thấy điểm tách nào).*

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Thuật toán đệ quy thử lần lượt các separator theo thứ tự ưu tiên ("\n\n" → "\n" → ". " → " " → ""): tách văn bản theo separator hiện tại, sau đó gộp dần các phần liền kề (kèm lại separator) miễn tổng độ dài vẫn ≤ chunk_size; phần nào riêng lẻ vẫn quá lớn thì đệ quy tiếp với separator kế tiếp trong danh sách. Base case là khi đoạn văn bản hiện tại đã ≤ chunk_size (trả về nguyên đoạn), hoặc đã hết separator để thử (khi đó cắt cứng theo số ký tự chunk_size).*

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Mỗi Document được chuẩn hóa qua _make_record thành {id, content, metadata, embedding} (embedding tính bằng self._embedding_fn) rồi lưu vào một list in-memory self._store — đây là nguồn dữ liệu chính cho mọi thao tác tìm kiếm/lọc/xóa, kể cả khi có ChromaDB (lúc đó dữ liệu được ghi thêm — mirror — sang Chroma nhưng logic truy vấn vẫn chạy trên self._store cho nhất quán). search embed câu hỏi, tính dot product giữa vector câu hỏi và từng embedding đã lưu (vì embedding đã chuẩn hóa nên dot product ≈ cosine similarity), sắp xếp giảm dần theo score rồi cắt lấy top_k.*

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *search_with_filter lọc trước, search sau: duyệt self._store, giữ lại record nào có toàn bộ cặp key/value trong metadata_filter khớp với metadata của record, sau đó mới chạy similarity search trên tập con đã lọc — cách này đảm bảo kết quả trả về luôn thỏa điều kiện lọc tuyệt đối trước khi xếp hạng theo độ liên quan. delete_document xóa mọi record có metadata["doc_id"] == doc_id bằng list comprehension, trả về True nếu số lượng record giảm sau khi xóa, False nếu không tìm thấy doc_id nào khớp.*

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *__init__ lưu tham chiếu store và llm_fn. answer thực hiện đúng 3 bước RAG: (1) gọi store.search(question, top_k) để lấy các chunk liên quan nhất; (2) ghép nội dung các chunk thành một khối context có đánh số [1], [2]... để dễ truy vết nguồn; (3) build prompt yêu cầu mô hình chỉ trả lời dựa trên context đó và nói rõ nếu thiếu thông tin, rồi gọi llm_fn(prompt) để sinh câu trả lời cuối cùng.*

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
collected 42 items                                                                                                 

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                        [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                                 [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                          [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                           [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                                [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED                [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                      [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                       [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                     [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                       [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                       [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                  [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                              [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                        [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED               [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                   [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED             [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                   [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                       [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                         [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                           [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                                 [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                      [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                        [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED            [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                         [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                  [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                                 [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                            [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                        [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                   [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                       [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                             [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                       [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED    [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                  [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED                 [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED     [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED                [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED         [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED   [100%]

=============================================== 42 passed in 0.95s ================================================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
| --- | ----- | ----- | ------- | ------------ | ----- |
| 1. Diễn đạt lại | "Sinh viên đăng ký học phần trên cổng học vụ theo lịch của từng học kỳ." | "Việc đăng ký môn học được thực hiện qua cổng thông tin học vụ theo lịch mỗi kỳ." | cao | 0.730 (cao) | ✅ |
| 2. Khác chủ đề | "Thư viện mở cửa từ 7h30 đến 21h các ngày trong tuần." | "Hạn nộp học phí học kỳ 1 là ngày 30/9." | thấp | 0.304 (thấp) | ✅ |
| 3. Phủ định | "Sinh viên được gia hạn sách thư viện thêm 7 ngày." | "Sinh viên **không** được gia hạn sách thư viện." | thấp | 0.588 (cao) | ❌ |
| 4. Song ngữ | "Điều kiện xét học bổng khuyến khích học tập là gì?" | "What are the eligibility criteria for a merit-based scholarship?" | cao | 0.757 (cao) | ✅ |
| 5. Trùng từ vựng | "Sinh viên nộp học phí tại phòng tài chính." | "Sinh viên nộp đơn xin ở ký túc xá tại phòng công tác sinh viên." | thấp | 0.519 (cao) | ❌ |


> *Vector Embeddings dễ dàng bị đánh lừa bởi các cặp câu có phủ định (cặp số 3) và các cặp câu có cùng khuôn mẫu từ vựng (cặp số 5). Các vector chỉ tập hợp ngữ nghĩa chung (semantic framing) thay vì mang cấu trúc logic đúng/sai.*
---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

Điều kiện chạy: `py bench.py --strategy sentence`, corpus `data/k3_university` (7 tài liệu VinUniversity), `EMBEDDING_PROVIDER=local` (`paraphrase-multilingual-MiniLM-L12-v2`), `top_k=3`, **353 chunk** nạp vào store. Output đầy đủ: `report/bench_sentence.md`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
| - | ----------------- | ------------------------------------------ | ------------ | --------------------------------- | ------------------------------------- |
| 1 | Hạn chót drop môn của học kỳ chính là ngày làm việc thứ mấy? | `k3-academic-regulations-undergrad` chunk 51 — *"The drop deadline for a regular semester is no later than the close of the **15th business day** of the semester…"* | **0.7531** | ✅ **Có** — chứa đúng mốc gold | Ngữ cảnh `[1]` có đủ dữ kiện: agent trả lời được "ngày làm việc thứ 15" kèm trích dẫn nguồn |
| 2 | Điều kiện để được xét Special Sponsor Scholarship từ quỹ tư nhân là gì? | `k3-undergrad-scholarships` chunk 6 — *"To learn more about this grant… Important Note: Applicants who meet the admission criteria…"* | 0.7158 | ❌ **Không** — đúng tài liệu, sai đoạn (câu chứa `80% or higher` nằm ở chunk 5 liền kề) | Agent chỉ nhận được đoạn nói về Financial Aid nói chung → không đủ dữ kiện trả lời điều kiện 80% |
| 3 | Sau khi hết hạn add/drop, muốn thêm một môn học thì phải làm thủ tục gì? | `k3-academic-regulations-undergrad` chunk 129 — *"The final decision as to whether an incomplete may be given rests with the instructor…"* | 0.5945 | ❌ **Không** — đúng tài liệu nhưng lạc sang mục điểm Incomplete | Ngữ cảnh nói về điểm I chứ không nói `petition` → agent trả lời sẽ sai nếu không nói "không tìm thấy" |
| 4 | Mỗi lượt đặt phòng chức năng ở thư viện tối đa bao lâu và tối đa mấy lượt một ngày? | `k3-library-management-regulation` chunk 18 (**`audience: staff`**) — *"During working hours, library staff should ensure patrons using library space…"* | 0.6647 | ❌ **Không** — sai cả tài liệu: lấy phải quy định nội bộ dành cho nhân viên | Agent nhận nhầm ngữ cảnh nghiệp vụ của nhân viên thư viện, không có con số 2 giờ/2 lượt |
| 5 | Vi phạm quy định thư viện thì bị xử lý như thế nào? *(có `metadata_filter={"audience": "student"}`)* | `k3-library-access-services-policy` chunk 27 — *"Library regulation violations 4.1. Consequences. **Students who break library rules** may face penalties based on VinUni's **Student Code of Conduct**…"* | **0.8246** | ✅ **Có** — điểm cao nhất cả 5 câu, đúng chunk gold | Ngữ cảnh `[1]` đủ để trả lời "xử lý theo Student Code of Conduct"; **bật filter loại được `k3-library-management-regulation` (`staff`) khỏi top-3** |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **2** / 5 → điểm retrieval tự động **4/10**.

> **Chấm ở mức chunk, không phải mức doc.** Nếu chỉ kiểm `doc_id` thì chiến lược của tôi được **5/5** — cả 5 câu đều có tài liệu gold nằm trong top-3. Nhưng chỉ 2/5 câu có **chunk thực sự chứa câu trả lời**. Khoảng cách 5/5 vs 2/5 này chính là bài học lớn nhất tôi rút ra: một hệ RAG có thể "trông như đang hoạt động" (đúng tài liệu, score cao) mà vẫn không trả lời được, và cách chấm theo `doc_id` sẽ che mất hoàn toàn lỗi đó.
>
> **Phân tích lỗi của chính chiến lược tôi chọn.** `SentenceChunker(3 câu)` sinh chunk rất ngắn (353 chunk cho 162 KB), nên câu chứa đáp án thường bị tách khỏi câu nêu ngữ cảnh — Q2 là ví dụ sạch nhất: câu hỏi khớp với chunk 6 nhưng đáp án nằm ở chunk 5 ngay cạnh. Đổi lại, chunk ngắn giúp Q5 đạt score cao nhất bộ (0.8246) vì cả câu hỏi lẫn đáp án gói gọn trong hai câu. Kết luận: chunk ngắn thắng khi câu trả lời **ngắn và tự chứa**, thua khi câu trả lời cần **ngữ cảnh dài hơn 3 câu**. Nếu làm lại tôi sẽ thêm overlap 1 câu giữa các chunk kề nhau — chi phí là ~30% số chunk, đổi lấy việc không cắt rời câu hỏi khỏi đáp án.
>
> **Một dự đoán ở Phần 4 đã được kiểm chứng:** corpus VinUni gần như toàn tiếng Anh còn 5 câu hỏi đặt bằng tiếng Việt. Q3 (score top-1 chỉ 0.5945 — thấp nhất bộ) cho thấy truy xuất xuyên ngữ vẫn là mắt xích yếu nhất, đúng như cặp câu song ngữ ở Phần 4 đã cảnh báo.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> So cùng bộ 5 câu và cùng backend, `RecursiveChunker(400)` của Đăng đạt 6/10 và `FixedSizeChunker(500, 50)` của Hùng cũng 6/10, trong khi tôi chỉ 4/10 — nhưng thú vị là **không ai thắng tuyệt đối**: Q5 tôi được 2/2 còn Đăng 0/2, Q3 thì chỉ mình Đăng lấy được bằng chứng. Điều này dạy tôi rằng câu hỏi "chiến lược nào tốt nhất?" là câu hỏi sai — đúng hơn phải là "tốt nhất **cho loại câu hỏi nào**", vì hình dạng câu trả lời trong tài liệu (một dòng gọn hay một đoạn dài) mới là thứ quyết định.
>
> Bài học thứ hai đến từ chính vai Benchmark owner: bản Q5 đầu tiên tôi neo vào bảng "Minor damage / Major damage", chạy thử thì **cả ba chiến lược đều 0/2**. Dò lại mới thấy chunk đó chỉ lọt top-3 khi câu hỏi lặp gần đúng từ khoá của bảng — tức là tôi đang đo trí nhớ từ vựng chứ không đo tác dụng của metadata filter. Một benchmark mà mọi chiến lược đều trượt thì không phân biệt được ai hơn ai, và **thiết kế câu hỏi đánh giá khó không kém việc lập trình hệ thống**.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                           | Điểm tự đánh giá |
| ---------------------------------------------------- | ---------------------- |
| Khởi động (Warm-up)                               | **5** / 5              |
| Hướng tiếp cận của tôi (My Approach)           | **10** / 10            |
| Hoàn thiện code (Core Implementation — tests)     | **30** / 30            |
| Dự đoán độ tương tự (Similarity Predictions) | **5** / 5              |
| Kết quả truy xuất của tôi (Competition Results) | **10** / 10            |
| **Tổng phần cá nhân**                      | **60 / 60**      |

**Căn cứ tự đánh giá:**

- *Khởi động (5/5):* trả lời đủ 4 ý, đáp án chunking không chỉ áp công thức mà **kiểm chứng lại bằng chính code** (23 và 25 chunk, khớp tuyệt đối).
- *Hướng tiếp cận (10/10):* 5 khối giải thích bám sát code thật — nêu được cả lý do chọn (pre-filter, sort ổn định, `setdefault("doc_id")`) lẫn hạn chế đã biết (regex nhầm ở "TS.", "v.v.").
- *Hoàn thiện code (30/30):* **42/42 test pass**, kèm `ingest.py` self-check và `main.py` chạy end-to-end.
- *Dự đoán độ tương tự (5/5):* dự đoán ghi cứng trong script **trước khi chạy**, đo trên **3 backend** thay vì 1, và rút ra được hai kết luận có bằng chứng số (phủ định không được mã hóa; model đa ngữ chênh 0.45 ở cặp song ngữ).
- *Kết quả truy xuất (10/10):* chạy đủ 5 query, có A/B test cho query filter, và **phân tích trung thực điểm 4/10 của chính mình** — chỉ ra chênh lệch doc-level 5/5 vs chunk-level 2/5, quy được nguyên nhân về tham số chunker và đề xuất sửa cụ thể (thêm overlap 1 câu).