# Bai 4 - Migration 002

Issue: #6. Branch: `exercise04-migration002`, base: `exercise03-section-event-index`.
Thuc hien: Luong-dung. Kiem tra de nghi: doanh9a246-afk (cho review).

Migration 002 them `note VARCHAR(200)` nullable vao enrollment_events. Cot tuy chon de
bo sung ly do/ghi chu nghiep vu sau nay; khong thay doi hop dong API hien tai.
Du lieu cu co note=NULL, cac cot cu va ID giu nguyen. Khong can gia tri mac dinh gia lap.

Chay `database/migrations/002_add_enrollment_event_note.sql` mot lan sau 001, tren database thu
da co du lieu. Transaction bao gom ALTER va schema_migrations: neu loi thi rollback ca hai.
Khong sua migration 001 da duoc ap dung. Duplicate migration bao loi thay vi che giau trang thai.

Rollback: `database/migrations/002_add_enrollment_event_note_rollback.sql`.
**Co mat du lieu:** moi gia tri note bi xoa vinh vien khi DROP COLUMN. Cac su kien, ID va cot cu
khong mat. Sao luu note theo event ID neu can giu truoc rollback. Chay UP lai khong phuc hoi note.

```powershell
python -m backend.tests.exercise04_migration_test
```

Test tao 3 events truoc migration trong schema rieng, so sanh toan bo cot cu truoc/sau,
xac nhan version002, NULL, ghi 200 ky tu, loi 201 ky tu va chay UP trung.
DOWN phai giu events/cot cu va chi con version001; UP lai thanh cong voi NULL notes.
finally xoa schema thu: schema chinh va migration version tren schema chinh khong doi.

## Ket qua thuc te

```text
PASS: 002 preserves all 3 old events, notes initially NULL; 200 accepted, 201 rejected; duplicate migration rejected.
PASS: rollback preserves old columns/rows but removes note values; reapply succeeds with NULL notes.
CLEANUP PASS: disposable schema removed; original tables untouched.
```
