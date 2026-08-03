# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** B4-E402
**Thành viên:** 
1. Bùi Gia Huy - 2A202601879
2. Phạm Hải Đăng - 2A202601367
3. Nguyễn Minh Hùng - 2A202601183
4. Hoàng Anh Quân - 2A202601875
5. Nguyễn Huy Đức - 2A202601097

**Ngày:** 3/8/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Tập trung chuyên sâu vào các quy định học vụ (đăng ký môn, quy chế học thuật), chính sách tài chính (học phí, học bổng), quy định thư viện và các nội quy áp dụng cho sinh viên/nhân viên tại VinUniversity.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Academic Regulations for Full-Time Undergraduate Programs | policy.vinuni.edu.vn | 2026-08-03 / not-stated | ~ 77k | doc_id, title, source_url, retrieved_at, document_version, audience, department, category, language, source_language, translation |
| 2 | Financial Regulations and Tariff (for student) | policy.vinuni.edu.vn | 2026-08-03 / not-stated | ~ 37k | doc_id, title, source_url, retrieved_at, document_version, audience, department, category, language, source_language, translation |
| 3 | Undergraduate Scholarships | admissions.vinuni.edu.vn | 2026-08-03 / not-stated | ~ 3k | doc_id, title, source_url, retrieved_at, document_version, audience, department, category, language, source_language, translation |
| 4 | Library Access & Services Policy | policy.vinuni.edu.vn | 2026-08-03 / not-stated | ~ 23k | doc_id, title, source_url, retrieved_at, document_version, audience, department, category, language, source_language, translation |
| 5 | Borrow and Request - Undergraduate Students and Staff | library.vinuni.edu.vn | 2026-08-03 / not-stated | ~ 6k | doc_id, title, source_url, retrieved_at, document_version, audience, department, category, language, source_language, translation |
| 6 | Regulation for Library Management | policy.vinuni.edu.vn | 2026-08-03 / not-stated | ~ 19k | doc_id, title, source_url, retrieved_at, document_version, audience, department, category, language, source_language, translation |
| 7 | Residential Life Guideline | policy.vinuni.edu.vn | 2026-08-03 / not-stated | ~ 24k | doc_id, title, source_url, retrieved_at, document_version, audience, department, category, language, source_language, translation |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | Enum | `student`, `staff`, `faculty` | Giúp lọc các quy định để tránh cung cấp thông tin sai đối tượng, đặc biệt với các quy chế xử phạt có sự phân cấp rõ ràng giữa nhân viên và sinh viên. |
| `department` | String | `registrar`, `library`, `finance` | Dùng để gom nhóm các quy định theo phòng ban chuyên trách, tránh nhầm lẫn giữa quy định thư viện và các khoản phí phạt tài chính chung. |
| `document_version` | String | `POL-LLR-001-V4.0`, `not-stated` | Giúp tra cứu văn bản nhanh chóng, đảm bảo LLM đưa ra thông tin dựa trên bản quy định có hiệu lực cập nhật mới nhất. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Academic Regulations | FixedSizeChunker (`fixed_size`) | 155 | 498.5 | Kém (hay cắt ngang từ khóa quan trọng ở cuối cụm 500 ký tự) |
| Academic Regulations | SentenceChunker (`by_sentences`) | 158 | 437.7 | Tốt (giữ trọn vẹn câu, bảo toàn ngữ nghĩa tuyệt đối) |
| Academic Regulations | RecursiveChunker (`recursive`) | 185 | 374.1 | Khá (cắt vụn hơn do ưu tiên các dấu phân cách đoạn) |
| Financial Regulations | FixedSizeChunker (`fixed_size`) | 75 | 496.5 | Kém (phá vỡ cấu trúc bảng biểu học phí) |
| Financial Regulations | SentenceChunker (`by_sentences`) | 66 | 505.0 | Tốt (câu hoàn chỉnh, ngữ cảnh liền mạch) |
| Financial Regulations | RecursiveChunker (`recursive`) | 84 | 397.3 | Trung bình (cắt ở mức danh sách bullet points) |
| Undergrad Scholarships | FixedSizeChunker (`fixed_size`) | 8 | 479.5 | Kém |
| Undergrad Scholarships | SentenceChunker (`by_sentences`) | 9 | 384.4 | Khá |
| Undergrad Scholarships | RecursiveChunker (`recursive`) | 9 | 385.6 | Tốt (do cấu trúc gạch đầu dòng nhiều) |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Minh Hùng**
- **Loại chiến lược:** `FixedSizeChunker(chunk_size=500, overlap=50)`
- **Mô tả & lý do chọn cho chủ đề này:** Chia cắt cứng bằng kích thước cố định. Lý do là để đảm bảo chunk đồng đều, giúp giới hạn số token tối đa đưa vào RAG một cách nghiêm ngặt.

