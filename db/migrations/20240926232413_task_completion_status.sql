-- migrate:up

-- convert task status from enum to boolean
ALTER TABLE tasks
    -- temp drop constraints
    ALTER COLUMN status DROP DEFAULT,
    DROP CONSTRAINT check_done_tasks_unordered,
    DROP CONSTRAINT check_pending_tasks_ordered,
    -- update status column and data
    ALTER COLUMN status TYPE boolean
        USING (status = 'done');
-- rename
ALTER TABLE tasks RENAME COLUMN status TO done ;
-- reapply constraints
ALTER TABLE tasks
    ALTER COLUMN done SET DEFAULT false,
    ADD CONSTRAINT check_done_tasks_unordered
        CHECK ( (daylist_order IS NULL) OR (done = false) ),
    ADD CONSTRAINT check_pending_tasks_ordered
        CHECK ( (daylist_order IS NOT NULL) OR (done = true) )
    ;
-- delete status enum
DROP TYPE IF EXISTS task_status;

-- migrate:down

-- rebuild status enum
CREATE TYPE task_status AS ENUM ('pending', 'done');
-- revert done boolean to status enum
ALTER TABLE tasks
    -- temp drop constraints
    ALTER COLUMN done DROP DEFAULT,
    DROP CONSTRAINT check_done_tasks_unordered,
    DROP CONSTRAINT check_pending_tasks_ordered,
    -- update status column and data
    ALTER COLUMN done TYPE task_status
        USING (CASE WHEN false THEN 'done'::task_status ELSE 'pending'::task_status END) ;
-- rename
ALTER TABLE tasks RENAME COLUMN done TO status ;
-- reapply constraints
ALTER TABLE tasks
    ALTER COLUMN status SET DEFAULT 'pending',
    ADD CONSTRAINT check_done_tasks_unordered
        CHECK ( (daylist_order IS NULL) OR (status = 'pending') ),
    ADD CONSTRAINT check_pending_tasks_ordered
        CHECK ( (daylist_order IS NOT NULL) OR (status = 'done') )
    ;
