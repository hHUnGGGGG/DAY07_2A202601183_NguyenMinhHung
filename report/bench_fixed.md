```text
====================================================================================================
BENCHMARK — strategy: fixed
  Người chạy       : Nguyễn Minh Hùng
  Chunker + tham số: FixedSizeChunker(chunk_size=500, overlap=50)
  Corpus           : data/k3_university
  Embedding backend: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
  top_k            : 3
====================================================================================================
Đã nạp 342 chunk vào EmbeddingStore.

----------------------------------------------------------------------------------------------------
Q1 [số liệu] Hạn chót drop môn của học kỳ chính là ngày làm việc thứ mấy?
   gold   : Chậm nhất là hết ngày làm việc thứ 15 của học kỳ (no later than the close of the 15th business day of the semester); với học kỳ Summer là ngày làm việc thứ 10. Thay đổi thực hiện trong thời hạn này không bị ghi vào học bạ.
   nguồn  : k3-academic-regulations-undergrad § Article 12. Course Add, Drop, and Withdrawal
   bằng chứng cần có (must_contain): ['15th business day']

   search(top_k=3)
   1. score=0.7355  doc_id=k3-academic-regulations-undergrad  chunk=46  audience=student
      chấp thuận của Giám đốc Chương trình. Điều 12. Thêm, bỏ, rút khóa học Sinh viên được phép thêm một khóa học và...
   2. score=0.6642  doc_id=k3-financial-regulations-tariff  chunk=66  audience=student
      iấy báo có của Ngân hàng VinUni là 26/08/2022 => Ngày hoàn thành nghĩa vụ thanh toán của sinh viên là 26/08/20...
   3. score=0.6590  doc_id=k3-academic-regulations-undergrad  chunk=111  audience=student
      à hoặc báo cáo đồ án cuối kỳ của một lớp học không được sớm hơn ngày được Nhà đăng ký công bố cho ngày cuối cù...

   ĐIỂM RETRIEVAL (tự động): 0/2 — không tìm thấy bằng chứng trong top-3
   doc gold có trong top-3? CÓ   ← doc đúng nhưng CHUNK SAI: đây là failure case đáng viết vào report

   Câu trả lời của agent:
      [DEMO LLM] Generated answer from prompt preview: Bạn là trợ lý trả lời câu hỏi về dịch vụ và quy định đại học. Chỉ dùng NGỮ CẢNH bên dưới để trả lời. Nếu ngữ cảnh không đủ thông tin, hãy nói rõ là không tìm thấy thay vì suy đoán. Trích dẫn số hiệu đoạn ([1], [2]...) cho thông tin bạn dùng. NGỮ CẢNH: [1] nguồn: https://policy.vinuni.edu.vn/all-policies/academic-regulations-for-full-time-undergradua...
   → Điểm rubric cuối cùng cần NGƯỜI đọc kiểm câu trả lời này (2 điểm = top-3 có chunk liên quan VÀ agent trả lời đúng).

----------------------------------------------------------------------------------------------------
Q2 [điều kiện] Điều kiện để được xét Special Sponsor Scholarship từ quỹ tư nhân là gì?
   gold   : Dành cho ứng viên xuất sắc đã được cấp học bổng Merit-based từ 80% trở lên (a Merit-based Scholarship of 80% or higher) nhưng gặp rào cản tài chính; khoản này hỗ trợ thêm 10% học phí và được xét theo tiêu chí riêng của từng quỹ tài trợ.
   nguồn  : k3-undergrad-scholarships § Special Sponsor Scholarships from Private Fund
   bằng chứng cần có (must_contain): ['80% or higher']

   search(top_k=3)
   1. score=0.7300  doc_id=k3-undergrad-scholarships  chunk=6  audience=student
      i. Để tìm hiểu thêm về khoản tài trợ này, vui lòng truy cập [TẠI ĐÂY]. ℹ️ Lưu ý quan trọng: Ứng viên đáp ứng c...
   2. score=0.7123  doc_id=k3-undergrad-scholarships  chunk=2  audience=student
      0% học phí. Học bổng Danh dự của Kỷ luật: Bao gồm 50%, 60% hoặc 70% học phí. (*) Học bổng dựa trên thành tích ...
   3. score=0.6777  doc_id=k3-financial-regulations-tariff  chunk=48  audience=student
      cho các Học bổng Tài năng, Học bổng bổ sung, các mức Hỗ trợ Tài chính và được hiểu bao gồm 35% hỗ trợ phát tri...

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
   1. score=0.6047  doc_id=k3-academic-regulations-undergrad  chunk=58  audience=student
      lại. Sinh viên trượt một môn học bắt buộc trong chương trình học sẽ phải học lại môn học đó hoặc học một môn h...
   2. score=0.6004  doc_id=k3-academic-regulations-undergrad  chunk=43  audience=student
      không quá 14 tín chỉ, áp dụng đối với sinh viên có kết quả học tập kém ở học kỳ trước. Điều này là để hoàn thà...
   3. score=0.5900  doc_id=k3-academic-regulations-undergrad  chunk=47  audience=student
      ỳ và không muộn hơn ngày làm việc thứ 10 của Mùa hè. Những thay đổi được thực hiện trong thời gian này sẽ khôn...

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
   1. score=0.6678  doc_id=k3-library-management-regulation  chunk=24  audience=staff
      trách chìa khóa vào thư viện phải mở/đóng thư viện trước giờ mở cửa quy định 05 phút và đóng cửa sau giờ đóng ...
   2. score=0.6635  doc_id=k3-library-management-regulation  chunk=6  audience=staff
      mục Nhân viên thư viện phải tuân theo sổ tay biên mục cho tất cả các loại tài liệu để đảm bảo nhận dạng và tru...
   3. score=0.6602  doc_id=k3-library-access-services-policy  chunk=13  audience=student
      việc Về trước: 15 phút trước giờ đóng cửa thư viện Quy tắc quan trọng: Đồ quá hạn quá 5 ngày coi như thất lạc;...

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
   1. score=0.8133  doc_id=k3-library-access-services-policy  chunk=15  audience=student
      úng giờ: Đặt chỗ sẽ bị hủy sau 10 phút không có mặt. Kiểm tra hướng dẫn trước khi sử dụng bất kỳ thiết bị nào....
   2. score=0.7661  doc_id=k3-library-management-regulation  chunk=0  audience=staff
      #Quy chế quản lý thư viện 1. Quy định chung Tất cả nhân viên chuyên trách và nhân viên hợp đồng dịch vụ của th...
   3. score=0.7353  doc_id=k3-library-management-regulation  chunk=19  audience=staff
      ường học tập Mọi thay đổi về cách bố trí cơ sở vật chất thư viện, cơ sở hạ tầng, trang thiết bị, trang trí thư...

   [B] CÓ filter {'audience': 'student'} — search_with_filter(top_k=3)
   1. score=0.8133  doc_id=k3-library-access-services-policy  chunk=15  audience=student
      úng giờ: Đặt chỗ sẽ bị hủy sau 10 phút không có mặt. Kiểm tra hướng dẫn trước khi sử dụng bất kỳ thiết bị nào....
   2. score=0.7197  doc_id=k3-library-access-services-policy  chunk=12  audience=student
      n truy cập trên toàn trường đại học và có thể dẫn đến hành động kỷ luật hoặc pháp lý. 2.6. Sao chép, in và qué...
   3. score=0.7150  doc_id=k3-library-access-services-policy  chunk=3  audience=student
      nhận thấy hành vi vi phạm hoặc có thắc mắc, hãy liên hệ với Bảo vệ theo số (0247 108 9779 máy lẻ 9901) hoặc bá...

   A/B: điểm không filter=0  |  có filter=0
        doc top-3 A: ['k3-library-access-services-policy', 'k3-library-management-regulation', 'k3-library-management-regulation']
        doc top-3 B: ['k3-library-access-services-policy', 'k3-library-access-services-policy', 'k3-library-access-services-policy']
        filter đã loại: ['k3-library-management-regulation']

   ĐIỂM RETRIEVAL (tự động): 0/2 — không tìm thấy bằng chứng trong top-3
   doc gold có trong top-3? CÓ   ← doc đúng nhưng CHUNK SAI: đây là failure case đáng viết vào report

   Câu trả lời của agent:
      [DEMO LLM] Generated answer from prompt preview: Bạn là trợ lý trả lời câu hỏi về dịch vụ và quy định đại học. Chỉ dùng NGỮ CẢNH bên dưới để trả lời. Nếu ngữ cảnh không đủ thông tin, hãy nói rõ là không tìm thấy thay vì suy đoán. Trích dẫn số hiệu đoạn ([1], [2]...) cho thông tin bạn dùng. NGỮ CẢNH: [1] nguồn: https://policy.vinuni.edu.vn/all-policies/library-policies-for-users/ | score=0.813 úng ...
   → Điểm rubric cuối cùng cần NGƯỜI đọc kiểm câu trả lời này (2 điểm = top-3 có chunk liên quan VÀ agent trả lời đúng).

====================================================================================================
TỔNG HỢP — fixed (FixedSizeChunker(chunk_size=500, overlap=50))
  Số chunk đã nạp: 342

  | Query | Điểm | Hạng bằng chứng | Doc gold trong top-3 | Ghi chú |
  |-------|------|-----------------|----------------------|---------|
  | Q1 | 0/2 | - | có | không tìm thấy bằng chứng trong top-3 |
  | Q2 | 0/2 | - | có | không tìm thấy bằng chứng trong top-3 |
  | Q3 | 0/2 | - | có | không tìm thấy bằng chứng trong top-3 |
  | Q4 | 0/2 | - | có | không tìm thấy bằng chứng trong top-3 |
  | Q5 | 0/2 | - | có | không tìm thấy bằng chứng trong top-3 |

  ĐIỂM RETRIEVAL TỰ ĐỘNG: 0/10
  (cận trên — điểm rubric thật còn phải kiểm câu trả lời của agent bằng mắt)
====================================================================================================
```
