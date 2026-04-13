from __future__ import annotations

from collections.abc import Iterable

from dateutil import parser as date_parser

from eventforge.core.event import Event
from eventforge.plugins.base import FilterPlugin, PluginConfig, PluginMetadata


class DateFilterConfig(PluginConfig):
    source: str = "@timestamp"
    target: str = "@timestamp"
    tag_on_failure: str = "_dateparsefailure"


class DateFilter(FilterPlugin):
    metadata = PluginMetadata(name="date", description="Date parser filter")
    config_model = DateFilterConfig

    def process(self, event: Event) -> Iterable[Event]:
        raw = event.get(self.config.source)
        if raw is None:
            return [event]
        try:
            parsed = date_parser.parse(str(raw))
            event.set(self.config.target, parsed.isoformat())
        except Exception:
            event.add_tag(self.config.tag_on_failure)
        return [event]
