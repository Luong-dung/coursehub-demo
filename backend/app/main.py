from __future__ import annotations

from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .database import engine
from .schemas import CapacityUpdate, EnrollmentCreate


app = FastAPI(
    title="CourseHub API",
    version="0.4.0",
    description="API thuc hanh Buoi 4 - transaction, locking va hieu nang",
)

# Buoi 5: chi cho phep frontend local goi API qua trinh duyet.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "CourseHub API dang hoat dong"}


@app.get("/health")
def health_check() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Khong the ket noi co so du lieu",
        )

    return {"status": "ok", "database": "connected"}


@app.get("/courses")
def list_courses(
    q: str | None = Query(default=None, min_length=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
) -> list[dict[str, Any]]:
    sql = """
        SELECT code, name, credits
        FROM courses
    """
    parameters: dict[str, Any] = {"skip": skip, "limit": limit}

    if q is not None:
        keyword = q.strip().lower()
        if not keyword:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tu khoa tim kiem khong duoc rong",
            )
        sql += """
            WHERE LOWER(code) LIKE :keyword
               OR LOWER(name) LIKE :keyword
        """
        parameters["keyword"] = f"%{keyword}%"

    sql += " ORDER BY code OFFSET :skip LIMIT :limit"

    with engine.connect() as connection:
        rows = connection.execute(text(sql), parameters).mappings().all()

    return [dict(row) for row in rows]


@app.get("/courses/{course_code}")
def get_course(course_code: str) -> dict[str, Any]:
    sql = """
        SELECT code, name, credits
        FROM courses
        WHERE code = :course_code
    """

    with engine.connect() as connection:
        row = connection.execute(
            text(sql),
            {"course_code": course_code.upper()},
        ).mappings().first()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay hoc phan",
        )

    return dict(row)


@app.get("/lecturers")
def list_lecturers() -> list[dict[str, Any]]:
    sql = "SELECT id, name FROM lecturers ORDER BY id"

    with engine.connect() as connection:
        rows = connection.execute(text(sql)).mappings().all()

    return [dict(row) for row in rows]


@app.get("/sections")
def list_sections(
    available_only: bool = False,
    q: str | None = Query(default=None, min_length=1, max_length=50),
    course_code: str | None = Query(default=None, min_length=1, max_length=20),
    skip: int = Query(default=0, ge=0),
    limit: int | None = Query(default=None, ge=1, le=100),
) -> list[dict[str, Any]]:
    # Bai tap 5.4: loc/phan trang tai PostgreSQL. Khong truyen limit thi giu
    # hanh vi cu (tra toan bo) cho frontend Buoi 5.
    sql = """
        SELECT s.class_id, s.course_code, s.capacity, s.enrolled, s.remaining
        FROM v_section_summary s
        JOIN courses c ON c.code = s.course_code
        WHERE 1 = 1
    """
    parameters: dict[str, Any] = {"skip": skip}

    if available_only:
        sql += " AND s.remaining > 0"
    if course_code is not None:
        sql += " AND s.course_code = :course_code"
        parameters["course_code"] = course_code
    if q is not None:
        sql += """ AND (s.class_id ILIKE :pattern OR s.course_code ILIKE :pattern
                     OR c.name ILIKE :pattern)"""
        escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        parameters["pattern"] = f"%{escaped}%"

    # class_id la khoa duy nhat nen thu tu on dinh giua cac trang.
    sql += " ORDER BY s.class_id OFFSET :skip"
    if limit is not None:
        sql += " LIMIT :limit"
        parameters["limit"] = limit

    with engine.connect() as connection:
        rows = connection.execute(text(sql), parameters).mappings().all()

    return [dict(row) for row in rows]


@app.get("/sections/{section_id}")
def get_section(section_id: str) -> dict[str, Any]:
    sql = """
        SELECT
            cs.id AS class_id,
            c.code AS course_code,
            c.name AS course_name,
            s.code AS semester_code,
            s.name AS semester_name,
            l.id AS lecturer_id,
            l.name AS lecturer_name,
            summary.capacity,
            summary.enrolled,
            summary.remaining
        FROM class_sections AS cs
        JOIN courses AS c ON c.code = cs.course_code
        JOIN semesters AS s ON s.code = cs.semester_code
        JOIN lecturers AS l ON l.id = cs.lecturer_id
        JOIN v_section_summary AS summary ON summary.class_id = cs.id
        WHERE cs.id = :section_id
    """

    with engine.connect() as connection:
        row = connection.execute(
            text(sql),
            {"section_id": section_id},
        ).mappings().first()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay lop hoc phan",
        )

    return dict(row)


@app.patch(
    "/sections/{section_id}/capacity",
    response_model=dict[str, Any],
)
def update_section_capacity(
    section_id: str,
    payload: CapacityUpdate,
) -> dict[str, Any]:
    lock_section_sql = """
        SELECT id
        FROM class_sections
        WHERE id = :section_id
        FOR UPDATE
    """
    count_sql = """
        SELECT COUNT(*)
        FROM enrollments
        WHERE class_section_id = :section_id
    """

    with engine.begin() as connection:
        row = connection.execute(
            text(lock_section_sql),
            {"section_id": section_id},
        ).first()

        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay lop hoc phan",
            )

        enrolled = int(connection.execute(
            text(count_sql), {"section_id": section_id}
        ).scalar_one())
        if payload.capacity < enrolled:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Suc chua khong duoc nho hon so sinh vien da dang ky",
            )

        connection.execute(
            text(
                """
                UPDATE class_sections
                SET capacity = :capacity
                WHERE id = :section_id
                """
            ),
            {"capacity": payload.capacity, "section_id": section_id},
        )

    return {"class_section_id": section_id, "capacity": payload.capacity}


