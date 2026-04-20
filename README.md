# dontbeeviltube

This is an unfinished project about an open-source frontend to
YouTube, kind of like [Invidious](https://invidious.io/) except with
an architecture based on downloading the video on the backend using
[yt-dlp](https://github.com/yt-dlp/yt-dlp) before streaming to the
client, and thus benefiting from their faster turnaround time on
responding to Google crap being updated.

## Setup

Create `.env` file:

```
DATABASE_URL=postgres://dontbeeviltube_admin:something@localhost:5432/dontbeeviltube?sslmode=disable

APP_DATABASE_URL=postgres://dontbeeviltube_app:somethingelse@localhost:5432/dontbeeviltube?sslmode=disable
STORAGE_DIR=/home/yourself/some/directory
FLASK_SECRET_KEY=supersecure
```

Install dependencies:

```
poetry install
npm install
```

Setup database (Ubuntu):

```
sudo apt install postgresql-14
sudo systemctl enable --now postgresql
sudo -u postgres createdb dontbeeviltube
```

Edit the `/etc/postgresql/14/main/postgresql.conf` to have `port =
5432` so we can connect over TCP. Check `sudo -u postgres psql
dontbeeviltube` works.

Setup admin account:

```
CREATE USER dontbeeviltube_admin WITH PASSWORD 'something';
```

Install dbmate and run db migrations:

```
dbmate up
```

Setup app account:

```
CREATE USER dontbeeviltube_app WITH PASSWORD 'somethingelse';
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON accounts, downloads, playback_positions, subscriptions, watch_history, youtube_channels, youtube_videos TO dontbeeviltube_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dontbeeviltube_app;
```

Run the app:

```
poetry run flask --app dontbeeviltube.server:app run --host 127.0.0.1 --debug
```
