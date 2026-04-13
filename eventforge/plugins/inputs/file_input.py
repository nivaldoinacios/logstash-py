from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Literal

from pydantic import Field

from eventforge.core.errors import ConfigError
from eventforge.plugins.base import InputPlugin, PluginConfig, PluginMetadata
from eventforge.plugins.codecs.json_codec import JsonCodec
from eventforge.plugins.codecs.plain import PlainCodec


class FileInputConfig(PluginConfig):
    path: str
    mode: Literal["read", "tail"] = "read"
    poll_interval_seconds: float = 0.5
    codec: Literal["plain", "json"] = "plain"
    codec_config: dict[str, Any] = Field(default_factory=dict)


class FileInput(InputPlugin):
    metadata = PluginMetadata(name="file", description="Read events from file")
    config_model = FileInputConfig

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._stop = False

    def stop(self) -> None:
        self._stop = True

    def run(self, emit: callable) -> None:
        path = Path(self.config.path)
        if not path.exists():
            raise ConfigError(f"file input path not found: {path}")

        codec = PlainCodec(self.config.codec_config) if self.config.codec == "plain" else JsonCodec(self.config.codec_config)

        with path.open("rb") as stream:
            while not self._stop:
                line = stream.readline()
                if line:
                    for event in codec.decode(line):
                        event.set("[event][source]", str(path))
                        emit(event)
                    continue
                if self.config.mode == "read":
                    break
                time.sleep(self.config.poll_interval_seconds)
