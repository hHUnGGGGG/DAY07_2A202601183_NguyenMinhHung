# Phiếu thu thập corpus — VinUniversity (K3)

Dùng kèm `docs/DATA_COLLECTION.md`. File này liệt kê **8 tài liệu đã chọn**, URL, phần nội dung cần lấy, và **anchor fact** cần xác minh để viết gold answer.

---

## Quy tắc bắt buộc trước khi lấy dữ liệu

1. Chỉ lấy nội dung **công khai**. Không đăng nhập, không vượt CAPTCHA, không né giới hạn truy cập.
2. `policy.vinuni.edu.vn/robots.txt` = `User-agent: * / Disallow:` — không cấm mục nào. Vẫn đọc điều khoản trang trước khi copy.
3. **`scripts/fetch_public_pages.py` KHÔNG dùng được cho nguồn này.** Đã kiểm chứng ngày 2026-08-03: `vinuni.edu.vn` và `policy.vinuni.edu.vn` trả **HTTP 403 cho mọi user-agent tự động**, kể cả file PDF trong `wp-content/uploads/`. Cách thu thập chính thức: **mở trình duyệt → đọc → copy phần công khai → làm sạch thủ công**. Không tìm cách vượt 403.
4. Làm sạch: bỏ menu, breadcrumb, footer, nút chia sẻ, khối "tin liên quan", banner cookie.
5. Không commit dữ liệu cá nhân, thông tin liên hệ cá nhân, hay nội dung nội bộ.

## Quy tắc dịch

| Việc | Cách làm |
|---|---|
| Con số, %, mốc thời gian, mã văn bản | **Giữ nguyên tuyệt đối** |
| Thuật ngữ chuyên môn | Dịch + để nguyên gốc trong ngoặc lần đầu: `ngày làm việc thứ 15 (the 15th business day)` |
| Câu không chắc nghĩa | Trích nguyên tiếng Anh, **không đoán** |
| Thông tin không có trong nguồn | Không được thêm, kể cả để "cho đủ ý" |
| Khai báo | `language: vi`, `source_language: en`, `translation: manual-vi` |

Anchor fact (cột cuối mỗi bảng dưới) nên **giữ nguyên dạng tiếng Anh** trong bản dịch, vì `bench_queries.py` dùng chính chuỗi đó làm `must_contain` để chấm ở mức chunk.

---

## 1. `vinuni-library-access-services` — audience: **student**

- **URL:** https://policy.vinuni.edu.vn/all-policies/library-policies-for-users/
- **Bản PDF (có mã văn bản):** `.../wp-content/uploads/2025/07/POL-LLR-001-V4.0_Library-Access-Services-Policy_9.7.2025_Clean.pdf`
- **`document_version`:** `POL-LLR-001-V4.0` — *xác minh lại trên bìa PDF*
- **`effective_date`:** 2025-07-09 — *xác minh lại*
- **Lấy phần:** phạm vi áp dụng, quyền truy cập theo nhóm người dùng, quy định đặt phòng học, thời gian mượn, phí phạt.
- **Anchor fact cần xác minh (cho Q4):** thời lượng mỗi lượt đặt phòng và số lượt tối đa mỗi ngày. Nguồn tra cứu ban đầu ghi *"2 hours per session, maximum of 2 sessions per day for all rooms combined"* — **phải mở văn bản gốc đối chiếu trước khi đưa vào gold answer.**

## 2. `vinuni-academic-regulations-undergrad` — audience: **student**

- **URL:** https://policy.vinuni.edu.vn/all-policies/academic-regulations-for-full-time-undergraduate-programs/
- **Trang liên quan:** https://registrar.vinuni.edu.vn/academics/policy-regulations/
- **Lấy phần:** add/drop, withdrawal, class standing, điều kiện tốt nghiệp, thang điểm.
- **Anchor fact (Q1):** hạn chót drop — *"no later than the close of the **15th business day** of the semester"* và *"**10th business day** of the Summer"*.
- **Anchor fact (Q3):** thêm môn sau add/drop — *"need to **petition** with approval from their academic advisor/Office of Registrar"*, và *"Withdrawal – W"* grade.
- Đây là tài liệu gánh 2/5 query → **ưu tiên cao nhất**, làm trước nếu thiếu thời gian.

## 3. `vinuni-student-code-of-conduct` — audience: **student** ⭐ cặp đối chứng

- **URL:** https://policy.vinuni.edu.vn/all-policies/student-affairs-regulations-code-of-conduct/
- **Lấy phần:** quyền và nghĩa vụ sinh viên, hành vi bị cấm, **các mức kỷ luật và hậu quả**, quy trình xử lý.
- **Anchor fact (Q5):** thang/mức kỷ luật áp dụng cho **sinh viên**. Ghi lại chính xác tên các mức (ví dụ `Level 1`, `Level 3`…) — chuỗi này sẽ là `must_contain` của Q5.
- **Làm cùng lúc với tài liệu #6.** Hai người phụ trách #3 và #6 phải ngồi cạnh nhau và xác nhận: *phần xử lý kỷ luật của hai văn bản khác nhau ở điểm nào?* Nếu không tìm được khác biệt thật, báo ngay để đổi khía cạnh Q5 (ví dụ: quy trình khiếu nại, thời hạn báo cáo vi phạm) **trước khi** ai đó chạy benchmark.

