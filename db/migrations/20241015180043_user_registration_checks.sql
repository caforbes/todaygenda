-- migrate:up

ALTER TABLE users
    ADD CONSTRAINT unique_email UNIQUE (email),
    ADD CONSTRAINT check_registered_user_data
        CHECK ( ( email IS NULL AND password_hash IS NULL AND registered_at IS NULL )
                OR 
                ( email IS NOT NULL AND password_hash IS NOT NULL AND registered_at IS NOT NULL ) );

-- migrate:down

ALTER TABLE users
    DROP CONSTRAINT unique_email,
    DROP CONSTRAINT check_registered_user_data;
