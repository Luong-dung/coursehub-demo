"""Run integration checks in a disposable PostgreSQL schema, never public."""
from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from uuid import uuid4

import requests
from psycopg import sql
from sqlalchemy import create_engine

from backend.app.database import engine

ROOT = Path(__file__).resolve().parents[2]


def execute_file(connection, path: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute((ROOT / path).read_text(encoding="utf-8-sig"))
        while cursor.nextset():
            pass


@contextmanager
def isolated_database():
    schema = "coursehub_test_" + uuid4().hex
    admin = engine.raw_connection()
    test_engine = None
    created = False
    try:
        with admin.cursor() as cursor:
            cursor.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        admin.commit()
        created = True
        test_engine = create_engine(
            engine.url, connect_args={"options": f"-c search_path={schema}"}
        )
        connection = test_engine.raw_connection()
        try:
            for path in (
                "database/01_schema.sql",
                "database/02_seed.sql",
                "database/04_views.sql",
                "database/migrations/001_add_enrollment_events.sql",
                "database/08_week04_demo_setup.sql",
            ):
                execute_file(connection, path)
            connection.commit()
        finally:
            connection.close()
        yield test_engine, schema
    finally:
        if test_engine is not None:
            test_engine.dispose()
        if created:
            admin.rollback()
            with admin.cursor() as cursor:
                cursor.execute(
                    sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema))
                )
            admin.commit()
            with admin.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM pg_namespace WHERE nspname=%s", (schema,))
                assert cursor.fetchone()[0] == 0
            print("CLEANUP PASS: disposable schema removed; original tables untouched.")
        admin.close()


@contextmanager
def running_api(schema: str):
    assert schema.startswith("coursehub_test_")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = os.environ.copy()
    env["PGOPTIONS"] = f"-c search_path={schema}"
    env["PYTHONUTF8"] = "1"
    with tempfile.TemporaryFile(mode="w+b") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--port", str(port)],
            cwd=ROOT, env=env, stdout=log, stderr=log,
        )
        try:
            base_url = f"http://127.0.0.1:{port}"
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                try:
                    requests.get(f"{base_url}/health", timeout=1).raise_for_status()
                    break
                except requests.RequestException:
                    if process.poll() is not None:
                        log.seek(0)
                        raise RuntimeError(log.read().decode("utf-8", errors="replace"))
                    time.sleep(0.1)
            else:
                raise RuntimeError("API startup timeout")
            yield base_url
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == "__main__":
    # Optional interactive sandbox for the read-only Postman collection.
    with isolated_database() as (test_engine, schema):
        from sqlalchemy import text

        with test_engine.begin() as connection:
            connection.execute(text("""
                INSERT INTO enrollment_events (student_id, class_section_id, event_type)
                VALUES ('22000001', 'WEB-01', 'CREATED')
            """))
        with running_api(schema) as base_url:
            print(f"Postman base_url = {base_url}; history_student_id = 22000001", flush=True)
            input("Press Enter after Postman checks to remove all test data: ")
