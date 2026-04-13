from __future__ import annotations

import signal
from dataclasses import dataclass

from eventforge.config.ast import ProjectConfig
from eventforge.observability.health import HealthServer
from eventforge.observability.metrics import Metrics
from eventforge.plugins.builtin import register_builtin_plugins
from eventforge.plugins.registry import PluginRegistry
from eventforge.runtime.pipeline import PipelineRuntime


@dataclass
class EngineOptions:
    metrics_port: int = 9600
    health_port: int = 9601


class Engine:
    def __init__(self, config: ProjectConfig, options: EngineOptions | None = None):
        self.config = config
        self.options = options or EngineOptions()
        self.metrics = Metrics()
        self.registry = PluginRegistry()
        register_builtin_plugins(self.registry)
        self.registry.load_entry_points()
        self.pipelines: list[PipelineRuntime] = [
            PipelineRuntime(spec=pipeline, registry=self.registry, metrics=self.metrics)
            for pipeline in config.pipelines
        ]
        self.health = HealthServer(port=self.options.health_port)
        self._stopping = False

    def start(self) -> None:
        Metrics.start_metrics_server(self.options.metrics_port)
        self.health.start()
        for pipeline in self.pipelines:
            pipeline.start()

    def wait(self, timeout: float | None = None) -> None:
        for pipeline in self.pipelines:
            pipeline.wait(timeout=timeout)

    def stop(self) -> None:
        if self._stopping:
            return
        self._stopping = True
        self.health.status["ready"] = False
        for pipeline in self.pipelines:
            pipeline.stop()
        self.health.stop()

    def run(self) -> None:
        def handle_signal(_sig, _frame):
            self.stop()

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
        self.start()
        self.wait()
