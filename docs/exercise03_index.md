# Bai 3 - Chi muc theo thong ke huy dang ky cua lop

Issue: #5. Branch: `exercise03-section-event-index`, base: `exercise02-rollback`.
Thuc hien: Luong-dung. Kiem tra de nghi: doanh9a246-afk (cho review).

Nghiep vu: dem so su kien huy dang ky cua mot lop trong khoang [tu ngay, den ngay).
Du lieu do: 100000 su kien mo phong, dataset=performance; khong phai so lieu nha truong.
Query, EXPLAIN va CREATE INDEX: `database/13_section_event_index.sql`.

Thu tu cot `(dataset, class_section_id, event_type, occurred_at)`:

- Ba cot dau la dieu kien bang nhau, thu hep dung bo du lieu/lop/loai su kien.
- Cot thoi gian cuoi de gioi han khoang, tranh quet tat ca su kien cua lop.
- Index theo student_id tu Buoi 4 van duoc giu khi do; no khong thay the duoc index theo lop.
- Khong tao index tung cot. Index nay ton dung luong va chi phi ghi; chi trien khai khi
  thong ke nay duoc dung thuong xuyen. Khong ep planner bang enable_seqscan=off.

```powershell
python -m backend.tests.exercise03_index_test --output docs/exercise03_plan_results.md
```

Test dung schema rieng va generator hien co, do 3 lan moi phuong an, luu full plan,
buffers, scan type va Execution Time vao file ket qua. So dem duoc doi chieu voi cong thuc
generator tinh doc lap bang Python. Co ca rong, input literal dac biet, timestamp sai va
tao index trung (phai bao loi, khong tao index ban sao).

finally xoa schema thu va ca hai index; khong xoa hay them index tren schema chinh.
Khi trien khai thu cong tren database thu, chay tung phan SQL va luu plan truoc CREATE INDEX.
Neu index da ton tai thi khong goi ket qua dau la "truoc index"; kiem tra pg_indexes truoc.
Cache/tải may anh huong so do, khong suy dien mot ty le tang toc cho moi he thong.
