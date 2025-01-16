from decimal import Decimal
import re
from typing import Optional, TypeVar


T = TypeVar("T")


def must(v: T | None, explanation: str = "got an unexpected None") -> T:
    assert v is not None, explanation
    return v


def strip_safe(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    return s.strip()


def parse_duration(s: str) -> Decimal:
    m = must(
        re.fullmatch(
            r"((?P<hours>[0-9]+):)?(?P<minutes>[0-9]+):(?P<seconds>[0-9]+(\.[0-9]+)?)",
            s,
        ),
        f"unparseable duration: {s}",
    ).groupdict()
    return (
        Decimal(m["seconds"])
        + Decimal(m["minutes"]) * 60
        + Decimal(m.get("hours") or "0") * 3600
    )


def parse_amount(s: str) -> int:
    n = Decimal(s.rstrip("KM"))
    if s.endswith("K"):
        n *= 10 ** 3
    elif s.endswith("M"):
        n *= 10 ** 6
    return int(n)
