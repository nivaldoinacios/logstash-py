from __future__ import annotations

import re
from functools import lru_cache

FIELD_RE = re.compile(r"\[([^\[\]]+)\]")


@lru_cache(maxsize=4096)
def parse_fieldref(path: str) -> tuple[str, ...]:
    if not path:
        raise ValueError("empty field path")
    if path.startswith("["):
        parts = tuple(FIELD_RE.findall(path))
        if not parts:
            raise ValueError(f"invalid field reference: {path}")
        return parts
    return (path,)
