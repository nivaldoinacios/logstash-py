from __future__ import annotations

import json

from eventforge.core.event import Event
from eventforge.plugins.base import CodecPlugin, PluginConfig, PluginMetadata


class JsonCodecConfig(PluginConfig):
    charset: str = "utf-8"


class JsonCodec(CodecPlugin):
    metadata = PluginMetadata(name="json", description="JSON codec")
    config_model = JsonCodecConfig

    def decode(self, payload: bytes | str) -> list[Event]:
        if isinstance(payload, bytes):
            payload = payload.decode(self.config.charset, errors="replace")
        data = json.loads(payload)
        event = Event.new()
        if isinstance(data, dict):
            event.data.update(data)
        else:
            event.set("message", data)
        return [event]

    def encode(self, event: Event) -> bytes:
        return (json.dumps(event.data, ensure_ascii=False) + "\n").encode(self.config.charset)
