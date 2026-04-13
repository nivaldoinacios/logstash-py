from __future__ import annotations

import re
from pystash.core.event import Event
from pystash.plugins.base import FilterPlugin


class GrokFilter(FilterPlugin):
    plugin_name = "grok"

    def __init__(self, config, context):
        super().__init__(config, context)
        self.field = config.get("source", "message")
        pattern = config.get("pattern")
        if not pattern:
            raise ValueError("grok pattern is required")
        self.regex = re.compile(pattern)

    def process(self, event: Event) -> list[Event]:
        value = event.get(self.field, "")
        if not isinstance(value, str):
            return [event]
        match = self.regex.search(value)
        if not match:
            event.tags.append("_grokparsefailure")
            return [event]
        event.data.update(match.groupdict())
        return [event]
