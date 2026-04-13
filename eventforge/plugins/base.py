from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from eventforge.core.event import Event


class PluginConfig(BaseModel):
    pass


@dataclass
class PluginMetadata:
    name: str
    version: str = "0.1.0"
    description: str = ""


class Plugin(ABC):
    metadata: PluginMetadata
    config_model: type[PluginConfig] = PluginConfig

    def __init__(self, config: dict[str, Any]):
        self.config = self.config_model.model_validate(config)

    def start(self) -> None:
        return

    def stop(self) -> None:
        return


class InputPlugin(Plugin, ABC):
    @abstractmethod
    def run(self, emit: Callable[[Event], None]) -> None:
        raise NotImplementedError


class FilterPlugin(Plugin, ABC):
    @abstractmethod
    def process(self, event: Event) -> Iterable[Event]:
        raise NotImplementedError


class OutputPlugin(Plugin, ABC):
    @abstractmethod
    def emit(self, events: list[Event]) -> None:
        raise NotImplementedError

    def flush(self) -> None:
        return


class CodecPlugin(Plugin, ABC):
    @abstractmethod
    def decode(self, payload: bytes | str) -> list[Event]:
        raise NotImplementedError

    @abstractmethod
    def encode(self, event: Event) -> bytes:
        raise NotImplementedError
