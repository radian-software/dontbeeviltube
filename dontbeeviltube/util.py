from typing import TypeVar


T = TypeVar("T")


def must(v: T | None) -> T:
    assert v is not None
    return v
