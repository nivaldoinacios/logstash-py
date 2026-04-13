from __future__ import annotations

import json
from pystash.core.event import Event
from pystash.plugins.base import FilterPlugin


class JsonFilter(FilterPlugin):
    plugin_name = "json"

    def process(self, event: Event) -> list[Event]:
        source = self.config.get("source", "message")
        target = self.config.get("target")
        value = event.get(source)
        if not isinstance(value, str):
            return [event]
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            event.tags.append("_jsonparsefailure")
            return [event]
        if target:
            event.set(target, parsed)
        else:
            if isinstance(parsed, dict):
                event.data.update(parsed)
            else:
                event.set(source, parsed)
        return [event]
