```text
====================================================================================================
BENCHMARK — strategy: sentence
  Người chạy       : Hoàng Anh Quân
  Chunker + tham số: SentenceChunker(max_sentences_per_chunk=3)
  Corpus           : data/k3_university
  Embedding backend: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
  top_k            : 3
====================================================================================================
Đã nạp 353 chunk vào EmbeddingStore.

----------------------------------------------------------------------------------------------------
Q1 [số liệu] Hạn chót drop môn của học kỳ chính là ngày làm việc thứ mấy?
   gold   : Chậm nhất là hết ngày làm việc thứ 15 của học kỳ (no later than the close of the 15th business day of the semester); với học kỳ Summer là ngày làm việc thứ 10. Thay đổi thực hiện trong thời hạn này không bị ghi vào học bạ.
   nguồn  : k3-academic-regulations-undergrad § Article 12. Course Add, Drop, and Withdrawal
   bằng chứng cần có (must_contain): ['15th business day']

   search(top_k=3)
   1. score=0.7531  doc_id=k3-academic-regulations-undergrad  chunk=51  audience=student
      The drop deadline for a regular semester is no later than the close of the 15th business day of the semester a...
   2. score=0.6852  doc_id=k3-academic-regulations-undergrad  chunk=50  audience=student
      Article 12. Course Add, Drop, and Withdrawal Students are allowed to add a course to their schedule no later t...
   3. score=0.6413  doc_id=k3-academic-regulations-undergrad  chunk=112  audience=student
      Final examinations requiring assignment of an exam time are scheduled by the Office of Registrar to avoid conf...

   ĐIỂM RETRIEVAL (tự động): 2/2 — chunk chứa đủ bằng chứng ở top-1
   doc gold có trong top-3? CÓ

   Câu trả lời của agent:
      [DEMO LLM] Generated answer from prompt preview: Bạn là trợ lý trả lời câu hỏi về dịch vụ và quy định đại học. Chỉ dùng NGỮ CẢNH bên dưới để trả lời. Nếu ngữ cảnh không đủ thông tin, hãy nói rõ là không tìm thấy thay vì suy đoán. Trích dẫn số hiệu đoạn ([1], [2]...) cho thông tin bạn dùng. NGỮ CẢNH: [1] nguồn: https://policy.vinuni.edu.vn/all-policies/academic-regulations-for-full-time-undergradua...
   → Điểm rubric cuối cùng cần NGƯỜI đọc kiểm câu trả lời này (2 điểm = top-3 có chunk liên quan VÀ agent trả lời đúng).

----------------------------------------------------------------------------------------------------
Q2 [điều kiện] Điều kiện để được xét Special Sponsor Scholarship từ quỹ tư nhân là gì?
   gold   : Dành cho ứng viên xuất sắc đã được cấp học bổng Merit-based từ 80% trở lên (a Merit-based Scholarship of 80% or higher) nhưng gặp rào cản tài chính; khoản này hỗ trợ thêm 10% học phí và được xét theo tiêu chí riêng của từng quỹ tài trợ.
   nguồn  : k3-undergrad-scholarships § Special Sponsor Scholarships from Private Fund
   bằng chứng cần có (must_contain): ['80% or higher']

   search(top_k=3)
   1. score=0.7158  doc_id=k3-undergrad-scholarships  chunk=6  audience=student
      To learn more about this grant, please visit [HERE]. ℹ️ Important Note: Applicants who meet the admission crit...
   2. score=0.6509  doc_id=k3-undergrad-scholarships  chunk=3  audience=student
      Special Encouragement Scholarships (*Stackable) Special Academic Scholarship: Offers a 5% tuition waiver for s...
   3. score=0.6315  doc_id=k3-financial-regulations-tariff  chunk=43  audience=student
      The Educational Development Grant is already included in the Merit-based Scholarship (ranging from 50% to full...

   ĐIỂM RETRIEVAL (tự động): 0/2 — không tìm thấy bằng chứng trong top-3
   doc gold có trong top-3? CÓ   ← doc đúng nhưng CHUNK SAI: đây là failure case đáng viết vào report

   Câu trả lời của agent:
      [DEMO LLM] Generated answer from prompt preview: Bạn là trợ lý trả lời câu hỏi về dịch vụ và quy định đại học. Chỉ dùng NGỮ CẢNH bên dưới để trả lời. Nếu ngữ cảnh không đủ thông tin, hãy nói rõ là không tìm thấy thay vì suy đoán. Trích dẫn số hiệu đoạn ([1], [2]...) cho thông tin bạn dùng. NGỮ CẢNH: [1] nguồn: https://admissions.vinuni.edu.vn/scholarship-and-financial-aid/undergraduate-programs/sc...
   → Điểm rubric cuối cùng cần NGƯỜI đọc kiểm câu trả lời này (2 điểm = top-3 có chunk liên quan VÀ agent trả lời đúng).

----------------------------------------------------------------------------------------------------
Q3 [quy trình] Sau khi hết hạn add/drop, muốn thêm một môn học thì phải làm thủ tục gì?
   gold   : Phải nộp đơn xin (petition) và được cố vấn học tập (academic advisor) hoặc Phòng Đào tạo (Office of Registrar) phê duyệt; giảng viên có toàn quyền quyết định có nhận thêm sinh viên vào lớp hay không.
   nguồn  : k3-academic-regulations-undergrad § Article 12. Course Add, Drop, and Withdrawal
   bằng chứng cần có (must_contain): ['petition', 'academic advisor']

   search(top_k=3)
   1. score=0.5945  doc_id=k3-academic-regulations-undergrad  chunk=129  audience=student
      The final decision as to whether an incomplete may be given rests with the instructor; however, the maximum ti...
   2. score=0.5761  doc_id=k3-academic-regulations-undergrad  chunk=50  audience=student
      Article 12. Course Add, Drop, and Withdrawal Students are allowed to add a course to their schedule no later t...
   3. score=0.5635  doc_id=k3-academic-regulations-undergrad  chunk=47  audience=student
      This is to complete the degree requirements within a normal specified duration of study. Automatic Overload 18...

   ĐIỂM RETRIEVAL (tự động): 0/2 — không tìm thấy bằng chứng trong top-3
   doc gold có trong top-3? CÓ   ← doc đúng nhưng CHUNK SAI: đây là failure case đáng viết vào report

   Câu trả lời của agent:
      [DEMO LLM] Generated answer from prompt preview: Bạn là trợ lý trả lời câu hỏi về dịch vụ và quy định đại học. Chỉ dùng NGỮ CẢNH bên dưới để trả lời. Nếu ngữ cảnh không đủ thông tin, hãy nói rõ là không tìm thấy thay vì suy đoán. Trích dẫn số hiệu đoạn ([1], [2]...) cho thông tin bạn dùng. NGỮ CẢNH: [1] nguồn: https://policy.vinuni.edu.vn/all-policies/academic-regulations-for-full-time-undergradua...
   → Điểm rubric cuối cùng cần NGƯỜI đọc kiểm câu trả lời này (2 điểm = top-3 có chunk liên quan VÀ agent trả lời đúng).

----------------------------------------------------------------------------------------------------
Q4 [liệt kê] Mỗi lượt đặt phòng chức năng ở thư viện tối đa bao lâu và tối đa mấy lượt một ngày?
   gold   : Tối đa 2 giờ mỗi lượt và 2 lượt mỗi ngày, tính gộp cho tất cả các phòng (Max: 2 hours/session, 2 sessions/day for all rooms combined). Chỉ dùng cho mục đích học thuật, đặt trước qua Microsoft Outlook trong vòng 1 tuần, quá 10 phút không đến thì lượt đặt bị huỷ.
   nguồn  : k3-library-access-services-policy § 3.2 Using Library Functional Rooms
   bằng chứng cần có (must_contain): ['2 hours/session', '2 sessions/day']

   search(top_k=3)
   1. score=0.6647  doc_id=k3-library-management-regulation  chunk=18  audience=staff
      During working hours, library staff should ensure patrons using library space and physical facility comply wit...
   2. score=0.6121  doc_id=k3-library-borrow-request-undergrad  chunk=4  audience=student
      Due time is 15 minutes before library’s closing time. Equipment overdue for more than 05 days will be consider...
   3. score=0.6019  doc_id=k3-library-access-services-policy  chunk=21  audience=student
      3. Use of library property & spaces 3.1. Borrowing Library Equipment Loan period: 1 working day Return by: 15 ...

   ĐIỂM RETRIEVAL (tự động): 0/2 — không tìm thấy bằng chứng trong top-3
   doc gold có trong top-3? CÓ   ← doc đúng nhưng CHUNK SAI: đây là failure case đáng viết vào report

   Câu trả lời của agent:
      [DEMO LLM] Generated answer from prompt preview: Bạn là trợ lý trả lời câu hỏi về dịch vụ và quy định đại học. Chỉ dùng NGỮ CẢNH bên dưới để trả lời. Nếu ngữ cảnh không đủ thông tin, hãy nói rõ là không tìm thấy thay vì suy đoán. Trích dẫn số hiệu đoạn ([1], [2]...) cho thông tin bạn dùng. NGỮ CẢNH: [1] nguồn: https://policy.vinuni.edu.vn/all-policies/regulation-for-library-management/ | score=0.6...
   → Điểm rubric cuối cùng cần NGƯỜI đọc kiểm câu trả lời này (2 điểm = top-3 có chunk liên quan VÀ agent trả lời đúng).

----------------------------------------------------------------------------------------------------
Q5 [ngoại lệ + filter] Vi phạm quy định thư viện thì bị xử lý như thế nào?
   gold   : Theo góc nhìn SINH VIÊN: sinh viên vi phạm quy định thư viện có thể bị xử lý kỷ luật theo Student Code of Conduct của VinUni (students who break library rules may face penalties based on VinUni's Student Code of Conduct); ngoài ra bị phạt tiền khi trả muộn hoặc làm hỏng/mất tài liệu, thiết bị, mức phạt theo Financial Regulations and Tariff, chia hai mức Minor damage và Major damage/loss. Chỉ được miễn phạt trong trường hợp nghiêm trọng (ốm đau, nhập viện — có bằng chứng); khiếu nại gửi email cho thư viện, xét theo từng trường hợp.
   nguồn  : k3-library-access-services-policy § 4. Library regulation violations (4.1 Consequences)
   bằng chứng cần có (must_contain): ['break library rules', 'Student Code of Conduct']

   [A] KHÔNG filter — search(top_k=3)
   1. score=0.8246  doc_id=k3-library-access-services-policy  chunk=27  audience=student
      Library regulation violations 4.1. Consequences Students who break library rules may face penalties based on V...
   2. score=0.7211  doc_id=k3-library-management-regulation  chunk=0  audience=staff
      # Regulation for Library Management 1. General regulations All library’s full-time staff and service-contract ...
   3. score=0.6469  doc_id=k3-library-borrow-request-undergrad  chunk=6  audience=student
      For more detailed, please read it in Library Policies for users. These fines and fees are regulated in VinUni’...

   [B] CÓ filter {'audience': 'student'} — search_with_filter(top_k=3)
   1. score=0.8246  doc_id=k3-library-access-services-policy  chunk=27  audience=student
      Library regulation violations 4.1. Consequences Students who break library rules may face penalties based on V...
   2. score=0.6469  doc_id=k3-library-borrow-request-undergrad  chunk=6  audience=student
      For more detailed, please read it in Library Policies for users. These fines and fees are regulated in VinUni’...
   3. score=0.6416  doc_id=k3-library-access-services-policy  chunk=10  audience=student
      Use of library materials 2.1. Circulation regulations for library materials No. Material types Can Borrow?

   A/B: điểm không filter=2  |  có filter=2
        doc top-3 A: ['k3-library-access-services-policy', 'k3-library-management-regulation', 'k3-library-borrow-request-undergrad']
        doc top-3 B: ['k3-library-access-services-policy', 'k3-library-borrow-request-undergrad', 'k3-library-access-services-policy']
        filter đã loại: ['k3-library-management-regulation']

   ĐIỂM RETRIEVAL (tự động): 2/2 — chunk chứa đủ bằng chứng ở top-1
   doc gold có trong top-3? CÓ

   Câu trả lời của agent:
      [DEMO LLM] Generated answer from prompt preview: Bạn là trợ lý trả lời câu hỏi về dịch vụ và quy định đại học. Chỉ dùng NGỮ CẢNH bên dưới để trả lời. Nếu ngữ cảnh không đủ thông tin, hãy nói rõ là không tìm thấy thay vì suy đoán. Trích dẫn số hiệu đoạn ([1], [2]...) cho thông tin bạn dùng. NGỮ CẢNH: [1] nguồn: https://policy.vinuni.edu.vn/all-policies/library-policies-for-users/ | score=0.825 Libr...
   → Điểm rubric cuối cùng cần NGƯỜI đọc kiểm câu trả lời này (2 điểm = top-3 có chunk liên quan VÀ agent trả lời đúng).

====================================================================================================
TỔNG HỢP — sentence (SentenceChunker(max_sentences_per_chunk=3))
  Số chunk đã nạp: 353

  | Query | Điểm | Hạng bằng chứng | Doc gold trong top-3 | Ghi chú |
  |-------|------|-----------------|----------------------|---------|
  | Q1 | 2/2 | 1 | có | chunk chứa đủ bằng chứng ở top-1 |
  | Q2 | 0/2 | - | có | không tìm thấy bằng chứng trong top-3 |
  | Q3 | 0/2 | - | có | không tìm thấy bằng chứng trong top-3 |
  | Q4 | 0/2 | - | có | không tìm thấy bằng chứng trong top-3 |
  | Q5 | 2/2 | 1 | có | chunk chứa đủ bằng chứng ở top-1 |

  ĐIỂM RETRIEVAL TỰ ĐỘNG: 4/10
  (cận trên — điểm rubric thật còn phải kiểm câu trả lời của agent bằng mắt)
====================================================================================================
```
