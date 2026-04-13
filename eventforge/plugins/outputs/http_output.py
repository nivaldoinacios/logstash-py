from __future__ import annotations

import requests
from pydantic import Field

from eventforge.plugins.base import OutputPlugin, PluginConfig, PluginMetadata


class HttpOutputConfig(PluginConfig):
    url: str
    method: str = "POST"
    timeout_seconds: float = 5.0
    headers: dict[str, str] = Field(default_factory=dict)


class HttpOutput(OutputPlugin):
    metadata = PluginMetadata(name="http", description="Send events via HTTP")
    config_model = HttpOutputConfig

    def emit(self, events: list) -> None:
        method = self.config.method.upper()
        for event in events:
            requests.request(
                method,
                self.config.url,
                json=event.data,
                headers=self.config.headers,
                timeout=self.config.timeout_seconds,
            ).raise_for_status()
