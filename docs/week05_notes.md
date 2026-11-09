# Buổi 5 – Frontend React cho CourseHub

## Đã làm
- Thêm `CORSMiddleware` vào `backend/app/main.py` (origin `localhost:5173`, `127.0.0.1:5173`; GET/POST/DELETE). Nghiệp vụ Buổi 4 (row lock, `enrollment_events`) giữ nguyên, version 0.4.0.
- Tạo `frontend/` (React 18.2.0, Vite 7.1.7): `api.js`, `Notice`, `SectionTable`, `EnrollmentList`, `App.jsx`, `styles.css`.
- `frontend/tests/api.test.mjs`: 8 tình huống HTTP giả lập cho `api.js`.
- `database/14_week05_verify.sql`: truy vấn đối chiếu (tài liệu đặt tên `13_…`, nhưng số 13 đã dùng cho `13_section_event_index.sql` nên đổi thành 14).
- Bài tập 1: tách `components/StudentForm.jsx`, state vẫn ở `App`.
- Bài tập 2: ô chọn học phần lấy từ `GET /courses` (INT2204/INT2205/INT2206); không có lớp phù hợp thì hiện trạng thái rỗng.

## Cách chạy
```
python -m uvicorn backend.app.main:app --reload   # thư mục gốc
cd frontend && cp .env.example .env.local && npm install && npm run dev
```
Mở http://127.0.0.1:5173/.

## Kết quả đo (2026-11-09, Node 24.19.0)
- `npm test`: 8/8 pass. `npm run build`: thành công.
- `GET /health` với Origin `http://127.0.0.1:5173` → `access-control-allow-origin: http://127.0.0.1:5173`; preflight OPTIONS POST → 200, `GET, POST, DELETE`.
- Trước bài: WEB-01 capacity 3, enrolled 2, remaining 1; RACE-01 đã đầy (22000004 giữ chỗ từ Buổi 4).
- POST 22000004/WEB-01 → 201, WEB-01 remaining 0. DELETE → 204, body rỗng, remaining về 1.
- `enrollment_events` (demo) có thêm CREATED rồi CANCELLED cho 22000004/WEB-01.
- `GET /students/99999999/enrollments` → 404.

## Bài tập 3 – lịch sử có phân trang
- Backend: `GET /enrollment-events` thêm tham số `dataset` (`demo` | `performance`, sai giá trị → 422). Không truyền thì giữ hành vi cũ.
- Frontend: `components/EventHistory.jsx`, gọi `?student_id=…&dataset=demo&skip=…&limit=6`, hiển thị 5 dòng/trang (lấy dư 1 dòng để biết còn trang sau). Không tải 100.000 sự kiện performance về trình duyệt.

## Bài tập 4 – tìm kiếm/phân trang phía server cho `GET /sections`
| Tham số | Ý nghĩa | Giới hạn |
|---|---|---|
| `q` | ILIKE trên mã lớp, mã học phần, tên học phần; `%`/`_` được escape | 1–50 ký tự |
| `course_code` | lọc đúng mã học phần | 1–20 ký tự |
| `available_only` | chỉ lớp còn chỗ (đã có) | – |
| `skip` | bỏ qua N dòng | ≥ 0 |
| `limit` | kích thước trang; không truyền = trả toàn bộ như cũ | 1–100 |

Thứ tự `ORDER BY class_id` (khóa duy nhất) nên các trang ổn định, không trùng/sót.

## Kiểm thử Bài tập 3–4 (2026-11-09, schema PostgreSQL tạm, không đụng `public`)
- `python -m backend.tests.week05_exercises_test` → `week05 exercises: OK`: lọc dataset demo, phân trang lịch sử, ghép các trang `/sections` (limit=2) đúng bằng danh sách đầy đủ, tìm `web-0` → WEB-01, WEB-02, tìm theo tên học phần, `%` không khớp tất cả, chuỗi `' OR 1=1` trả rỗng, tham số vượt giới hạn → 422.
- Hồi quy: `exercise01_event_history_test` PASS, `exercise05_project_concurrency_test` PASS, `npm test` 8/8, `npm run build` OK.
- Không chạy `week04_concurrency_test` vì nó xóa đăng ký RACE-01 trên dữ liệu demo thật.

## Chưa làm
- Bản phác Figma (cần tài khoản Figma, tự làm).
- Kiểm tra trên trình duyệt thật (hai cửa sổ RACE-01 → 409, màn hình 390 px, màn hình lịch sử): chưa chạy trong phiên này.
