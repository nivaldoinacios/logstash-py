from __future__ import annotations

import queue
import time
from dataclasses import dataclass

from eventforge.core.event import Event


@dataclass
class QueueStats:
    enqueued: int = 0
    dequeued: int = 0
    dropped: int = 0
    blocked_seconds: float = 0.0


class MemoryEventQueue:
    def __init__(self, maxsize: int = 10000):
        self._queue: queue.Queue[Event] = queue.Queue(maxsize=maxsize)
        self.stats = QueueStats()

    @property
    def size(self) -> int:
        return self._queue.qsize()

    @property
    def capacity(self) -> int:
        return self._queue.maxsize

    def put(self, event: Event, timeout: float = 1.0) -> bool:
        start = time.monotonic()
        try:
            self._queue.put(event, timeout=timeout)
            self.stats.enqueued += 1
            self.stats.blocked_seconds += max(0.0, time.monotonic() - start)
            return True
        except queue.Full:
            self.stats.dropped += 1
            return False

    def get_batch(self, max_batch: int, timeout: float = 0.5) -> list[Event]:
        batch: list[Event] = []
        try:
            first = self._queue.get(timeout=timeout)
            batch.append(first)
        except queue.Empty:
            return batch

        while len(batch) < max_batch:
            try:
                batch.append(self._queue.get_nowait())
            except queue.Empty:
                break

        self.stats.dequeued += len(batch)
        return batch
