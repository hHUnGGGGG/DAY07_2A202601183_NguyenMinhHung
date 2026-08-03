# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> *1 câu — ví dụ: thư viện + đăng ký môn học.*

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [ ] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [ ] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

> Nguồn chuẩn của bộ câu hỏi là `bench_queries.py` (phụ trách: Hoàng Anh Quân). Bảng dưới đây chỉ là bản trình bày cho báo cáo — khi hai bên lệch nhau thì lấy `bench_queries.py` làm chuẩn. Mỗi câu kèm `must_contain`: chuỗi bắt buộc phải có trong chunk truy xuất được, dùng để chấm ở **mức chunk** thay vì chỉ kiểm `doc_id`.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1<br>*số liệu* | Hạn chót drop môn của học kỳ chính là ngày làm việc thứ mấy? | Chậm nhất là hết **ngày làm việc thứ 15** của học kỳ (*the close of the 15th business day of the semester*); học kỳ Summer là ngày làm việc thứ 10. Thay đổi trong thời hạn này không bị ghi vào học bạ. | `k3-academic-regulations-undergrad` § Article 12. Course Add, Drop, and Withdrawal<br>`must_contain`: `15th business day` |
| 2<br>*điều kiện* | Điều kiện để được xét Special Sponsor Scholarship từ quỹ tư nhân là gì? | Dành cho ứng viên xuất sắc **đã được cấp học bổng Merit-based từ 80% trở lên** (*a Merit-based Scholarship of 80% or higher*) nhưng gặp rào cản tài chính; hỗ trợ thêm 10% học phí, xét theo tiêu chí riêng của từng quỹ. | `k3-undergrad-scholarships` § Special Sponsor Scholarships from Private Fund<br>`must_contain`: `80% or higher` |
| 3<br>*quy trình* | Sau khi hết hạn add/drop, muốn thêm một môn học thì phải làm thủ tục gì? | Phải nộp **đơn xin (petition)** được **cố vấn học tập (academic advisor)** hoặc Phòng Đào tạo (Office of Registrar) phê duyệt; giảng viên có toàn quyền quyết định có nhận thêm hay không. | `k3-academic-regulations-undergrad` § Article 12<br>`must_contain`: `petition` + `academic advisor` |
| 4<br>*liệt kê* | Mỗi lượt đặt phòng chức năng ở thư viện tối đa bao lâu và tối đa mấy lượt một ngày? | Tối đa **2 giờ/lượt và 2 lượt/ngày**, tính gộp cho mọi phòng (*Max: 2 hours/session, 2 sessions/day for all rooms combined*); chỉ dùng cho mục đích học thuật, đặt qua Microsoft Outlook trong vòng 1 tuần, quá 10 phút không đến thì bị huỷ. | `k3-library-access-services-policy` § 3.2 Using Library Functional Rooms<br>`must_contain`: `2 hours/session` + `2 sessions/day` |
| 5<br>*ngoại lệ + filter*<br>**`audience=student`** | Vi phạm quy định thư viện thì bị xử lý như thế nào? | Sinh viên vi phạm bị xử lý theo **Student Code of Conduct** của VinUni (*students who break library rules may face penalties…*); kèm phạt tiền khi trả muộn / làm hỏng / mất tài liệu theo Financial Regulations and Tariff (hai mức Minor damage và Major damage/loss). Miễn phạt chỉ trong trường hợp nghiêm trọng có bằng chứng (ốm, nhập viện); khiếu nại qua email, xét theo từng ca. | `k3-library-access-services-policy` § 4.1 Consequences<br>`must_contain`: `break library rules` + `Student Code of Conduct` |

**Vì sao Q5 cần lọc metadata:** corpus có **cặp đối chứng** cùng chủ đề, cùng từ vựng, khác `audience` và khác hẳn đáp án — `k3-library-access-services-policy` (`student`: nghĩa vụ của người vi phạm) đối lại `k3-library-management-regulation` (`staff`: quy trình tác nghiệp, nhân viên lập biên bản và đề xuất xử phạt sinh viên, cũng viện dẫn "Student code of conduct"). Câu hỏi **cố tình không nêu người hỏi là ai**. Lưu ý kỹ thuật: cụm `Student Code of Conduct` xuất hiện ở 4/7 tài liệu nên **một mình nó không đủ** phân biệt — phải ghép với `break library rules` (chỉ có trong bản dành cho sinh viên).

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

