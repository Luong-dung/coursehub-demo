from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import DataError
from psycopg.errors import DuplicateColumn

from backend.tests.support import execute_file, isolated_database

UP = "database/migrations/002_add_enrollment_event_note.sql"
DOWN = "database/migrations/002_add_enrollment_event_note_rollback.sql"
OLD_COLUMNS = "id, student_id, class_section_id, event_type, source, dataset, occurred_at"


def migrate(engine, path: str) -> None:
    connection = engine.raw_connection()
    try:
        execute_file(connection, path)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def rows(engine):
    with engine.connect() as connection:
        return connection.execute(text(f"SELECT {OLD_COLUMNS} FROM enrollment_events ORDER BY id")).all()


def main() -> None:
    with isolated_database() as (engine, _):
        with engine.begin() as connection:
            connection.execute(text("""
                INSERT INTO enrollment_events (student_id, class_section_id, event_type)
                VALUES ('22000001', 'WEB-01', 'CREATED'),
                       ('22000002', 'WEB-01', 'CREATED'),
                       ('22000001', 'WEB-01', 'CANCELLED')
            """))
        before = rows(engine)
        migrate(engine, UP)
        assert rows(engine) == before
        with engine.begin() as connection:
            assert connection.execute(text("SELECT COUNT(*) FROM enrollment_events WHERE note IS NULL")).scalar_one() == 3
            assert connection.execute(text("SELECT COUNT(*) FROM schema_migrations WHERE version='002'")).scalar_one() == 1
            connection.execute(text("UPDATE enrollment_events SET note=:note WHERE id=1"), {"note": "a" * 200})
        try:
            with engine.begin() as connection:
                connection.execute(text("UPDATE enrollment_events SET note=:note WHERE id=1"), {"note": "a" * 201})
        except DataError as exc:
            assert exc.orig.sqlstate == "22001", exc
        else:
            raise AssertionError("201-character note must fail")
        try:
            migrate(engine, UP)
        except DuplicateColumn:
            pass
        else:
            raise AssertionError("Applying migration twice must fail atomically")
        with engine.connect() as connection:
            assert connection.execute(text("SELECT length(note) FROM enrollment_events WHERE id=1")).scalar_one() == 200
            assert connection.execute(text("SELECT COUNT(*) FROM schema_migrations WHERE version='002'")).scalar_one() == 1
        print("PASS: 002 preserves all 3 old events, notes initially NULL; 200 accepted, 201 rejected; duplicate migration rejected.")

        migrate(engine, DOWN)
        assert rows(engine) == before
        with engine.connect() as connection:
            assert connection.execute(text("""
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = 'enrollment_events' AND column_name = 'note'
            """)).scalar_one() == 0
            assert connection.execute(text("SELECT version FROM schema_migrations ORDER BY version")).scalars().all() == ["001"]
        migrate(engine, UP)
        assert rows(engine) == before
        with engine.connect() as connection:
            assert connection.execute(text("SELECT COUNT(*) FROM enrollment_events WHERE note IS NULL")).scalar_one() == 3
        print("PASS: rollback preserves old columns/rows but removes note values; reapply succeeds with NULL notes.")


if __name__ == "__main__":
    main()
