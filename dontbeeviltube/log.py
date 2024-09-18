from datetime import datetime
import traceback
from typing import Any, Optional


def log(level: str, msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S%Z")
    print(f"{ts} [{level}] {msg}")


def log_error(msg: str, exc: Optional[Exception] = None, report: bool = True):
    if exc:
        traceback.print_exception(exc)
        msg += f": {type(exc).__name__}: {str(exc)}"
    log("ERROR", msg)
