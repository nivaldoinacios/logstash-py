from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from pystash.core.event import Event


@dataclass(slots=True)
class PluginContext:
    pipeline_id: str


class BasePlugin:
    plugin_name = "base"

    def __init__(self, config: dict[str, Any], context: PluginContext):
        self.config = config
        self.context = context


class InputPlugin(BasePlugin):
    def run(self):
        raise NotImplementedError


class FilterPlugin(BasePlugin):
    def process(self, event: Event) -> list[Event]:
        raise NotImplementedError


class OutputPlugin(BasePlugin):
    def send(self, events: list[Event]) -> None:
        raise NotImplementedError
