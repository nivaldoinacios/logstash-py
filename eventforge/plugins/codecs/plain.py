from __future__ import annotations

from eventforge.core.event import Event
from eventforge.plugins.base import CodecPlugin, PluginConfig, PluginMetadata


class PlainCodecConfig(PluginConfig):
    charset: str = "utf-8"


class PlainCodec(CodecPlugin):
    metadata = PluginMetadata(name="plain", description="Plain text codec")
    config_model = PlainCodecConfig

    def decode(self, payload: bytes | str) -> list[Event]:
        if isinstance(payload, bytes):
            message = payload.decode(self.config.charset, errors="replace")
        else:
            message = payload
        return [Event.new(message=message.rstrip("\n"))]

    def encode(self, event: Event) -> bytes:
        return f"{event.data}\n".encode(self.config.charset)
