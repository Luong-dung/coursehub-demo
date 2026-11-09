# Bai 5 - Ho so Project CourseHub

Issue: #7. Branch: `exercise05-project-concurrency`, base: `exercise04-migration002`.

Pham vi dang ap dung la Project CourseHub trong repository nay: quan ly hoc phan,
lop hoc phan va dang ky cua sinh vien. Chua nhan thong tin ve mot Project khac,
nen day la lua chon theo repo hien tai, can nhom xac nhan khi review.
Khong gan test cua CourseHub cho mot Project nghiep vu khac.

## Phan cong

| Hang muc | Nguoi thuc hien | Nguoi kiem tra de nghi | Bang chung |
|---|---|---|---|
| Transaction dang ky/huy va audit | Luong-dung | doanh9a246-afk | main.py; test rollback Bai 2 |
| Phan tich race va khoa lop | Luong-dung | doanh9a246-afk | test POST/POST va POST/PATCH ben duoi |
| Migration dau tien | Luong-dung | doanh9a246-afk | 001_add_enrollment_events.sql + rollback |
| Truy van va du lieu do | Luong-dung | doanh9a246-afk | Bai 3; 100000 su kien, full plans |
| Migration ghi chu | Luong-dung | doanh9a246-afk | Bai 4; UP/DOWN tren du lieu co san |
| Test, log va khoi phuc du lieu | Luong-dung | doanh9a246-afk | exercise05_concurrency_results.txt |

Nguoi kiem tra la de nghi/yeu cau review, khong phai khang dinh da review hay da chap thuan.
Moi hang muc co Issue va PR; xem bang lien ket trong exercise_tracker.md.

## Transaction cot loi va bat bien

Dang ky mot lop: xac nhan sinh vien -> khoa dong lop -> kiem tra trung -> dem dang ky
-> kiem tra enrolled < capacity -> INSERT enrollments -> INSERT CREATED -> COMMIT.
Neu ghi audit loi, engine.begin rollback ca hai bang (Bai 2 test truc tiep qua POST that).

Huy dang ky: khoa cung dong lop -> DELETE ... RETURNING -> neu khong co thi 404
-> INSERT CANCELLED -> COMMIT. Huy lan hai khong tao them su kien.
Thay doi suc chua: khoa lop -> dem lai trong SELECT rieng -> tu choi neu capacity < enrolled
-> UPDATE -> COMMIT. Ca ba thao tac giu khoa den COMMIT/ROLLBACK.

Bat bien: capacity > 0, 0 <= enrolled <= capacity; moi cap student/lop chi mot dang ky;
ca thanh cong co audit tuong ung, ca that bai khong de lai dang ky/audit do dang.
Audit la lich su su kien, khong dem audit de tinh so dang ky hien tai.

## Rui ro dong thoi va tai nguyen khoa

- Hai POST cung thay cho trong: khoa `class_sections.id` truoc COUNT ngan vuot suc chua.
- Hai POST cung student/lop: row lock + duplicate check + primary key ngan trung.
- POST va PATCH: chi khoa o lenh UPDATE la qua muon; PATCH can khoa truoc COUNT.
  Bai nay sua loi do trong code that cua repo, khong chi viet vi du SQL doc lap.
- POST va DELETE: cung khoa lop, DELETE tra RETURNING va chi ghi audit neu that su xoa.
- Thu tu: khoa lop truoc thay doi enrollments/audit, moi request hien tai chi sua mot lop.
  Neu sau nay dang ky nhieu lop trong mot transaction, khoa cac ID theo thu tu tang de tranh deadlock.
- Gia dinh PostgreSQL READ COMMITTED mac dinh, khong co writer bo qua quy uoc khoa nay.
  SQL thu cong/generator khong duoc dung de thay doi enrollments nghiep vu trong production.
  Neu doi isolation level thi can danh gia lai retry serialization, khong suy dien tu test nay.

## Migration va truy van

Migration dau tien la 001: them audit events va schema_migrations, constraint event_type/dataset,
foreign key den student va lop. UP chay mot lan; DOWN xoa lich su audit, can sao luu truoc.
002 them note nullable, giu cot cu, DOWN mat gia tri note (chi tiet Bai 4).

Truy van can do: so su kien CANCELLED cua mot lop trong khoang ngay, dataset tach rieng.
Do tren 100000 events de thay chi phi truy cap, khong dua dump len Git.
Index `(dataset, class_section_id, event_type, occurred_at)` theo dieu kien bang nhau truoc
khoang thoi gian. So lieu mo phong nay dung de hoc; khong khang dinh la quy mo production.
Ket qua/count=138 va full plans trong exercise03_plan_results.md.

## Test hai worker va log

```powershell
python -m backend.tests.exercise05_project_concurrency_test --output docs/exercise05_concurrency_results.txt
```

Test dung Uvicorn/POST/PATCH that tren schema rieng, hai worker ThreadPoolExecutor.
POST/POST dung Barrier, doi 201/409, enrolled=1 va dung mot CREATED event.
Ca loi: trung=409, thieu student/lop=404, capacity=0 la 422 va khong ghi audit.

Regression POST/PATCH dung ket noi thu ba lam gate giu FOR UPDATE:
POST vao doi truoc, kiem tra pg_stat_activity thay request bi chan, cho PATCH vao doi,
xac nhan ca hai request cho Lock, sau do nha gate. POST them sinh vien thu hai thanh cong;
PATCH phai dem lai va tu choi ha suc chua ve 1. Khong dua vao pg_sleep de doan thu tu.
Deadline chi de tranh treo test, khong dung thoi gian ngu lam bang chung da lay khoa.
Ca thu tu nguoc PATCH truoc, POST sau cung duoc kiem tra.

Ket noi kiem tra pg_stat_activity cung DB user voi API; API dung application_name rieng
cho schema test de khong nham request/server khac. Khong can quyen xem session cua user khac.

## Truy van xac nhan trang thai cuoi

```sql
SELECT class_id, capacity, enrolled, remaining
FROM v_section_summary
WHERE class_id = 'RACE-01';

SELECT event_type, COUNT(*) AS total
FROM enrollment_events
WHERE class_section_id = 'RACE-01'
GROUP BY event_type
ORDER BY event_type;
```

Ket qua trong schema thu truoc cleanup: capacity=1, enrolled=1, remaining=0;
CREATED=2, CANCELLED=1. Log that duoc luu trong exercise05_concurrency_results.txt.
finally dung API, nha gate va xoa schema cung moi fixture/index/sequence. Khong chay reset
hay xoa du lieu tren schema chinh. Loi assertion van cleanup; neu bi kill may/dien dot ngot,
kiem tra schema `coursehub_test_*` theo chu so huu truoc khi don thu cong.
