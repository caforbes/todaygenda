-- :name count_users :scalar
SELECT count(id) FROM users;
-- TESTED

-- :name count_anon_users :scalar
SELECT count(id) FROM users WHERE email IS NULL;
-- TESTED



-- :name get_user :one
SELECT id FROM users WHERE id = :user_id;
-- BOOKMARK: test more with registered users

-- :name get_anon_user :one
SELECT id FROM users WHERE email IS NULL ORDER BY id DESC LIMIT 1;
-- TESTED




-- :name add_anon_user :scalar
INSERT INTO users (email)
    VALUES (NULL)
    RETURNING id;
-- TESTED



-- :name delete_user :affected
DELETE FROM users WHERE id = :user_id;
-- TESTED

-- :name delete_all_users :affected
DELETE FROM users;
-- TESTED
