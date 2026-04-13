from __future__ import annotations

import json

import requests
from pydantic import Field

from eventforge.plugins.base import OutputPlugin, PluginConfig, PluginMetadata


class ElasticsearchOutputConfig(PluginConfig):
    hosts: list[str] = Field(default_factory=lambda: ["http://127.0.0.1:9200"])
    index: str = "eventforge-%Y.%m.%d"
    timeout_seconds: float = 5.0


class ElasticsearchOutput(OutputPlugin):
    metadata = PluginMetadata(name="elasticsearch", description="Elasticsearch bulk output")
    config_model = ElasticsearchOutputConfig

    def emit(self, events: list) -> None:
        if not events:
            return
        base = self.config.hosts[0].rstrip("/")
        bulk_url = f"{base}/_bulk"
        lines: list[str] = []
        for event in events:
            lines.append('{"index":{}}')
            lines.append(json.dumps(event.data, ensure_ascii=False))
        payload = "\n".join(lines) + "\n"
        response = requests.post(
            bulk_url,
            data=payload.encode("utf-8"),
            headers={"Content-Type": "application/x-ndjson"},
            timeout=self.config.timeout_seconds,
        )
        response.raise_for_status()
