-- :name count_tasks :scalar
SELECT count(id)
    FROM tasks
    WHERE daylist_id = :daylist_id;
-- TESTED

-- :name get_task :one
SELECT id, title, estimate, done
    FROM tasks
    WHERE id = :id;
-- TESTED
-- BOOKMARK: need to validate permissions for whoever is getting

-- :name get_current_tasks :many
SELECT t.id, t.title, t.estimate, t.done
    FROM tasks as t INNER JOIN daylists as dl
                    ON t.daylist_id = dl.id
    WHERE   dl.user_id = :user_id
            AND dl.expiry > now()
    ORDER BY done ASC, daylist_order ASC, finished_at ASC;
-- TESTED
-- BOOKMARK: add testing after items may get reordered by updates

-- :name get_pending_tasks :many
SELECT t.id, t.title, t.estimate
    FROM tasks as t INNER JOIN daylists as dl
                    ON t.daylist_id = dl.id
    WHERE   dl.user_id = :user_id
            AND dl.expiry > now()
            AND NOT done
    ORDER BY daylist_order ASC;
-- TESTED
-- BOOKMARK: add testing after items may get reordered by updates

-- :name get_done_tasks :many
SELECT t.id, t.title, t.estimate
    FROM tasks as t INNER JOIN daylists as dl
                    ON t.daylist_id = dl.id
    WHERE   dl.user_id = :user_id
            AND dl.expiry > now()
            AND done
    ORDER BY finished_at ASC;
-- BOOKMARK: test this q



-- :name add_task_for_user :scalar
WITH last_row (target_daylist_id, max_order) AS (
    SELECT  max(dl.id),
            coalesce(max(t.daylist_order), 0)
        FROM daylists as dl
            LEFT JOIN tasks as t ON dl.id = t.daylist_id
            WHERE dl.user_id = :user_id AND dl.expiry > now()          
)
INSERT INTO tasks
    (title, estimate, daylist_id, daylist_order)
    VALUES (:title, :estimate,
            (SELECT target_daylist_id from last_row),
            (SELECT max_order + 1 from last_row))
    RETURNING id;
-- TESTED

-- :name add_task_to_list :scalar
WITH last_row (max_order) AS (
    SELECT coalesce(max(daylist_order), 0)
        FROM tasks
        WHERE daylist_id = :daylist_id
)
INSERT INTO tasks
    (title, estimate, daylist_id, daylist_order)
    VALUES (:title, :estimate, :daylist_id,
            (SELECT max_order + 1 from last_row))
    RETURNING id;
-- TESTED
