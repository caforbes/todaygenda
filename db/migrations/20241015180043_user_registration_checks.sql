-- migrate:up

ALTER TABLE users
    ADD CONSTRAINT check_registered_user_data
    CHECK ( ( email IS NULL AND password_hash IS NULL AND registered_at IS NULL )
            OR 
            ( email IS NOT NULL AND password_hash IS NOT NULL AND registered_at IS NOT NULL ) );

-- migrate:down

ALTER TABLE users
    DROP CONSTRAINT check_registered_user_data;
