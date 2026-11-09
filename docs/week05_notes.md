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

## Chưa làm
- Bản phác Figma (cần tài khoản Figma, tự làm).
- Kiểm tra trên trình duyệt thật (hai cửa sổ RACE-01 → 409, màn hình 390 px): chưa chạy trong phiên này.
- Bài tập 3 (lịch sử có phân trang: `GET /enrollment-events` chưa lọc được theo `dataset`) và Bài tập 4.
