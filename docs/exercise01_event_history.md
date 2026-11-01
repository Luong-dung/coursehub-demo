# Bai 1 - API doc lich su dang ky

Issue: #3. Branch: `exercise01-event-history`.
Nguoi thuc hien: Luong-dung. Nguoi kiem tra de nghi: doanh9a246-afk (cho review).

`GET /enrollment-events`: student_id (8 ky tu), event_type (CREATED/CANCELLED)
la bo loc tuy chon; skip >= 0, limit tu 1 den 100 (mac dinh 10).
Thu tu `occurred_at DESC, id DESC` on dinh khi trung timestamp.
Gia tri bo loc va phan trang dung bind parameter. Khong co du lieu tra `200 []`.
Pagination on dinh voi cung tap du lieu; offset khong dam bao snapshot khi co insert dong thoi.

## Kiem thu tu dong

```powershell
python -m backend.tests.exercise01_event_history_test
```

Ket qua thuc te:

```text
PASS: history filters, empty data, stable ties/pagination, bounds and bind parameters.
CLEANUP PASS: disposable schema removed; original tables untouched.
```

Test tao schema PostgreSQL rieng, seed 3 events (2 events trung timestamp),
chay API o port rieng, xac nhan thu tu ID 3,2,1 va phan trang, tung bo loc/ket hop,
empty, limit=100, limit=0/101, skip=-1, enum sai, student ID sai va input injection.
API dung search_path chi schema thu; finally dung API va xoa schema ke ca assert loi.
Khong sua du lieu/schema chinh. Tai khoan database can quyen CREATE SCHEMA trong database thu.

## Postman: co du lieu, rong va loi

```powershell
python -m backend.tests.support
```

Import `postman/CourseHub_Enrollment_Events.postman_collection.json`.
Dat `base_url` theo URL terminal in ra (port ngau nhien); neu co Postman environment,
cap nhat bien cung ten vi environment uu tien hon collection. Dat history_student_id=22000001.
Chay 4 requests: co du lieu, khong du lieu, limit sai, event_type sai.
Nhan Enter o terminal de dung API va xoa du lieu thu. Khong chay collection tren production
de suy dien "khong co du lieu" neu 99999999 thuc su la sinh vien da co lich su.

## Thu tu PR

PR Bai 1 dua tren `week04-transaction-index` (PR #2), vi API can migration 001.
Merge PR nen truoc roi moi merge PR nay; khong commit `.env` hay dump du lieu.
