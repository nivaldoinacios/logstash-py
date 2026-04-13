from __future__ import annotations

from pystash.core.event import Event
from pystash.plugins.base import FilterPlugin


class DropFilter(FilterPlugin):
    plugin_name = "drop"

    def process(self, event: Event) -> list[Event]:
        return []
