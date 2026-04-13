from __future__ import annotations

import json
from pathlib import Path

from eventforge.plugins.base import OutputPlugin, PluginConfig, PluginMetadata


class FileOutputConfig(PluginConfig):
    path: str


class FileOutput(OutputPlugin):
    metadata = PluginMetadata(name="file", description="Write events to file")
    config_model = FileOutputConfig

    def emit(self, events: list) -> None:
        path = Path(self.config.path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            for event in events:
                handle.write(json.dumps(event.data, ensure_ascii=False) + "\n")
