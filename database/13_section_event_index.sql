-- Count cancellations for a class in a time window. Run each stage separately.
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) AS event_count
FROM enrollment_events
WHERE dataset = 'performance'
    AND class_section_id = 'WEB-01'
    AND event_type = 'CANCELLED'
    AND occurred_at >= TIMESTAMP '2025-12-20 00:00:00'
    AND occurred_at < TIMESTAMP '2026-01-01 00:00:00';

CREATE INDEX idx_enrollment_events_dataset_section_type_time
ON enrollment_events (dataset, class_section_id, event_type, occurred_at);

ANALYZE enrollment_events;

EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) AS event_count
FROM enrollment_events
WHERE dataset = 'performance'
    AND class_section_id = 'WEB-01'
    AND event_type = 'CANCELLED'
    AND occurred_at >= TIMESTAMP '2025-12-20 00:00:00'
    AND occurred_at < TIMESTAMP '2026-01-01 00:00:00';