> Số liệu dưới đây là **điểm retrieval tự động** do `bench.py` chấm ở mức chunk (2 = chunk chứa đủ bằng chứng ở top-1; 1 = có nhưng không ở top-1, hoặc bằng chứng bị chia rời; 0 = không có trong top-3). Đây là **cận trên** của điểm rubric — điểm cuối vẫn cần người đọc kiểm câu trả lời của agent.
>
> Điều kiện chạy giống nhau cho mọi thành viên: corpus `data/k3_university` (7 tài liệu), `EMBEDDING_PROVIDER=local` (`paraphrase-multilingual-MiniLM-L12-v2`), `top_k=3`. **Biến duy nhất là chiến lược chunking.**
>
> ⚠️ Mới đo được 3/5 chiến lược. `HeadingChunker` và `HeadingRecursiveChunker` chưa lập trình xong (`src/heading_chunker.py` còn `NotImplementedError`) nên hai cột đó bỏ trống, **không suy đoán**.

| # | Câu hỏi | sentence<br>(Quân) | fixed<br>(Hùng) | recursive<br>(Đăng) | heading<br>(Huy) | heading_rec<br>(Đức) | Chiến lược tốt nhất cho câu này | Ghi chú |
|---|---------|---|---|---|---|---|---|---|
| Q1 | Hạn chót drop môn | **2** | 1 | **2** | — | — | sentence / recursive | fixed cắt 500 ký tự làm mốc 15th business day rơi xuống hạng 2 |
| Q2 | Điều kiện Special Sponsor Scholarship | 0 | **1** | **1** | — | — | fixed / recursive | Không chiến lược nào đưa được lên top-1: tài liệu học bổng dày đặc số % gây nhiễu |
| Q3 | Thủ tục thêm môn sau add/drop | 0 | 0 | **1** | — | — | recursive | Câu khó nhất. `petition` xuất hiện ở ≥4 ngữ cảnh khác nhau trong cùng tài liệu |
| Q4 | Giới hạn đặt phòng thư viện | 0 | **2** | **2** | — | — | fixed / recursive | sentence cắt 3 câu/chunk làm tách rời "2 hours/session" khỏi ngữ cảnh phòng học |
| Q5 | Xử lý vi phạm thư viện *(có filter)* | **2** | **2** | 0 | — | — | sentence / fixed | recursive cắt 400 ký tự làm vỡ đoạn §4.1 |
| | **TỔNG** | **4/10** | **6/10** | **6/10** | — | — | | |

**Nhận xét:** không có chiến lược nào thắng tuyệt đối — `sentence` mạnh nhất ở Q1/Q5 (đoạn ngắn, câu trả lời gọn trong 1–3 câu) nhưng thua sạch ở Q2/Q3/Q4 (câu trả lời cần ngữ cảnh dài hơn 3 câu). Đáng chú ý: **cả 5 câu đều có `doc_id` gold nằm trong top-3 ở mọi chiến lược**, nghĩa là mọi điểm 0 đều là lỗi **chunk-level chứ không phải doc-level** — nếu chỉ chấm theo `doc_id` thì cả ba chiến lược đều "10/10", một kết luận sai hoàn toàn.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, và đo được trực tiếp ở **Q5** — `bench.py` chạy câu này hai lần (A: `search`, B: `search_with_filter`). **Cả ba chiến lược, filter đều loại đúng `k3-library-management-regulation` (`audience=staff`) khỏi top-3.** Trường hợp rõ nhất là `recursive`: không filter thì **top-1 lẫn top-2 đều là văn bản dành cho nhân viên** (score 0.7039 và 0.6860) — agent sẽ trả lời sinh viên bằng quy trình lập biên bản nội bộ của thư viện; bật filter thì cả 3 slot đều là tài liệu `student`.
>
> Điều đáng nói: **filter không tự nó làm tăng điểm**. Ở `recursive`, Q5 vẫn 0/2 cả khi có filter vì chunk chứa bằng chứng bị cắt vỡ — filter chỉ loại được tài liệu sai đối tượng, không sửa được chunk cắt tồi. Ở `sentence` và `fixed`, top-1 vốn đã đúng nên điểm không đổi (2/2 ở cả A và B); giá trị của filter tại đó là **loại nhiễu khỏi ngữ cảnh đưa vào agent**, chứ không phải đổi thứ hạng top-1.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
