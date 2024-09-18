from dataclasses import dataclass
import os
from pathlib import Path


@dataclass
class Config:
    media_dir: Path
    temp_dir: Path
    db_addr: str
    flask_secret_key: str

    @staticmethod
    def from_env():
        storage = Path(os.environ["STORAGE_DIR"]).resolve()
        assert storage.is_dir(), storage
        cfg = Config(
            media_dir=storage / "media",
            temp_dir=storage / "temp",
            db_addr=os.environ["APP_DATABASE_URL"],
            flask_secret_key=os.environ["FLASK_SECRET_KEY"],
        )
        cfg.media_dir.mkdir(exist_ok=True)
        cfg.temp_dir.mkdir(exist_ok=True)
        return cfg


cfg = Config.from_env()
