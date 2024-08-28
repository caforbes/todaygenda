-- :name count_users :scalar
SELECT count(id) FROM users;

-- :name count_anon_users :scalar
SELECT count(id) FROM users WHERE email IS NULL;



-- :name get_user :one
SELECT id FROM users WHERE id = :user_id;

-- :name get_anon_user :one
SELECT id FROM users WHERE email IS NULL ORDER BY id DESC LIMIT 1;




-- :name add_anon_user :scalar
INSERT INTO users (email)
    VALUES (NULL)
    RETURNING id;



-- :name delete_user :affected
DELETE FROM users WHERE id = :user_id;

-- :name delete_all_users :affected
DELETE FROM users;

