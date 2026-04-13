from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PluginSpec:
    plugin_type: str
    name: str
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PipelineSpec:
    pipeline_id: str
    workers: int = 1
    batch_size: int = 125
    queue_type: str = "memory"
    plugins: dict[str, list[PluginSpec]] = field(default_factory=lambda: {"input": [], "filter": [], "output": []})


@dataclass(slots=True)
class ProjectConfig:
    pipelines: list[PipelineSpec]
