from __future__ import annotations

import json

from eventforge.plugins.base import OutputPlugin, PluginConfig, PluginMetadata


class StdoutOutputConfig(PluginConfig):
    pretty: bool = False


class StdoutOutput(OutputPlugin):
    metadata = PluginMetadata(name="stdout", description="Write events to stdout")
    config_model = StdoutOutputConfig

    def emit(self, events: list) -> None:
        for event in events:
            if self.config.pretty:
                print(json.dumps(event.data, ensure_ascii=False, indent=2))
            else:
                print(json.dumps(event.data, ensure_ascii=False))
