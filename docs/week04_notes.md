# CourseHub - Buoi 4

- Migration 001: enrollment_events.
- Demo class: RACE-01, capacity = 1.
- POST /enrollments: lock class_sections bang FOR UPDATE.
- DELETE /enrollments: cung thu tu lock, ghi CANCELLED trong transaction.
- Concurrency test: 1 request 201, 1 request 409.
- Performance data: 100000 rows, dataset=performance.
- Index: idx_enrollment_events_dataset_student_time.

| Phuong an | Scan type | Execution Time (3 lan) |
|---|---|---|
| Truoc index | Seq Scan + Sort | 5.056 / 5.242 / 4.957 ms |
| Sau index | Index Scan | 0.162 / 0.056 / 0.049 ms |

## Huong dan review tren database thu

1. Cai thu vien bang `python -m pip install -r backend/requirements.txt`.
2. Tao `backend/.env` tu `.env.example`, dien cau hinh database thu; khong commit `.env`.
3. Tren schema Buoi 3, chay migration `001_add_enrollment_events.sql` mot lan, roi chay `08_week04_demo_setup.sql`.
4. Chay API va concurrency test theo lenh ben duoi; doi chieu 201/409 va enrolled=1.
5. Chay `11_generate_performance_events.sql`, sau do tung phan cua `12_explain_and_index.sql`; luu plan truoc khi tao index.
6. Doc rollback truoc khi dung: rollback xoa bang enrollment_events va lich su su kien. Khong chay tren database can giu lich su.

## Concurrent requests

```text
22000002: 409 - Lop hoc phan da het cho
22000004: 201 - Dang ky thanh cong
PASS: enrolled = 1, remaining = 0, capacity = 1
```

## Before index - run 1

```text
Limit  (cost=2914.49..2914.61 rows=50 width=39) (actual time=5.039..5.043 rows=50.00 loops=1)
  Buffers: shared hit=1137
  ->  Sort  (cost=2914.49..2916.56 rows=827 width=39) (actual time=5.038..5.040 rows=50.00 loops=1)
        Sort Key: occurred_at DESC
        Sort Method: top-N heapsort  Memory: 31kB
        Buffers: shared hit=1137
        ->  Seq Scan on enrollment_events  (cost=0.00..2887.02 rows=827 width=39) (actual time=0.036..4.930 rows=820.00 loops=1)
              Filter: ((occurred_at >= '2025-12-20 00:00:00'::timestamp without time zone) AND ((dataset)::text = 'performance'::text) AND ((student_id)::text = '22000001'::text))
              Rows Removed by Filter: 99181
              Buffers: shared hit=1137
Planning:
  Buffers: shared hit=30 read=1
Planning Time: 0.745 ms
Execution Time: 5.056 ms
```

## Before index - run 2

```text
Limit  (cost=2914.49..2914.61 rows=50 width=39) (actual time=5.226..5.230 rows=50.00 loops=1)
  Buffers: shared hit=1137
  ->  Sort  (cost=2914.49..2916.56 rows=827 width=39) (actual time=5.225..5.227 rows=50.00 loops=1)
        Sort Key: occurred_at DESC
        Sort Method: top-N heapsort  Memory: 31kB
        Buffers: shared hit=1137
        ->  Seq Scan on enrollment_events  (cost=0.00..2887.02 rows=827 width=39) (actual time=0.023..5.117 rows=820.00 loops=1)
              Filter: ((occurred_at >= '2025-12-20 00:00:00'::timestamp without time zone) AND ((dataset)::text = 'performance'::text) AND ((student_id)::text = '22000001'::text))
              Rows Removed by Filter: 99181
              Buffers: shared hit=1137
Planning Time: 0.049 ms
Execution Time: 5.242 ms
```

## Before index - run 3