**Thành viên 2 — Hoàng Anh Quân**
- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=3)`
- **Mô tả & lý do chọn:** Cắt dựa trên ranh giới dấu chấm câu. Quy định đại học thường chứa các câu đơn giải thích thể chế dài dòng, việc cắt theo câu giúp LLM lấy được trọn vẹn 1-3 câu lập luận liên tiếp, không làm mất nghĩa.

**Thành viên 3 — Phạm Hải Đăng**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=400)`
- **Mô tả & lý do chọn:** Chia đệ quy qua các separator tự nhiên. Tài liệu dạng sổ tay (Guideline) thường có các cấu trúc đoạn (Paragraph) rõ rệt, đệ quy giúp giữ cho các list và paragraph nguyên vẹn.

**Thành viên 4 — Bùi Gia Huy**
- **Loại chiến lược:** `HeadingChunker(max_chunk_size=800)`
- **Mô tả & lý do chọn:** Phù hợp với các văn bản quy chế dài có đánh số thứ tự Điều (Articles) và Khoản (Sections) rõ ràng.

**Thành viên 5 — Nguyễn Huy Đức**
- **Loại chiến lược:** `HeadingRecursiveChunker(max_chunk_size=800, breadcrumb=True)`
- **Mô tả & lý do chọn:** Gắn lại breadcrumb tiêu đề giúp đoạn trích luôn giữ được context tổng thể của cấu trúc phân cấp, tránh tình trạng chunk chỉ có nội dung mà không biết thuộc "Điều mấy, khoản mấy".

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Hoàng Anh Quân | SentenceChunker | 4/10 | Giữ vẹn nghĩa của các câu ngắn, không bị cắt đôi từ khóa quan trọng. | Thiếu ngữ cảnh lớn khi câu trả lời cần bao quát từ >3 câu (bị cắt đoạn). |
| Nguyễn Minh Hùng | FixedSizeChunker | 6/10 | Bao phủ rộng, kích thước đồng đều giúp dễ quản trị embedding limits. | Cắt cứng làm rớt đáp án ra khỏi câu hỏi, chia cắt ngữ nghĩa. |
| Phạm Hải Đăng | RecursiveChunker | 6/10 | Phân bổ mượt mà các đoạn text tự nhiên, tốt cho quy trình (process) dài. | Các bảng biểu số liệu dễ bị vỡ do xử lý newline (`\n`). |

