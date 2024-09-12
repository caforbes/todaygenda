-- migrate:up
ALTER TABLE daylists
    ALTER COLUMN expiry TYPE timestamp with time zone ;

-- migrate:down
ALTER TABLE daylists
    ALTER COLUMN expiry TYPE timestamp ;
