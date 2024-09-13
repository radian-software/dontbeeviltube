from dataclasses import dataclass
import os
from pathlib import Path


@dataclass
class Config:
    media_dir: Path
    temp_dir: Path
    db_addr: str

    @staticmethod
    def from_env():
        storage = Path(os.environ["STORAGE_DIR"]).resolve()
        return Config(
            media_dir=storage / "media",
            temp_dir=storage / "temp",
            db_addr=os.environ["APP_DATABASE_URL"],
        )


cfg = Config.from_env()
