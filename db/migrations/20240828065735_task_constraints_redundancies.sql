-- migrate:up

ALTER TABLE tasks
    RENAME CONSTRAINT check_tasks_ordered_in_daylist
                      TO unique_task_order_in_daylist;
ALTER TABLE tasks ALTER COLUMN daylist_order DROP NOT NULL;
ALTER TABLE tasks DROP COLUMN IF EXISTS user_id;

-- modify records that violate new check
UPDATE tasks t
    SET daylist_order = new_order
    FROM (
        SELECT id,
            (SELECT max(t.daylist_order) FROM tasks AS t WHERE t.daylist_id = tasks.daylist_id)
            + ROW_NUMBER() OVER (PARTITION BY daylist_id ORDER BY created_at)
            AS new_order
        FROM tasks
        WHERE daylist_order IS NULL AND status = 'done'
    ) violations
    WHERE t.id = violations.id;

ALTER TABLE tasks
    ADD CONSTRAINT check_pending_tasks_ordered
    CHECK ( daylist_order IS NOT NULL OR status = 'done' );
ALTER TABLE tasks
    ADD CONSTRAINT check_done_tasks_unordered
    CHECK ( daylist_order IS NULL OR status = 'pending' );

-- migrate:down

ALTER TABLE tasks
    RENAME CONSTRAINT unique_task_order_in_daylist
                        TO check_tasks_ordered_in_daylist;
ALTER TABLE tasks ALTER COLUMN daylist_order SET NOT NULL;
ALTER TABLE tasks DROP CONSTRAINT check_pending_tasks_ordered;
ALTER TABLE tasks DROP CONSTRAINT check_done_tasks_unordered;
ALTER TABLE tasks ADD COLUMN user_id int REFERENCES users (id) ON DELETE CASCADE;

-- recover redundant user id through daylist table
UPDATE tasks t
    SET user_id = related_user
    FROM (
        SELECT dl.user_id AS related_user, t.id
            FROM daylists AS dl
            INNER JOIN tasks as t ON dl.id = t.daylist_id
    ) violations
    WHERE t.id = violations.id;

ALTER TABLE tasks
    ALTER COLUMN user_id SET NOT NULL;
