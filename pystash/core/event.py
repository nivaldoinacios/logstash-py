from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import copy
import re

_PATH_RE = re.compile(r"\[([^\]]+)\]")


def parse_path(path: str) -> list[str]:
    if path.startswith("["):
        return _PATH_RE.findall(path)
    return path.split(".")


@dataclass(slots=True)
class Event:
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    errors: list[str] = field(default_factory=list)
    source: dict[str, Any] = field(default_factory=dict)

    def get(self, path: str, default: Any = None) -> Any:
        target = self.metadata if path.startswith("[@metadata]") else self.data
        keys = parse_path(path)
        if keys and keys[0] == "@metadata":
            keys = keys[1:]
        cur: Any = target
        for key in keys:
            if not isinstance(cur, dict) or key not in cur:
                return default
            cur = cur[key]
        return cur

    def set(self, path: str, value: Any) -> None:
        target = self.metadata if path.startswith("[@metadata]") else self.data
        keys = parse_path(path)
        if keys and keys[0] == "@metadata":
            keys = keys[1:]
        cur = target
        for key in keys[:-1]:
            if key not in cur or not isinstance(cur[key], dict):
                cur[key] = {}
            cur = cur[key]
        cur[keys[-1]] = value

    def delete(self, path: str) -> None:
        target = self.metadata if path.startswith("[@metadata]") else self.data
        keys = parse_path(path)
        if keys and keys[0] == "@metadata":
            keys = keys[1:]
        cur = target
        for key in keys[:-1]:
            nxt = cur.get(key)
            if not isinstance(nxt, dict):
                return
            cur = nxt
        cur.pop(keys[-1], None)

    def clone(self, deep: bool = False) -> "Event":
        if deep:
            return copy.deepcopy(self)
        return Event(
            data=dict(self.data),
            metadata=dict(self.metadata),
            tags=list(self.tags),
            timestamp=self.timestamp,
            errors=list(self.errors),
            source=dict(self.source),
        )
