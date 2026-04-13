from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from eventforge.config.ast import PipelineSpec, PluginSpec, ProjectConfig
from eventforge.config.dsl import parse_dsl_file
from eventforge.core.errors import ConfigError


def _normalize_plugins(plugin_type: str, items: list[dict[str, Any]]) -> list[PluginSpec]:
    normalized: list[PluginSpec] = []
    for item in items:
        if len(item) != 1:
            raise ConfigError(f"invalid plugin declaration in {plugin_type}: {item}")
        name, config = next(iter(item.items()))
        normalized.append(PluginSpec(plugin_type=plugin_type, name=name, config=config or {}))
    return normalized


def parse_yaml_config(path: Path) -> ProjectConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ConfigError("top-level config must be a mapping")

    pipelines_raw = raw.get("pipelines")
    if not isinstance(pipelines_raw, list):
        raise ConfigError("config requires 'pipelines' list")

    pipelines: list[PipelineSpec] = []
    for item in pipelines_raw:
        if not isinstance(item, dict):
            raise ConfigError("pipeline entry must be an object")
        pipeline_id = item.get("id") or item.get("pipeline.id") or "main"
        workers = int(item.get("workers", 1))
        batch_size = int(item.get("batch_size", 125))
        queue_type = str(item.get("queue", "memory"))
        plugins = {
            "input": _normalize_plugins("input", item.get("input", [])),
            "filter": _normalize_plugins("filter", item.get("filter", [])),
            "output": _normalize_plugins("output", item.get("output", [])),
        }
        pipelines.append(
            PipelineSpec(
                pipeline_id=pipeline_id,
                workers=workers,
                batch_size=batch_size,
                queue_type=queue_type,
                plugins=plugins,
            )
        )

    return ProjectConfig(pipelines)


def load_config(path: str) -> ProjectConfig:
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"config file not found: {p}")
    if p.suffix.lower() in {".yml", ".yaml"}:
        return parse_yaml_config(p)
    if p.suffix.lower() in {".conf", ".dsl", ".ls"}:
        return parse_dsl_file(p)
    raise ConfigError(f"unsupported config extension: {p.suffix}")


def validate_config(config: ProjectConfig) -> None:
    if not config.pipelines:
        raise ConfigError("at least one pipeline is required")
    for pipeline in config.pipelines:
        if not pipeline.plugins.get("input"):
            raise ConfigError(f"pipeline '{pipeline.pipeline_id}' has no input plugin")
        if not pipeline.plugins.get("output"):
            raise ConfigError(f"pipeline '{pipeline.pipeline_id}' has no output plugin")
