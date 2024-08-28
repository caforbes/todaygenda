-- :name count_tasks :scalar
SELECT count(id)
    FROM tasks 
    WHERE daylist_id = :daylist_id;

-- :name get_pending_tasks :many
SELECT id, title, estimate
    FROM tasks 
    WHERE   daylist_id = :daylist_id
            AND status = 'pending'
    ORDER BY daylist_order ASC;

-- :name get_done_tasks :many
SELECT id, title, estimate
    FROM tasks 
    WHERE   daylist_id = :daylist_id
            AND status = 'done'
    ORDER BY finished_at ASC;



-- :name add_task :scalar
WITH alias (target_user_id, max_order) AS (
    SELECT  max(dl.user_id),
            coalesce(max(t.daylist_order), 0)
        FROM daylists as dl
            LEFT JOIN tasks as t ON dl.id = t.daylist_id
            WHERE dl.id = :daylist_id          
)
INSERT INTO tasks
    (title, estimate, daylist_id, daylist_order, user_id)
    VALUES (:title, :estimate, :daylist_id,
            (SELECT max_order + 1 from alias),
            (SELECT target_user_id from alias))
    RETURNING id;
