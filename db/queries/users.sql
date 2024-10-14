-- :name count_users :scalar
SELECT count(id) FROM users;
-- TESTED

-- :name count_anon_users :scalar
SELECT count(id) FROM users WHERE email IS NULL;
-- TESTED

-- :name count_registered_users :scalar
SELECT count(id) FROM users WHERE email IS NOT NULL;
-- TESTED



-- :name get_user :one
SELECT id, email, password_hash, registered_at FROM users WHERE id = :id;
-- TESTED

-- :name get_registered_user :one
SELECT id, email, password_hash, registered_at FROM users WHERE email = :email;
-- TESTED

-- :name get_anon_user :one
SELECT id FROM users WHERE email IS NULL ORDER BY id DESC LIMIT 1;
-- TESTED




-- :name add_anon_user :scalar
INSERT INTO users (email)
    VALUES (NULL)
    RETURNING id;
-- TESTED

-- :name add_registered_user :scalar
INSERT INTO users (email, password_hash, registered_at)
    VALUES (:email, :password_hash, now())
    RETURNING id;
-- TESTED




-- :name register_anon_user :affected
UPDATE users
    SET email = :email,
        password_hash = :password_hash,
        registered_at = now()
    WHERE id = :id;
-- BOOKMARK: test



-- :name delete_user :affected
DELETE FROM users WHERE id = :id;
-- TESTED

-- :name delete_all_users :affected
DELETE FROM users;
-- TESTED
