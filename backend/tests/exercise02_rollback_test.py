from __future__ import annotations

import requests
from sqlalchemy import text

from backend.tests.support import isolated_database, running_api


def snapshot(engine):
    with engine.connect() as connection:
        return (
            connection.execute(text("SELECT * FROM enrollments ORDER BY student_id, class_section_id")).all(),
            connection.execute(text("SELECT * FROM enrollment_events ORDER BY id")).all(),
        )


def main() -> None:
    with isolated_database() as (engine, schema):
        baseline = snapshot(engine)
        # Inject the error only into this disposable schema, on the real POST path.
        with engine.begin() as connection:
            connection.execute(text("""
                CREATE FUNCTION fail_audit_for_test() RETURNS trigger AS $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM enrollments
                        WHERE student_id = NEW.student_id
                          AND class_section_id = NEW.class_section_id
                    ) THEN
                        RAISE EXCEPTION 'Enrollment must be inserted before audit';
                    END IF;
                    NEW.event_type := 'INVALID';
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                CREATE TRIGGER fail_audit_for_test
                BEFORE INSERT ON enrollment_events
                FOR EACH ROW EXECUTE FUNCTION fail_audit_for_test();
            """))
        with running_api(schema) as base:
            payload = {"student_id": "22000004", "class_section_id": "RACE-01"}
            response = requests.post(f"{base}/enrollments", json=payload, timeout=5)
            assert response.status_code == 409, response.text
            assert snapshot(engine) == baseline, "Enrollment/audit data leaked after rollback"
            print("PASS: invalid audit after enrollment INSERT returns 409; both tables unchanged.")

            with engine.begin() as connection:
                connection.execute(text("DROP TRIGGER fail_audit_for_test ON enrollment_events"))
                connection.execute(text("DROP FUNCTION fail_audit_for_test()"))
            response = requests.post(f"{base}/enrollments", json=payload, timeout=5)
            assert response.status_code == 201, response.text
            enrollments, events = snapshot(engine)
            assert len(enrollments) == len(baseline[0]) + 1
            assert len(events) == len(baseline[1]) + 1
            assert events[-1].event_type == "CREATED"
            response = requests.delete(f"{base}/enrollments/22000004/RACE-01", timeout=5)
            assert response.status_code == 204, response.text
            enrollments, events = snapshot(engine)
            assert enrollments == baseline[0]
            assert [row.event_type for row in events] == ["CREATED", "CANCELLED"]
            response = requests.delete(f"{base}/enrollments/22000004/RACE-01", timeout=5)
            assert response.status_code == 404
            assert snapshot(engine) == (enrollments, events)
            print("PASS: normal POST commits enrollment + CREATED; DELETE records CANCELLED; repeated DELETE is 404.")
    # PostgreSQL sequences may advance on rollback, so IDs need not be contiguous.


if __name__ == "__main__":
    main()
