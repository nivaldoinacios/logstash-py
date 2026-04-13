from __future__ import annotations

import random
from collections.abc import Iterable

from eventforge.core.event import Event
from eventforge.plugins.base import FilterPlugin, PluginConfig, PluginMetadata


class DropFilterConfig(PluginConfig):
    percentage: int = 100


class DropFilter(FilterPlugin):
    metadata = PluginMetadata(name="drop", description="Drop events")
    config_model = DropFilterConfig

    def process(self, event: Event) -> Iterable[Event]:
        if random.random() < (self.config.percentage / 100.0):
            return []
        return [event]
