from __future__ import annotations

from collections import Counter


class Metrics:
    def __init__(self) -> None:
        self.counters: Counter[str] = Counter()

    def inc(self, key: str, count: int = 1) -> None:
        self.counters[key] += count


metrics = Metrics()
