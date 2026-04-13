from __future__ import annotations

from datetime import datetime, timezone
from pystash.core.event import Event
from pystash.plugins.base import FilterPlugin


class DateFilter(FilterPlugin):
    plugin_name = "date"

    def process(self, event: Event) -> list[Event]:
        source = self.config.get("source", "timestamp")
        fmt = self.config.get("format", "%Y-%m-%dT%H:%M:%S")
        value = event.get(source)
        if not isinstance(value, str):
            return [event]
        try:
            parsed = datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
            event.timestamp = parsed
        except ValueError:
            event.tags.append("_dateparsefailure")
        return [event]
