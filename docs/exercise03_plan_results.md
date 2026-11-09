# Bai 3 - Actual query plans

## Before, run 1

```text
Aggregate  (cost=1333.30..1333.31 rows=1 width=8) (actual time=1.135..1.136 rows=1.00 loops=1)
  Buffers: shared hit=346
  ->  Bitmap Heap Scan on enrollment_events  (cost=122.75..1332.90 rows=161 width=0) (actual time=0.433..1.123 rows=138.00 loops=1)
        Recheck Cond: (((dataset)::text = 'performance'::text) AND (occurred_at >= '2025-12-20 00:00:00'::timestamp without time zone) AND (occurred_at < '2026-01-01 00:00:00'::timestamp without time zone))
        Filter: (((class_section_id)::text = 'WEB-01'::text) AND ((event_type)::text = 'CANCELLED'::text))
        Rows Removed by Filter: 3141
        Heap Blocks: exact=308
        Buffers: shared hit=346
        ->  Bitmap Index Scan on idx_enrollment_events_dataset_student_time  (cost=0.00..122.71 rows=3251 width=0) (actual time=0.371..0.371 rows=3279.00 loops=1)
              Index Cond: (((dataset)::text = 'performance'::text) AND (occurred_at >= '2025-12-20 00:00:00'::timestamp without time zone) AND (occurred_at < '2026-01-01 00:00:00'::timestamp without time zone))
              Index Searches: 5
              Buffers: shared hit=38
Planning Time: 0.127 ms
Execution Time: 1.185 ms
```

## Before, run 2

```text
Aggregate  (cost=1333.30..1333.31 rows=1 width=8) (actual time=1.176..1.177 rows=1.00 loops=1)
  Buffers: shared hit=346
  ->  Bitmap Heap Scan on enrollment_events  (cost=122.75..1332.90 rows=161 width=0) (actual time=0.449..1.162 rows=138.00 loops=1)
        Recheck Cond: (((dataset)::text = 'performance'::text) AND (occurred_at >= '2025-12-20 00:00:00'::timestamp without time zone) AND (occurred_at < '2026-01-01 00:00:00'::timestamp without time zone))
        Filter: (((class_section_id)::text = 'WEB-01'::text) AND ((event_type)::text = 'CANCELLED'::text))
        Rows Removed by Filter: 3141
        Heap Blocks: exact=308
        Buffers: shared hit=346
        ->  Bitmap Index Scan on idx_enrollment_events_dataset_student_time  (cost=0.00..122.71 rows=3251 width=0) (actual time=0.382..0.382 rows=3279.00 loops=1)
              Index Cond: (((dataset)::text = 'performance'::text) AND (occurred_at >= '2025-12-20 00:00:00'::timestamp without time zone) AND (occurred_at < '2026-01-01 00:00:00'::timestamp without time zone))
              Index Searches: 5
              Buffers: shared hit=38
Planning Time: 0.143 ms
Execution Time: 1.210 ms
```

## Before, run 3

```text
Aggregate  (cost=1333.30..1333.31 rows=1 width=8) (actual time=1.109..1.109 rows=1.00 loops=1)
  Buffers: shared hit=346
  ->  Bitmap Heap Scan on enrollment_events  (cost=122.75..1332.90 rows=161 width=0) (actual time=0.417..1.096 rows=138.00 loops=1)
        Recheck Cond: (((dataset)::text = 'performance'::text) AND (occurred_at >= '2025-12-20 00:00:00'::timestamp without time zone) AND (occurred_at < '2026-01-01 00:00:00'::timestamp without time zone))
        Filter: (((class_section_id)::text = 'WEB-01'::text) AND ((event_type)::text = 'CANCELLED'::text))
        Rows Removed by Filter: 3141
        Heap Blocks: exact=308
        Buffers: shared hit=346
        ->  Bitmap Index Scan on idx_enrollment_events_dataset_student_time  (cost=0.00..122.71 rows=3251 width=0) (actual time=0.355..0.355 rows=3279.00 loops=1)
              Index Cond: (((dataset)::text = 'performance'::text) AND (occurred_at >= '2025-12-20 00:00:00'::timestamp without time zone) AND (occurred_at < '2026-01-01 00:00:00'::timestamp without time zone))
              Index Searches: 5
              Buffers: shared hit=38
Planning Time: 0.130 ms
Execution Time: 1.140 ms
```

## After, run 1

```text
Aggregate  (cost=283.90..283.91 rows=1 width=8) (actual time=0.205..0.206 rows=1.00 loops=1)
  Buffers: shared hit=142
  ->  Index Only Scan using idx_enrollment_events_dataset_section_type_time on enrollment_events  (cost=0.42..283.49 rows=164 width=0) (actual time=0.036..0.193 rows=138.00 loops=1)
        Index Cond: ((dataset = 'performance'::text) AND (class_section_id = 'WEB-01'::text) AND (event_type = 'CANCELLED'::text) AND (occurred_at >= '2025-12-20 00:00:00'::timestamp without time zone) AND (occurred_at < '2026-01-01 00:00:00'::timestamp without time zone))
        Heap Fetches: 138
        Index Searches: 1
        Buffers: shared hit=142
Planning Time: 0.145 ms
Execution Time: 0.228 ms
```

## After, run 2

```text
Aggregate  (cost=283.90..283.91 rows=1 width=8) (actual time=0.179..0.180 rows=1.00 loops=1)
  Buffers: shared hit=142
  ->  Index Only Scan using idx_enrollment_events_dataset_section_type_time on enrollment_events  (cost=0.42..283.49 rows=164 width=0) (actual time=0.028..0.169 rows=138.00 loops=1)
        Index Cond: ((dataset = 'performance'::text) AND (class_section_id = 'WEB-01'::text) AND (event_type = 'CANCELLED'::text) AND (occurred_at >= '2025-12-20 00:00:00'::timestamp without time zone) AND (occurred_at < '2026-01-01 00:00:00'::timestamp without time zone))
        Heap Fetches: 138
        Index Searches: 1
        Buffers: shared hit=142
Planning Time: 0.109 ms
Execution Time: 0.201 ms
```

## After, run 3

```text
Aggregate  (cost=283.90..283.91 rows=1 width=8) (actual time=0.177..0.177 rows=1.00 loops=1)
  Buffers: shared hit=142
  ->  Index Only Scan using idx_enrollment_events_dataset_section_type_time on enrollment_events  (cost=0.42..283.49 rows=164 width=0) (actual time=0.043..0.163 rows=138.00 loops=1)
        Index Cond: ((dataset = 'performance'::text) AND (class_section_id = 'WEB-01'::text) AND (event_type = 'CANCELLED'::text) AND (occurred_at >= '2025-12-20 00:00:00'::timestamp without time zone) AND (occurred_at < '2026-01-01 00:00:00'::timestamp without time zone))
        Heap Fetches: 138
        Index Searches: 1
        Buffers: shared hit=142
Planning Time: 0.176 ms
Execution Time: 0.207 ms
```

Expected and actual event_count: 138.

PASS: count unchanged, empty/literal input = 0, invalid timestamp rejected, duplicate index rejected.
CLEANUP PASS: disposable schema removed; original tables/indexes untouched.
