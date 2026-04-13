from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class PipelineConfig:
    pipeline_id: str
    batch_size: int
    workers: int
    inputs: list[dict[str, Any]]
    filters: list[dict[str, Any]]
    outputs: list[dict[str, Any]]


@dataclass(slots=True)
class AppConfig:
    pipelines: list[PipelineConfig]


def load_config(path: str) -> AppConfig:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    pipelines = []
    for item in raw.get("pipelines", []):
        pipelines.append(
            PipelineConfig(
                pipeline_id=item["id"],
                batch_size=int(item.get("batch_size", 125)),
                workers=int(item.get("workers", 1)),
                inputs=item.get("input", []),
                filters=item.get("filter", []),
                outputs=item.get("output", []),
            )
        )
    return AppConfig(pipelines=pipelines)


def validate_config(cfg: AppConfig) -> list[str]:
    errors: list[str] = []
    if not cfg.pipelines:
        errors.append("at least one pipeline is required")
    for pipe in cfg.pipelines:
        if not pipe.inputs:
            errors.append(f"pipeline {pipe.pipeline_id}: input is required")
        if not pipe.outputs:
            errors.append(f"pipeline {pipe.pipeline_id}: output is required")
    return errors
