from __future__ import annotations

from collections.abc import Callable
from typing import Any


class Registry:
    def __init__(self) -> None:
        self._plugins: dict[tuple[str, str], Callable[..., Any]] = {}

    def register(self, kind: str, name: str, cls: Callable[..., Any]) -> None:
        self._plugins[(kind, name)] = cls

    def get(self, kind: str, name: str):
        key = (kind, name)
        if key not in self._plugins:
            raise KeyError(f"Plugin not found: {kind}:{name}")
        return self._plugins[key]


registry = Registry()