@app.get("/students/{student_id}/enrollments")
def list_student_enrollments(student_id: str) -> list[dict[str, Any]]:
    student_sql = "SELECT id FROM students WHERE id = :student_id"
    enrollment_sql = """
        SELECT e.student_id,
               s.name AS student_name,
               cs.id AS class_section_id,
               c.code AS course_code,
               c.name AS course_name,
               e.registered_at
        FROM enrollments AS e
        JOIN students AS s ON s.id = e.student_id
        JOIN class_sections AS cs ON cs.id = e.class_section_id
        JOIN courses AS c ON c.code = cs.course_code
        WHERE e.student_id = :student_id
        ORDER BY cs.id
    """

    with engine.connect() as connection:
        student = connection.execute(
            text(student_sql),
            {"student_id": student_id},
        ).first()

        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay sinh vien",
            )

        rows = connection.execute(
            text(enrollment_sql),
            {"student_id": student_id},
        ).mappings().all()

    return [dict(row) for row in rows]


@app.get("/enrollment-events")
def list_enrollment_events(
    student_id: str | None = Query(default=None, min_length=8, max_length=8),
    event_type: Literal["CREATED", "CANCELLED"] | None = None,
    dataset: Literal["demo", "performance"] | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
) -> list[dict[str, Any]]:
    sql = """
        SELECT id, student_id, class_section_id, event_type,
               source, dataset, occurred_at
        FROM enrollment_events
        WHERE 1 = 1
    """
    parameters: dict[str, Any] = {"skip": skip, "limit": limit}
    if student_id is not None:
        sql += " AND student_id = :student_id"
        parameters["student_id"] = student_id
    if event_type is not None:
        sql += " AND event_type = :event_type"
        parameters["event_type"] = event_type
    if dataset is not None:
        sql += " AND dataset = :dataset"
        parameters["dataset"] = dataset
    sql += " ORDER BY occurred_at DESC, id DESC OFFSET :skip LIMIT :limit"

    with engine.connect() as connection:
        rows = connection.execute(text(sql), parameters).mappings().all()
    return [dict(row) for row in rows]


@app.post(
    "/enrollments",
    status_code=status.HTTP_201_CREATED,
)
def create_enrollment(payload: EnrollmentCreate) -> dict[str, str]:
    student_sql = "SELECT id FROM students WHERE id = :student_id"
    lock_section_sql = """
        SELECT id, capacity
        FROM class_sections
        WHERE id = :class_section_id
        FOR UPDATE
    """
    duplicate_sql = """
        SELECT 1
        FROM enrollments
        WHERE student_id = :student_id
          AND class_section_id = :class_section_id
    """
    count_sql = """
        SELECT COUNT(*)
        FROM enrollments
        WHERE class_section_id = :class_section_id
    """
    insert_sql = """
        INSERT INTO enrollments (student_id, class_section_id)
        VALUES (:student_id, :class_section_id)
    """
    event_sql = """
        INSERT INTO enrollment_events
            (student_id, class_section_id, event_type, source, dataset)
        VALUES
            (:student_id, :class_section_id, 'CREATED', 'api', 'demo')
    """
    parameters = {
        "student_id": payload.student_id,
        "class_section_id": payload.class_section_id,
    }

    try:
        with engine.begin() as connection:
            student = connection.execute(
                text(student_sql),
                {"student_id": payload.student_id},
            ).first()
            if student is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Khong tim thay sinh vien",
                )

            section = connection.execute(
                text(lock_section_sql),
                {"class_section_id": payload.class_section_id},
            ).mappings().first()
            if section is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Khong tim thay lop hoc phan",
                )

            duplicated = connection.execute(
                text(duplicate_sql), parameters
            ).first()
            if duplicated is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Sinh vien da dang ky lop nay",
                )

            enrolled = connection.execute(
                text(count_sql),
                {"class_section_id": payload.class_section_id},
            ).scalar_one()
            if int(enrolled) >= int(section["capacity"]):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Lop hoc phan da het cho",
                )

            connection.execute(text(insert_sql), parameters)
            connection.execute(text(event_sql), parameters)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Dang ky xung dot voi du lieu hien tai",
        ) from exc

    return {
        "message": "Dang ky thanh cong",
        "student_id": payload.student_id,
        "class_section_id": payload.class_section_id,
    }


@app.delete(
    "/enrollments/{student_id}/{class_section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_enrollment(student_id: str, class_section_id: str) -> Response:
    lock_section_sql = """
        SELECT id
        FROM class_sections
        WHERE id = :class_section_id
        FOR UPDATE
    """
    delete_sql = """
        DELETE FROM enrollments
        WHERE student_id = :student_id
          AND class_section_id = :class_section_id
        RETURNING student_id
    """
    event_sql = """
        INSERT INTO enrollment_events
            (student_id, class_section_id, event_type, source, dataset)
        VALUES
            (:student_id, :class_section_id, 'CANCELLED', 'api', 'demo')
    """
    parameters = {
        "student_id": student_id,
        "class_section_id": class_section_id,
    }

    with engine.begin() as connection:
        section = connection.execute(
            text(lock_section_sql),
            {"class_section_id": class_section_id},
        ).first()
        if section is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay lop hoc phan",
            )

        deleted = connection.execute(
            text(delete_sql), parameters
        ).first()
        if deleted is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay dang ky can huy",
            )

        connection.execute(text(event_sql), parameters)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
