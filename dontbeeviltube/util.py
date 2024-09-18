from typing import Optional, TypeVar


T = TypeVar("T")


def must(v: T | None) -> T:
    assert v is not None
    return v


def strip_safe(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    return s.strip()