*(HeadingChunker và HeadingRecursiveChunker chưa có data điểm chính thức do chưa tích hợp vào bench.py, nhưng hứa hẹn mang lại context tốt nhất).*

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **RecursiveChunker** kết hợp hoặc **HeadingRecursiveChunker** là tối ưu nhất cho văn bản Quy định Đại học (University Services). Vì quy chế học vụ luôn được định dạng với cấu trúc thứ bậc (Điều, Khoản, Điểm) rất nghiêm ngặt. Việc sử dụng kỹ thuật cắt theo Semantic (ngữ nghĩa phân đoạn tự nhiên) và gắn thêm breadcrumb tiêu đề giúp RAG nắm bắt trọn vẹn context pháp lý, trong khi chiến lược cắt cứng (FixedSize) khiến LLM lạc lối vì mất đi tiêu đề của Điều luật tương ứng.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1<br>*số liệu* | Hạn chót drop môn của học kỳ chính là ngày làm việc thứ mấy? | Chậm nhất là hết **ngày làm việc thứ 15** của học kỳ (*the close of the 15th business day of the semester*); học kỳ Summer là ngày làm việc thứ 10. Thay đổi trong thời hạn này không bị ghi vào học bạ. | `k3-academic-regulations-undergrad` § Article 12. Course Add, Drop, and Withdrawal<br>`must_contain`: `15th business day` |
| 2<br>*điều kiện* | Điều kiện để được xét Special Sponsor Scholarship từ quỹ tư nhân là gì? | Dành cho ứng viên xuất sắc **đã được cấp học bổng Merit-based từ 80% trở lên** (*a Merit-based Scholarship of 80% or higher*) nhưng gặp rào cản tài chính; hỗ trợ thêm 10% học phí, xét theo tiêu chí riêng của từng quỹ. | `k3-undergrad-scholarships` § Special Sponsor Scholarships from Private Fund<br>`must_contain`: `80% or higher` |
| 3<br>*quy trình* | Sau khi hết hạn add/drop, muốn thêm một môn học thì phải làm thủ tục gì? | Phải nộp **đơn xin (petition)** được **cố vấn học tập (academic advisor)** hoặc Phòng Đào tạo (Office of Registrar) phê duyệt; giảng viên có toàn quyền quyết định có nhận thêm hay không. | `k3-academic-regulations-undergrad` § Article 12<br>`must_contain`: `petition` + `academic advisor` |
| 4<br>*liệt kê* | Mỗi lượt đặt phòng chức năng ở thư viện tối đa bao lâu và tối đa mấy lượt một ngày? | Tối đa **2 giờ/lượt và 2 lượt/ngày**, tính gộp cho mọi phòng (*Max: 2 hours/session, 2 sessions/day for all rooms combined*); chỉ dùng cho mục đích học thuật, đặt qua Microsoft Outlook trong vòng 1 tuần, quá 10 phút không đến thì bị huỷ. | `k3-library-access-services-policy` § 3.2 Using Library Functional Rooms<br>`must_contain`: `2 hours/session` + `2 sessions/day` |
| 5<br>*ngoại lệ + filter*<br>**`audience=student`** | Vi phạm quy định thư viện thì bị xử lý như thế nào? | Sinh viên vi phạm bị xử lý theo **Student Code of Conduct** của VinUni (*students who break library rules may face penalties…*); kèm phạt tiền khi trả muộn / làm hỏng / mất tài liệu theo Financial Regulations and Tariff (hai mức Minor damage và Major damage/loss). Miễn phạt chỉ trong trường hợp nghiêm trọng có bằng chứng (ốm, nhập viện); khiếu nại qua email, xét theo từng ca. | `k3-library-access-services-policy` § 4.1 Consequences<br>`must_contain`: `break library rules` + `Student Code of Conduct` |

