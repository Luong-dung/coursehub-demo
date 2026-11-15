# Buổi 6 - Docker, Testing, CI

## Môi trường
- OS: Windows 11 Pro
- Docker version: 29.9.3, build 5457199, Docker Desktop 4.99.0, WSL2
- Python / Node version: Python 3.12.7 (local, image python:3.12-slim) / Node 24 local, node:22-alpine trong image, 22.12.0 trong CI

## Kết quả local
- pytest -q: 3 passed (test_openapi_contract.py)
- npm test: pass
- npm run build: pass
- docker compose up: backend healthy, frontend started; 8080 và 8000 trả 200

## Một luồng tích hợp đã kiểm tra
- Request: GET http://127.0.0.1:8080/api/students/22000004/enrollments (qua Nginx -> backend:8000 -> PostgreSQL host)
- HTTP status: 200; log backend ghi nhận request từ container frontend (172.18.x.x)
- SQL xác nhận: /health trả "database":"connected"; dữ liệu là database coursehub hiện có

## Debug / AI
- Lỗi gặp phải: `docker compose up --build` (Compose bake) đòi quyền `--allow=fs.read=C:\Users\Admin\OneDrive` vì repo nằm trong OneDrive.
- Cách xử lý: build bằng `docker build` cho từng image rồi `docker compose up -d --no-build`.
- Lỗi khác: các file `*_test.py` cũ là script tích hợp cần PostgreSQL thật, pytest mặc định cũng thu chúng -> thêm pytest.ini chỉ thu `test_*.py`.
- Lỗi tự gây: build trong Git Bash làm MSYS đổi `VITE_API_BASE_URL=/api` thành `C:/Program Files/Git/api`; trang 8080 báo "Không nhận được phản hồi API", log Nginx không có request /api. Sửa: build lại bằng PowerShell (hoặc đặt `MSYS_NO_PATHCONV=1`).
- CI backend dùng biến DB_* giả vì database.py bắt buộc có biến khi import; contract test không kết nối DB.

## Pull Request / CI
- PR:
- Reviewer:
- CI run:
