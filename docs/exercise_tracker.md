# Bai tap tu thuc hanh - theo doi

Moi bai co nhánh/Issue/PR rieng; PR xep chong de tai su dung test support.
Khong merge tu dong, khong xoa nhanh khi chua review/merge.

| Bai | Issue | Branch | PR | Base |
|---|---|---|---|---|
| 1 - API lich su | #3 | exercise01-event-history | #8 | week04-transaction-index |
| 2 - Rollback | #4 | exercise02-rollback | #9 | exercise01-event-history |
| 3 - Index theo lop | #5 | exercise03-section-event-index | #10 | exercise02-rollback |
| 4 - Migration 002 | #6 | exercise04-migration002 | #11 | exercise03-section-event-index |
| 5 - Project concurrency | #7 | exercise05-project-concurrency | #12 | exercise04-migration002 |

Repo: https://github.com/Luong-dung/coursehub-demo
Nguoi thuc hien: Luong-dung; nguoi kiem tra de nghi: doanh9a246-afk.
Nguoi review can doc log va chay lai cac ca dung/loi tren database thu, khong chi ghi OK.
Yeu cau PostgreSQL dang chay, backend/.env da cau hinh va quyen CREATE SCHEMA trong database thu.

```powershell
python -m pip install -r backend/requirements.txt
python -m backend.tests.exercise01_event_history_test
python -m backend.tests.exercise02_rollback_test
python -m backend.tests.exercise03_index_test
python -m backend.tests.exercise04_migration_test
python -m backend.tests.exercise05_project_concurrency_test
```

Moi lenh tao schema rieng, chay SQL/test va xoa schema trong finally. Khong can Uvicorn
ben ngoai cho cac test API; moi test tu chay server tren port rieng. Test scripts dung assert,
khong chay voi `python -O`. Khong commit `.env`, `.venv`, dump hay du lieu lon.
Du lieu chinh va cac migration/index tren schema chinh khong bi thay doi boi test.

Thu tu merge de nghi: PR #2 (Buoi 4) -> #8 -> #9 -> #10 -> #11 -> #12.
Sau moi base merge, kiem tra/doi base PR ke tiep ve main neu GitHub chua tu cap nhat.
`Closes #n` chi dong Issue khi thay doi vao default branch; PR nham nhanh base chua dong Issue ngay.

Gioi han: Bai 5 dang dung CourseHub theo repo hien tai, chua nhan thong tin Project khac.
Migration 002 va index Bai 3 moi duoc chay tren schema thu co du lieu, chua trien khai schema chinh.
