from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
import shutil
import subprocess
from uuid import UUID, uuid4 as get_random_uuid

from dontbeeviltube.config import cfg
from dontbeeviltube.database import db
from dontbeeviltube.util import must


@dataclass
class Video:
    internal_id: int
    external_id: str
    name: str | None
    description: str | None
    duration: Decimal | None
    upload_ts: datetime | None
    refresh_ts: datetime
    object_id: UUID | None = None

    @staticmethod
    def from_db(internal_id: int) -> Video:
        with db.cursor() as curs:
            curs.execute(
                "SELECT * FROM youtube_videos WHERE video_id = %s LIMIT 1",
                (internal_id,),
            )
            rec = must(curs.fetchone())
            v = Video(
                internal_id=rec.video_id,
                external_id=rec.video_external_id,
                name=rec.video_name,
                description=rec.video_description,
                duration=rec.video_duration,
                upload_ts=rec.upload_ts,
                refresh_ts=rec.refresh_ts,
            )
            curs.execute(
                "SELECT object_id FROM downloads WHERE video_id = %s AND completed ORDER BY download_end_ts DESC LIMIT 1",
                (internal_id,),
            )
            if rec := curs.fetchone():
                v.object_id = rec.object_id
            return v

    def download(self, cfg: Config):
        # Check most recent download for the video. If it is
        # completed, we should initiate a new download. If it is not
        # completed yet, but is less than an hour old, we can resume
        # it. If we are initiating a new download, log in the
        # database. Otherwise, the existing database entry is fine.
        with db.transaction() as txn:
            txn.execute(
                "SELECT object_id, download_start_ts FROM downloads WHERE video_id = %s ORDER BY download_start_ts DESC LIMIT 1",
                (self.internal_id,),
            )
            if not (
                rec := must(txn.fetchone())
            ).completed and datetime.now() - rec.download_start_ts < timedelta(hours=1):
                object_id = rec.object_id
            else:
                txn.execute(
                    "INSERT INTO downloads (video_id) VALUES (%s) RETURNING object_id",
                    (self.internal_id,),
                )
                object_id = must(txn.fetchone()).object_id
        # Perform the actual download. This is the step that is the
        # most likely to be interrupted. Set up the temporary
        # directory beforehand, and tear it down afterward. If we get
        # interrupted, things will be cleaned up next time the video
        # is downloaded, or eventually by a cleanup process.
        (cfg.temp_dir / f"{object_id}").mkdir(exist_ok=True)
        subprocess.run(
            [
                "yt-dlp",
                f"-Phome:{cfg.media_dir}",
                f"-Ptemp:{cfg.temp_dir}/{object_id}",
                f"-o{object_id}.%(ext)s",
                "-c",
                f"https://www.youtube.com/watch?v={self.external_id}",
            ],
            check=True,
        )
        assert (cfg.media_dir / f"{object_id}.mp4").is_file()
        try:
            shutil.rmtree(cfg.temp_dir / f"{object_id}")
        except FileNotFoundError:
            pass
        # Log in the database and in our own object that we completed
        # the download. If somebody else messed with the same object
        # while we were downloading, this might not work right.
        with db.cursor() as txn:
            txn.execute(
                "UPDATE downloads SET download_end_ts = current_timestamp WHERE object_id = %s",
                (object_id,),
            )
        self.object_id = object_id
        # Remove all previous downloads for the same video if this one
        # has succeeded.
        with db.cursor() as txn:
            txn.execute(
                "SELECT object_id FROM downloads WHERE video_id = %s AND object_id != %s",
                (self.internal_id, self.object_id),
            )
            while rec := txn.fetchone():
                try:
                    (cfg.media_dir / f"{rec.object_id}.mp4").unlink()
                except FileNotFoundError:
                    pass
                try:
                    (cfg.temp_dir / f"{rec.object_id}").unlink()
                except FileNotFoundError:
                    pass
            txn.execute("DELETE FROM downloads WHERE video_id = %s AND object_id != %s")