**Vì sao Q5 cần lọc metadata:** corpus có **cặp đối chứng** cùng chủ đề, cùng từ vựng, khác `audience` và khác hẳn đáp án — `k3-library-access-services-policy` (`student`: nghĩa vụ của người vi phạm) đối lại `k3-library-management-regulation` (`staff`: quy trình tác nghiệp, nhân viên lập biên bản và đề xuất xử phạt sinh viên, cũng viện dẫn "Student code of conduct"). Câu hỏi **cố tình không nêu người hỏi là ai**. Lưu ý kỹ thuật: cụm `Student Code of Conduct` xuất hiện ở 4/7 tài liệu nên **một mình nó không đủ** phân biệt — phải ghép với `break library rules` (chỉ có trong bản dành cho sinh viên).

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | sentence<br>(Quân) | fixed<br>(Hùng) | recursive<br>(Đăng) | heading<br>(Huy) | heading_rec<br>(Đức) | Chiến lược tốt nhất cho câu này | Ghi chú |
|---|---------|---|---|---|---|---|---|---|
| Q1 | Hạn chót drop môn | **2** | 0 | **2** | — | — | sentence / recursive | fixed cắt ngang làm mốc thời gian văng khỏi top-3 |
| Q2 | Điều kiện Special Sponsor Scholarship | 0 | 0 | **1** | — | — | recursive | Tài liệu học bổng chứa nhiều % gây nhiễu, fixed không bắt được đáp án |
| Q3 | Thủ tục thêm môn sau add/drop | 0 | 0 | **1** | — | — | recursive | `petition` xuất hiện dàn trải, sentence không gom đủ độ rộng |
| Q4 | Giới hạn đặt phòng thư viện | 0 | 0 | **2** | — | — | recursive | sentence cắt 3 câu làm rách ngữ cảnh, fixed băm nát thông số giờ |
| Q5 | Xử lý vi phạm thư viện *(có filter)* | **2** | 0 | 0 | — | — | sentence | recursive cắt 400 ký tự làm vỡ đoạn xử phạt (hậu quả của luật) |
| | **TỔNG** | **4/10** | **0/10** | **6/10** | — | — | | |

**Nhận xét:** Chiến lược `recursive` hoạt động đồng đều nhất nhờ bảo vệ cấu trúc đoạn văn, mặc dù đôi khi phân tách quá chi li. Trái lại, `fixed` đem lại kết quả truy xuất 0/10 điểm tự động, một thất bại thú vị chứng minh rằng dù tài liệu đúng (Gold Doc) được tìm thấy trong top 3, nhưng bằng chứng nằm sai chunk sẽ khiến Agent (LLM) không thể trả lời.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, đo lường vô cùng rõ nét ở **Q5**. Khi bật filter `audience=student`, hệ thống đã mạnh tay gạt bỏ các tài liệu quy trình vận hành thư viện (`audience=staff`), đảm bảo LLM không nhận được các biên bản phạt sai bối cảnh, từ đó đưa ra câu trả lời dựa trên đúng quy chế học vụ dành cho sinh viên. Lọc trước bằng Metadata Filter (Pre-filtering) đóng vai trò quyết định với các nguồn luật lệ phức tạp.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. Truy xuất trúng tài liệu không đồng nghĩa với việc truy xuất trúng đoạn chứa câu trả lời. Khoảng cách (Gap) giữa 5/5 Docs Hit và 0/5 Chunks Hit ở FixedSizeChunker minh hoạ rất rõ vai trò của Chunk Coherence.
> 2. Filter theo Metadata giúp giải quyết triệt để nhiễu loạn thông tin (Noise) giữa các phòng ban và nhóm đối tượng khác nhau (Staff vs Student).
> 3. Mô hình Embedding hiện nay cực kì nhạy cảm với cấu trúc từ khóa nhưng lại dễ bị đánh lừa bởi các yếu tố "Khẳng định/Phủ định" (như `Có` vs `Không`), RAG prompt cần bổ trợ chặt chẽ.

**Bài học rút ra khi so sánh trong nhóm:**
> Khi cắt theo các giới hạn cứng (Fixed Size) không tôn trọng ngữ nghĩa câu chữ, xác suất từ khóa bị cắt tách rời khỏi con số đáp án tăng rất cao. Trong khi đó, việc bám vào ngữ nghĩa dấu chấm câu (Sentence) hoặc đoạn văn (Recursive) lại cải thiện điểm Retrieval lên tới 4-6 điểm cho các câu hỏi logic rải rác.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ thiết kế Chunk theo hướng Hierarchical (như HeadingRecursiveChunker), luôn đính kèm đường dẫn thư mục (Breadcrumb: Ví dụ `Điều 12 > Khoản 1 > ...`) vào đầu mỗi chunk trước khi nhúng (embed). Điều này không chỉ giúp LLM hiểu chính xác nguồn gốc, mà Vector Embedding cũng có thêm tín hiệu mạnh mẽ hơn để Retrieval trúng trọng tâm câu hỏi người dùng.
