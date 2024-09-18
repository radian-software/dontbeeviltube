-- migrate:up

ALTER TABLE accounts ADD COLUMN flask_login_id VARCHAR(64) NOT NULL UNIQUE DEFAULT gen_random_uuid();

-- migrate:down

ALTER TABLE accounts DROP COLUMN IF EXISTS flask_login_id;