## 4. `vinuni-financial-regulations-student` — audience: **student**

- **URL:** https://policy.vinuni.edu.vn/all-policies/financial-regulations-and-tariff-for-student-2/
- **Bản PDF:** `.../wp-content/uploads/2025/08/VU_TS03.EN_Quy-dinh-tai-chinh-va-Bieu-phi_AY25-26_Websent_01.08.2025.pdf`
- **`document_version`:** `VU_TS03.EN` / AY25-26 — *xác minh trên bìa*
- **Lấy phần:** biểu phí, hạn nộp, chính sách hoàn phí, phí trả chậm.
- **Anchor fact:** *"Educational Development Grant ... equivalent to **35% discount** of the listed tuition fees"* — xác minh lại.

## 5. `vinuni-scholarship-maintenance` — audience: **student**

- **URL:** https://policy.vinuni.edu.vn/all-policies/criteria-to-maintain-the-entry-scholarship-and-financial-aid-support/
- **Trang liên quan:** https://policy.vinuni.edu.vn/all-policies/guidelines-for-student-financial-support-request/
- **Lấy phần:** điều kiện duy trì học bổng đầu vào và hỗ trợ tài chính, hệ quả khi không đạt.
- **Anchor fact (Q2):** danh sách điều kiện. Nguồn tra cứu ban đầu nêu: *enrollment in a full-time academic program · demonstration of financial need · satisfactory academic progress (not at-risk academic standing) · **no major disciplinary action (Level 3 and up)** · completion of the necessary application forms* — **đối chiếu văn bản gốc**, đặc biệt chuỗi `Level 3` (dùng làm `must_contain`).

## 6. `vinuni-employees-code-of-conduct` — audience: **staff** ⭐ cặp đối chứng

- **URL:** https://policy.vinuni.edu.vn/all-policies/code-of-conduct/
- **Phạm vi áp dụng (đã ghi trên trang):** *"faculty (including adjunct, visiting, and affiliated faculty) and staff of the University, as well as consultants and contractors"*
- **Lấy phần:** chuẩn mực đạo đức nghề nghiệp, xung đột lợi ích, **quy trình xử lý vi phạm của nhân viên**.
- **Vai trò trong benchmark:** đây là **document nhiễu chủ đích** của Q5. Nó phải đủ giống #3 về từ vựng để lọt top-3 khi không filter, và đủ khác về đáp án để câu trả lời sai lệch nếu agent lấy nhầm.
- `audience: staff` (chọn một giá trị; ghi chú phạm vi gồm cả faculty trong phần thân văn bản, không nhồi hai giá trị vào một field).

## 7. `vinuni-faculty-appointment-promotion` — audience: **faculty**

- **URL:** https://policy.vinuni.edu.vn/all-policies/faculty-appointment-and-promotion-policy-and-procedures/
- **Lấy phần:** bổ nhiệm lần đầu, tái bổ nhiệm, thăng hạng, bổ nhiệm dài hạn; tiêu chí và hội đồng.
- **Vai trò:** tạo giá trị `audience: faculty` thứ ba trong corpus, làm corpus có nhiễu thật khi không filter.

## 8. `vinuni-course-registration-announcement` — audience: **student**

- **URL:** https://registrar.vinuni.edu.vn/2025/12/15/official-announcement-spring-2026-course-registration/
- **Thay thế nếu link đổi:** https://registrar.vinuni.edu.vn/2026/05/22/official-announcement-summer-2026-course-registration/
- **Lấy phần:** lịch đăng ký theo đợt, đối tượng từng đợt, hướng dẫn thao tác, đầu mối hỗ trợ.
- **`document_version`:** thường không có mã → ghi `not-stated`, và dùng `effective_date` = ngày đăng thông báo.
- **Vai trò (Q3):** thông báo tác nghiệp, từ vựng gần với #2 nhưng chi tiết hơn về quy trình → kiểm tra chunker có phân biệt được "quy chế" và "thông báo thực thi" hay không.

---

## Bảng kiểm sau khi thu thập xong

| Kiểm tra | Cách xác nhận |
|---|---|
| 8 file, `doc_id` = tên file, không trùng | `py scripts/check_corpus.py` |
| Đủ 6 field bắt buộc mỗi file | `py scripts/check_corpus.py` |
| `sources.csv` khớp 1–1 | `py scripts/check_corpus.py` |
| `audience` ≥ 2 giá trị | kỳ vọng `student` 6, `staff` 1, `faculty` 1 |
| Không còn marker `TODO` | `py scripts/check_corpus.py` |
| 5 repo cùng corpus | so **corpus hash** do script in ra |
| Anchor fact đã đối chiếu văn bản gốc | người thứ hai đọc lại, ký tên vào `REPORT_NHOM.md` |
