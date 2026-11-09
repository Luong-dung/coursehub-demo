# Bai 2 - Rollback nhieu bang

Issue: #4. Branch: `exercise02-rollback`, base: `exercise01-event-history`.
Thuc hien: Luong-dung. Kiem tra de nghi: doanh9a246-afk (cho review).

```powershell
python -m backend.tests.exercise02_rollback_test
```

Test dung POST that cua production app tren schema thu rieng. Trigger chi trong schema thu
xac nhan enrollments da duoc INSERT, sau do doi event_type thanh INVALID de vi pham CHECK
ck_enrollment_events_type. POST tra 409; snapshot day du cua hai bang truoc/sau phai bang nhau.
Khong them endpoint demo vao main.py, khong cai trigger tren schema chinh.

Sau khi go trigger, ca dung POST phai commit ca enrollment va CREATED; DELETE phai xoa
enrollment va ghi CANCELLED. DELETE lan hai tra 404 va khong them su kien.
Schema thu (bao gom trigger, function, bang va sequence) duoc xoa trong finally.
Sequence ID co the tang du transaction rollback; khong nham khoang trong ID voi mat du lieu.

## Log thuc te

```text
PASS: invalid audit after enrollment INSERT returns 409; both tables unchanged.
PASS: normal POST commits enrollment + CREATED; DELETE records CANCELLED; repeated DELETE is 404.
CLEANUP PASS: disposable schema removed; original tables untouched.
```
