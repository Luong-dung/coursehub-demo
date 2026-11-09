from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import DataError, ProgrammingError

from backend.tests.support import ROOT, execute_file, isolated_database


def main(output: Path | None = None) -> None:
    notes = ["# Bai 3 - Actual query plans", ""]
    with isolated_database() as (engine, _):
        raw = engine.raw_connection()
        try:
            execute_file(raw, "database/11_generate_performance_events.sql")
            # Keep the first business index, so this comparison measures the extra index.
            with raw.cursor() as cursor:
                cursor.execute("""
                    CREATE INDEX idx_enrollment_events_dataset_student_time
                    ON enrollment_events (dataset, student_id, occurred_at DESC)
                """)
            raw.commit()
        finally:
            raw.close()

        params = {
            "dataset": "performance", "section": "WEB-01", "type": "CANCELLED",
            "start": datetime(2025, 12, 20), "end": datetime(2026, 1, 1),
        }
        query = """
            SELECT COUNT(*) AS event_count FROM enrollment_events
            WHERE dataset = :dataset AND class_section_id = :section
                AND event_type = :type
                AND occurred_at >= :start AND occurred_at < :end
        """
        # Independent expected value for the deterministic generator, not another SQL COUNT.
        first_day = (params["start"] - datetime(2025, 1, 1)).days
        expected = sum(g % 4 == 0 and g % 5 == 0 and g % 365 >= first_day
                       for g in range(1, 100001))
        statements = [part.strip() for part in
                      (ROOT / "database/13_section_event_index.sql").read_text().split(";")
                      if part.strip()]
        with engine.connect() as connection:
            assert connection.execute(text(query), params).scalar_one() == expected
            assert connection.execute(text(query), params | {"section": "NO-CLASS"}).scalar_one() == 0
            assert connection.execute(text(query), params | {"type": "' OR '1'='1"}).scalar_one() == 0
            for label, statement in (("Before", statements[0]), ("After", statements[3])):
                if label == "After":
                    connection.exec_driver_sql(statements[1])
                    connection.exec_driver_sql(statements[2])
                    connection.commit()
                assert connection.execute(text(query), params).scalar_one() == expected
                for run in range(1, 4):
                    plan = "\n".join(connection.exec_driver_sql(statement).scalars())
                    notes += [f"## {label}, run {run}", "", "```text", plan, "```", ""]
                    print(label, run, next(line for line in plan.splitlines()
                                          if line.startswith("Execution Time")))
            connection.rollback()
            try:
                connection.execute(text(query), params | {"start": "not-a-timestamp"})
            except DataError:
                connection.rollback()
            else:
                raise AssertionError("Invalid timestamp must fail")
            try:
                connection.exec_driver_sql(statements[1])
            except ProgrammingError as exc:
                assert exc.orig.sqlstate == "42P07", exc
                connection.rollback()
            else:
                raise AssertionError("Duplicate index must not silently create another index")
            assert connection.execute(text(query), params).scalar_one() == expected
        notes += [f"Expected and actual event_count: {expected}.", "",
                  "PASS: count unchanged, empty/literal input = 0, invalid timestamp rejected, duplicate index rejected.",
                  "CLEANUP PASS: disposable schema removed; original tables/indexes untouched."]
        print(f"PASS: count={expected}; before/after results match; empty and invalid cases checked.")
    if output is not None:
        output.write_text("\n".join(notes) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    main(parser.parse_args().output)
