from __future__ import annotations

import json
from collections.abc import Iterable

from eventforge.core.event import Event
from eventforge.plugins.base import FilterPlugin, PluginConfig, PluginMetadata


class JsonFilterConfig(PluginConfig):
    source: str = "message"
    target: str = ""
    tag_on_failure: str = "_jsonparsefailure"


class JsonFilter(FilterPlugin):
    metadata = PluginMetadata(name="json", description="Parse JSON from field")
    config_model = JsonFilterConfig

    def process(self, event: Event) -> Iterable[Event]:
        raw = event.get(self.config.source)
        if raw is None:
            return [event]
        try:
            parsed = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            event.add_tag(self.config.tag_on_failure)
            return [event]
        if self.config.target:
            event.set(self.config.target, parsed)
        elif isinstance(parsed, dict):
            event.data.update(parsed)
        else:
            event.set(self.config.source, parsed)
        return [event]
