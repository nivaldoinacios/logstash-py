from __future__ import annotations

import sys
import threading
from collections.abc import Callable
from typing import Any

from pydantic import Field

from eventforge.plugins.base import InputPlugin, PluginConfig, PluginMetadata
from eventforge.plugins.codecs.plain import PlainCodec


class StdinInputConfig(PluginConfig):
    codec: str = "plain"
    codec_config: dict[str, Any] = Field(default_factory=dict)


class StdinInput(InputPlugin):
    metadata = PluginMetadata(name="stdin", description="Read lines from stdin")
    config_model = StdinInputConfig

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._stop = threading.Event()

    def stop(self) -> None:
        self._stop.set()

    def run(self, emit: Callable) -> None:
        codec = PlainCodec(self.config.codec_config)
        for line in sys.stdin:
            if self._stop.is_set():
                break
            for event in codec.decode(line):
                emit(event)
