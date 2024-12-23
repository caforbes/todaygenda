-- :name get_active_daylist :one
SELECT id, expiry
    FROM daylists
    WHERE user_id = :user_id AND expiry > now()
    ORDER BY expiry DESC LIMIT 1;
-- TESTED

-- :name add_daylist :scalar
INSERT INTO daylists (user_id, expiry)
    VALUES (:user_id, :expiry)
    RETURNING id;
-- TESTED