```text
Limit  (cost=2914.49..2914.61 rows=50 width=39) (actual time=4.940..4.945 rows=50.00 loops=1)
  Buffers: shared hit=1137
  ->  Sort  (cost=2914.49..2916.56 rows=827 width=39) (actual time=4.940..4.942 rows=50.00 loops=1)
        Sort Key: occurred_at DESC
        Sort Method: top-N heapsort  Memory: 31kB
        Buffers: shared hit=1137
        ->  Seq Scan on enrollment_events  (cost=0.00..2887.02 rows=827 width=39) (actual time=0.025..4.837 rows=820.00 loops=1)
              Filter: ((occurred_at >= '2025-12-20 00:00:00'::timestamp without time zone) AND ((dataset)::text = 'performance'::text) AND ((student_id)::text = '22000001'::text))
              Rows Removed by Filter: 99181
              Buffers: shared hit=1137
Planning Time: 0.063 ms
Execution Time: 4.957 ms
```

## After index - run 1

```text
Limit  (cost=0.42..67.50 rows=50 width=39) (actual time=0.115..0.150 rows=50.00 loops=1)
  Buffers: shared hit=50 read=3
  ->  Index Scan using idx_enrollment_events_dataset_student_time on enrollment_events  (cost=0.42..1117.97 rows=833 width=39) (actual time=0.114..0.146 rows=50.00 loops=1)
        Index Cond: (((dataset)::text = 'performance'::text) AND ((student_id)::text = '22000001'::text) AND (occurred_at >= '2025-12-20 00:00:00'::timestamp without time zone))
        Index Searches: 1
        Buffers: shared hit=50 read=3
Planning:
  Buffers: shared hit=20 read=1
Planning Time: 0.160 ms
Execution Time: 0.162 ms
```

## After index - run 2

```text
Limit  (cost=0.42..67.50 rows=50 width=39) (actual time=0.023..0.047 rows=50.00 loops=1)
  Buffers: shared hit=53
  ->  Index Scan using idx_enrollment_events_dataset_student_time on enrollment_events  (cost=0.42..1117.97 rows=833 width=39) (actual time=0.022..0.044 rows=50.00 loops=1)
        Index Cond: (((dataset)::text = 'performance'::text) AND ((student_id)::text = '22000001'::text) AND (occurred_at >= '2025-12-20 00:00:00'::timestamp without time zone))
        Index Searches: 1
        Buffers: shared hit=53
Planning Time: 0.050 ms
Execution Time: 0.056 ms
```

## After index - run 3

```text
Limit  (cost=0.42..67.50 rows=50 width=39) (actual time=0.023..0.041 rows=50.00 loops=1)
  Buffers: shared hit=53
  ->  Index Scan using idx_enrollment_events_dataset_student_time on enrollment_events  (cost=0.42..1117.97 rows=833 width=39) (actual time=0.022..0.038 rows=50.00 loops=1)
        Index Cond: (((dataset)::text = 'performance'::text) AND ((student_id)::text = '22000001'::text) AND (occurred_at >= '2025-12-20 00:00:00'::timestamp without time zone))
        Index Searches: 1
        Buffers: shared hit=53
Planning Time: 0.050 ms
Execution Time: 0.049 ms
```

## Special search input

GET /courses with q = `%' OR '1'='1'--` returned HTTP 200 and `[]`. The endpoint uses the bind parameter `:keyword`; no unsafe SQL example was added.

## Run again

```powershell
python -m uvicorn backend.app.main:app --reload
# In another terminal:
python backend/tests/week04_concurrency_test.py
```

RACE-01 currently has one enrollment. Run database/08_week04_demo_setup.sql to reset it. The performance dataset contains 100,000 generated events, not real enrollment history. Plans above include scan type, rows, buffers and execution time. Cache and machine load affect timing; the planner was not forced to use the index. The index now exists; inspect pg_indexes before repeating the before/after experiment.

To remove only generated events when needed:

```sql
DELETE FROM enrollment_events WHERE dataset = 'performance';
ANALYZE enrollment_events;
```
