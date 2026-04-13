from __future__ import annotations

from collections.abc import Callable
from importlib.metadata import entry_points
from typing import Any

from eventforge.core.errors import ConfigError
from eventforge.plugins.base import CodecPlugin, FilterPlugin, InputPlugin, OutputPlugin

PluginType = type[InputPlugin | FilterPlugin | OutputPlugin | CodecPlugin]


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, dict[str, PluginType]] = {
            "input": {},
            "filter": {},
            "output": {},
            "codec": {},
        }

    def register(self, plugin_type: str, name: str, cls: PluginType) -> None:
        self._plugins[plugin_type][name] = cls

    def get(self, plugin_type: str, name: str) -> PluginType:
        try:
            return self._plugins[plugin_type][name]
        except KeyError as exc:
            raise ConfigError(f"unknown {plugin_type} plugin '{name}'") from exc

    def create(self, plugin_type: str, name: str, config: dict[str, Any]) -> Any:
        return self.get(plugin_type, name)(config)

    def list_plugins(self) -> dict[str, list[str]]:
        return {t: sorted(v.keys()) for t, v in self._plugins.items()}

    def load_entry_points(self) -> None:
        eps = entry_points(group="eventforge.plugins")
        for ep in eps:
            loader: Callable[[PluginRegistry], None] = ep.load()
            loader(self)
