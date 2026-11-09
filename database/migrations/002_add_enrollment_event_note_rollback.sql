-- Removes every note value. Existing events and their other columns remain.
-- Back up note values first if they must be retained.
BEGIN;

ALTER TABLE enrollment_events
DROP COLUMN note;

DELETE FROM schema_migrations
WHERE version = '002';

COMMIT;
