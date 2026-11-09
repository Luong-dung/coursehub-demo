from __future__ import annotations

import requests
from sqlalchemy import text

from backend.tests.support import isolated_database, running_api


def main() -> None:
    with isolated_database() as (engine, schema):
        with engine.begin() as connection:
            connection.execute(text("""
                INSERT INTO enrollment_events
                    (student_id, class_section_id, event_type, occurred_at)
                VALUES
                    ('22000001', 'WEB-01', 'CREATED', '2026-01-01'),
                    ('22000001', 'WEB-01', 'CANCELLED', '2026-01-01'),
                    ('22000002', 'WEB-02', 'CREATED', '2026-01-02')
            """))
        with running_api(schema) as base:
            def get(**params):
                return requests.get(f"{base}/enrollment-events", params=params, timeout=5)

            response = get()
            assert response.status_code == 200, response.text
            rows = response.json()
            assert [row["id"] for row in rows] == [3, 2, 1], rows
            assert [row["id"] for row in get(skip=1, limit=1).json()] == [2]
            assert [row["id"] for row in get(student_id="22000001").json()] == [2, 1]
            assert [row["id"] for row in get(student_id="22000001", event_type="CREATED").json()] == [1]
            assert [row["id"] for row in get(event_type="CANCELLED").json()] == [2]
            assert get(student_id="99999999").json() == []
            assert get(skip=100).json() == []
            assert get(limit=100).status_code == 200
            for params in (
                {"limit": 0}, {"limit": 101}, {"skip": -1},
                {"event_type": "INVALID"}, {"student_id": "123"},
                {"student_id": "' OR 1=1"}, {"limit": "oops"},
            ):
                response = get(**params)
                # Eight-character injection input is treated as a literal value.
                if params == {"student_id": "' OR 1=1"}:
                    assert response.status_code == 200 and response.json() == []
                else:
                    assert response.status_code == 422, (params, response.text)
        print("PASS: history filters, empty data, stable ties/pagination, bounds and bind parameters.")


if __name__ == "__main__":
    main()
