"""Buoi 5 - Bai tap 3/4: loc dataset cho lich su va loc/phan trang /sections."""
from __future__ import annotations

import requests
from sqlalchemy import text

from backend.tests.support import isolated_database, running_api


def main() -> None:
    with isolated_database() as (engine, schema):
        with engine.begin() as connection:
            connection.execute(text("""
                INSERT INTO enrollment_events
                    (student_id, class_section_id, event_type, dataset, occurred_at)
                VALUES
                    ('22000001', 'WEB-01', 'CREATED', 'demo', '2026-01-01'),
                    ('22000001', 'WEB-01', 'CANCELLED', 'performance', '2026-01-02'),
                    ('22000001', 'WEB-02', 'CREATED', 'demo', '2026-01-03')
            """))
            all_ids = [r[0] for r in connection.execute(text(
                "SELECT id FROM class_sections ORDER BY id"))]
        with running_api(schema) as base:
            def ev(**p):
                return requests.get(f"{base}/enrollment-events", params=p, timeout=5)

            def sec(**p):
                return requests.get(f"{base}/sections", params=p, timeout=5)

            # Bai 3: chi lay nhat ky demo, co phan trang.
            demo = ev(student_id="22000001", dataset="demo").json()
            assert [r["class_section_id"] for r in demo] == ["WEB-02", "WEB-01"], demo
            assert all(r["dataset"] == "demo" for r in demo)
            assert len(ev(student_id="22000001", dataset="demo", limit=1).json()) == 1
            assert ev(student_id="22000001", dataset="demo", skip=2).json() == []
            assert len(ev(student_id="22000001").json()) == 3
            assert ev(dataset="other").status_code == 422

            # Bai 4: khong tham so -> giu hanh vi cu.
            assert [r["class_id"] for r in sec().json()] == all_ids
            # Phan trang on dinh theo class_id, cac trang noi lai dung bang toan bo.
            pages, skip = [], 0
            while True:
                page = sec(skip=skip, limit=2).json()
                if not page:
                    break
                pages += [r["class_id"] for r in page]
                skip += 2
            assert pages == all_ids, pages
            # Tim khong phan biet hoa/thuong tren ma lop va ten hoc phan.
            assert [r["class_id"] for r in sec(q="web-0").json()] == ["WEB-01", "WEB-02"]
            by_name = sec(q="du lieu web").json()
            assert by_name and all(r["course_code"] == "INT2204" for r in by_name), by_name
            assert all(r["course_code"] == "INT2205"
                       for r in sec(course_code="INT2205").json())
            assert sec(q="%").json() == [], "ky tu % phai duoc escape"
            assert sec(q="' OR 1=1").json() == []
            for p in ({"limit": 0}, {"limit": 101}, {"skip": -1}, {"q": "x" * 51}):
                assert sec(**p).status_code == 422, p
    print("week05 exercises: OK")


if __name__ == "__main__":
    main()
