from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from eventforge.core.fieldref import parse_fieldref


RESERVED_FIELDS = {"@timestamp", "@metadata", "tags", "event", "host", "log", "trace"}


@dataclass
class Event:
    data: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def new(message: Any = None) -> "Event":
        payload: dict[str, Any] = {
            "@timestamp": datetime.now(timezone.utc).isoformat(),
            "@metadata": {},
            "tags": [],
        }
        if message is not None:
            payload["message"] = message
        return Event(payload)

    def clone(self, deep: bool = False) -> "Event":
        return Event(copy.deepcopy(self.data) if deep else dict(self.data))

    def get(self, path: str, default: Any = None) -> Any:
        keys = parse_fieldref(path)
        current: Any = self.data
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current

    def set(self, path: str, value: Any) -> None:
        keys = parse_fieldref(path)
        current = self.data
        for key in keys[:-1]:
            nxt = current.get(key)
            if not isinstance(nxt, dict):
                nxt = {}
                current[key] = nxt
            current = nxt
        current[keys[-1]] = value

    def remove(self, path: str) -> Any:
        keys = parse_fieldref(path)
        current = self.data
        for key in keys[:-1]:
            nxt = current.get(key)
            if not isinstance(nxt, dict):
                return None
            current = nxt
        return current.pop(keys[-1], None)

    def rename(self, source: str, target: str) -> None:
        value = self.remove(source)
        if value is not None:
            self.set(target, value)

    def append(self, path: str, value: Any) -> None:
        existing = self.get(path)
        if existing is None:
            self.set(path, [value])
            return
        if not isinstance(existing, list):
            existing = [existing]
            self.set(path, existing)
        existing.append(value)

    def merge(self, path: str, value: dict[str, Any]) -> None:
        existing = self.get(path)
        if existing is None:
            self.set(path, dict(value))
            return
        if not isinstance(existing, dict):
            raise TypeError(f"cannot merge non-dict field {path}")
        existing.update(value)

    def add_tag(self, tag: str) -> None:
        tags = self.get("tags", [])
        if not isinstance(tags, list):
            tags = [str(tags)]
            self.set("tags", tags)
        if tag not in tags:
            tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        tags = self.get("tags", [])
        if isinstance(tags, list) and tag in tags:
            tags.remove(tag)

    def mark_error(self, reason: str) -> None:
        self.set("[event][error]", reason)
        self.add_tag("_eventforge_error")
