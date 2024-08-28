-- migrate:up

CREATE TABLE users (
    id serial PRIMARY KEY,
    email varchar(254),
    password_hash varchar(100),
    registered_at timestamp
);

CREATE TABLE daylists (
    id serial PRIMARY KEY,
    user_id integer NOT NULL
                    REFERENCES users (id) ON DELETE CASCADE,
    expiry timestamp NOT NULL,
    created_at timestamp DEFAULT now()
);

CREATE TYPE task_status AS ENUM ('pending', 'done');

CREATE TABLE tasks (
    id serial PRIMARY KEY,
    user_id integer NOT NULL 
                    REFERENCES users (id) ON DELETE CASCADE,
    title varchar(200) NOT NULL,
    status task_status NOT NULL DEFAULT 'pending',
    estimate interval,
    created_at timestamp DEFAULT now(),
    updated_at timestamp,
    finished_at timestamp,
    daylist_id integer  NOT NULL
                        REFERENCES daylists (id) ON DELETE CASCADE,
    daylist_order integer NOT NULL
);
ALTER TABLE tasks
    ADD CONSTRAINT  check_tasks_ordered_in_daylist
                    UNIQUE (daylist_id, daylist_order);

-- migrate:down
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS daylists;
DROP TABLE IF EXISTS users;
DROP TYPE IF EXISTS task_status;