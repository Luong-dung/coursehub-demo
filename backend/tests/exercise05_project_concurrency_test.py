from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import threading
import time

import requests
from sqlalchemy import text

from backend.tests.support import isolated_database, running_api

VERIFY_SQL = """
SELECT class_id, capacity, enrolled, remaining
FROM v_section_summary
WHERE class_id = 'RACE-01'
"""


def wait_for_blocked_requests(engine, schema: str, expected: int) -> None:
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        with engine.connect() as connection:
            count = connection.execute(text("""
                SELECT COUNT(*) FROM pg_stat_activity
                WHERE application_name = :schema
                  AND wait_event_type = 'Lock'
                  AND query LIKE '%class_sections%'
            """), {"schema": schema}).scalar_one()
        if count >= expected:
            return
        time.sleep(0.02)
    raise AssertionError(f"Expected {expected} API requests blocked on class row")


def main(output: Path | None = None) -> None:
    log = []

    def report(message):
        print(message, flush=True)
        log.append(message)

    with isolated_database() as (engine, schema):
        with running_api(schema) as base:
            def post(student_id):
                return requests.post(f"{base}/enrollments", json={
                    "student_id": student_id, "class_section_id": "RACE-01",
                }, timeout=20)

            def patch(capacity):
                return requests.patch(f"{base}/sections/RACE-01/capacity",
                                      json={"capacity": capacity}, timeout=20)

            def state():
                with engine.connect() as connection:
                    return dict(connection.execute(text(VERIFY_SQL)).mappings().one())

            barrier = threading.Barrier(2)

            def enroll_together(student_id):
                barrier.wait(timeout=5)
                return post(student_id)

            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(enroll_together, student)
                           for student in ("22000002", "22000004")]
                responses = [future.result() for future in futures]
            assert sorted(response.status_code for response in responses) == [201, 409]
            assert state() == {"class_id": "RACE-01", "capacity": 1, "enrolled": 1, "remaining": 0}
            winner = next(response.json()["student_id"] for response in responses
                          if response.status_code == 201)
            with engine.connect() as connection:
                assert connection.execute(text("SELECT COUNT(*) FROM enrollment_events WHERE class_section_id='RACE-01'")).scalar_one() == 1
            assert post(winner).status_code == 409
            assert post("99999999").status_code == 404
            assert patch(0).status_code == 422
            assert requests.patch(f"{base}/sections/NO-CLASS/capacity",
                                  json={"capacity": 1}, timeout=5).status_code == 404
            with engine.connect() as connection:
                assert connection.execute(text("SELECT COUNT(*) FROM enrollment_events WHERE class_section_id='RACE-01'")).scalar_one() == 1
            report("PASS POST/POST: statuses=[201,409]; capacity=1, enrolled=1, remaining=0; one CREATED event.")
            report("PASS error cases: duplicate=409, missing student/class=404, invalid capacity=422; no extra registration/audit.")

            # Retain the winning registration, expand capacity to 2, then queue
            # a real POST before PATCH behind a separate row-lock gate connection.
            assert patch(2).status_code == 200
            loser = "22000004" if winner == "22000002" else "22000002"
            gate = engine.connect()
            try:
                gate.execute(text("SELECT id FROM class_sections WHERE id='RACE-01' FOR UPDATE"))
                with ThreadPoolExecutor(max_workers=2) as pool:
                    try:
                        post_future = pool.submit(post, loser)
                        wait_for_blocked_requests(engine, schema, 1)
                        patch_future = pool.submit(patch, 1)
                        wait_for_blocked_requests(engine, schema, 2)
                    finally:
                        # Always release the gate before executor waits for workers.
                        gate.rollback()
                    post_response = post_future.result()
                    patch_response = patch_future.result()
            finally:
                gate.close()
            assert post_response.status_code == 201, post_response.text
            assert patch_response.status_code == 409, patch_response.text
            assert state() == {"class_id": "RACE-01", "capacity": 2, "enrolled": 2, "remaining": 0}
            report("PASS ordered POST/PATCH: database confirms both waiting; POST=201, PATCH=409; capacity=2, enrolled=2.")

            # Opposite serialization: capacity is reduced first, so POST must fail.
            deleted = requests.delete(f"{base}/enrollments/{loser}/RACE-01", timeout=5)
            assert deleted.status_code == 204
            assert patch(1).status_code == 200
            assert post(loser).status_code == 409
            report("PASS PATCH-first: PATCH=200, POST=409; enrolled never exceeds capacity.")
            final_state = state()
            assert final_state["enrolled"] == 1 and final_state["remaining"] == 0
            with engine.connect() as connection:
                events = connection.execute(text("""
                    SELECT event_type, COUNT(*) AS total FROM enrollment_events
                    WHERE class_section_id='RACE-01' GROUP BY event_type ORDER BY event_type
                """)).all()
            assert dict(events) == {"CANCELLED": 1, "CREATED": 2}
            report(f"FINAL STATE: {final_state}")
            report(f"AUDIT: {dict(events)}")
    report("CLEANUP PASS: schema removed, all fixture data/locks/indexes removed, original tables untouched.")
    if output is not None:
        output.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    main(parser.parse_args().output)
