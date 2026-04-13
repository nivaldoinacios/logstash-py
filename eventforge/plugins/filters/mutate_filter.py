from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pydantic import Field

from eventforge.core.event import Event
from eventforge.plugins.base import FilterPlugin, PluginConfig, PluginMetadata


class MutateFilterConfig(PluginConfig):
    add_field: dict[str, Any] = Field(default_factory=dict)
    remove_field: list[str] = Field(default_factory=list)
    rename: dict[str, str] = Field(default_factory=dict)
    add_tag: list[str] = Field(default_factory=list)
    remove_tag: list[str] = Field(default_factory=list)
    lowercase: list[str] = Field(default_factory=list)
    uppercase: list[str] = Field(default_factory=list)


class MutateFilter(FilterPlugin):
    metadata = PluginMetadata(name="mutate", description="Mutate event fields")
    config_model = MutateFilterConfig

    def process(self, event: Event) -> Iterable[Event]:
        for source, target in self.config.rename.items():
            event.rename(source, target)
        for field, value in self.config.add_field.items():
            event.set(field, value)
        for field in self.config.remove_field:
            event.remove(field)
        for field in self.config.lowercase:
            value = event.get(field)
            if isinstance(value, str):
                event.set(field, value.lower())
        for field in self.config.uppercase:
            value = event.get(field)
            if isinstance(value, str):
                event.set(field, value.upper())
        for tag in self.config.add_tag:
            event.add_tag(tag)
        for tag in self.config.remove_tag:
            event.remove_tag(tag)
        return [event]
