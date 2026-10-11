# CourseHub - Buoi 3

Backend: FastAPI + SQLAlchemy Core + PostgreSQL.

## Chay ung dung

Tu thu muc goc repository:

```powershell
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --reload
```

Swagger UI: http://127.0.0.1:8000/docs  
Postman environment: `base_url = http://127.0.0.1:8000`

Tao `backend/.env` tu `backend/.env.example` va dien thong tin PostgreSQL.
Khong commit `backend/.env`.

## Luong kiem tra

1. `GET /health`
2. `GET /courses` va `GET /courses?q=web`
3. `GET /sections?available_only=true`
4. Thu `GET /lecturers`, chi tiet section va phan trang courses
5. `POST /enrollments` voi `22000004` vao `WEB-01`
6. Gui lai de kiem tra `409`, body sai de kiem tra `422`
7. `DELETE /enrollments/22000004/WEB-01`
8. Kiem tra lai `GET /sections`

Du lieu mau ban dau: 3 hoc phan, 4 lop, 5 dang ky.
