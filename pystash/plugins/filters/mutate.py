from __future__ import annotations

from pystash.core.event import Event
from pystash.plugins.base import FilterPlugin


class MutateFilter(FilterPlugin):
    plugin_name = "mutate"

    def process(self, event: Event) -> list[Event]:
        for key, value in self.config.get("add_field", {}).items():
            event.set(key, value)
        for key in self.config.get("remove_field", []):
            event.delete(key)
        return [event]
