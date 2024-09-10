-- migrate:up

CREATE TABLE accounts (
  account_id SERIAL PRIMARY KEY,
  login_name VARCHAR(64) NOT NULL,
  password_bcrypt VARCHAR(128) NOT NULL
);

CREATE TABLE youtube_channels (
  channel_id SERIAL PRIMARY KEY,
  channel_external_id VARCHAR(32) NOT NULL,
  channel_name VARCHAR(256) NOT NULL
);

CREATE TABLE youtube_videos (
  video_id SERIAL PRIMARY KEY,
  video_external_id VARCHAR(16) NOT NULL,
  video_name VARCHAR(1024) NOT NULL,
  video_description VARCHAR(65536) NOT NULL,
  video_duration REAL NOT NULL,
  upload_ts TIMESTAMP WITH TIME ZONE NOT NULL,
  refresh_ts TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE downloads (
  video_id INT PRIMARY KEY,
  object_id VARCHAR(32)
);

CREATE TABLE subscriptions (
  account_id INT REFERENCES accounts,
  channel_id INT REFERENCES youtube_channels,
  PRIMARY KEY (account_id, channel_id)
);

CREATE TABLE watch_history (
  watch_id SERIAL PRIMARY KEY,
  account_id INT REFERENCES accounts,
  video_id INT REFERENCES youtube_videos,
  watch_ts TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE playback_positions (
  account_id INT REFERENCES accounts,
  video_id INT REFERENCES youtube_videos,
  PRIMARY KEY (account_id, video_id),
  playback_position REAL NOT NULL,
  refresh_ts TIMESTAMP WITH TIME ZONE NOT NULL
);

-- migrate:down

DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS youtube_channels;
DROP TABLE IF EXISTS youtube_videos;
DROP TABLE IF EXISTS downloads;
DROP TABLE IF EXISTS subscriptions;
DROP TABLE IF EXISTS watch_history;
DROP TABLE IF EXISTS playback_positions;
