from __future__ import annotations

from queue import Queue
from pystash.config.loader import AppConfig, PipelineConfig
from pystash.observability.metrics import metrics
from pystash.plugins.base import PluginContext
from pystash.plugins.registry import registry


class PipelineRunner:
    def __init__(self, cfg: PipelineConfig):
        self.cfg = cfg
        self.ctx = PluginContext(pipeline_id=cfg.pipeline_id)
        self.queue = Queue(maxsize=10000)

    def _build(self, kind: str, conf: dict):
        name = conf["plugin"]
        cls = registry.get(kind, name)
        return cls(conf, self.ctx)

    def run_once(self) -> None:
        inputs = [self._build("input", c) for c in self.cfg.inputs]
        filters = [self._build("filter", c) for c in self.cfg.filters]
        outputs = [self._build("output", c) for c in self.cfg.outputs]

        for inp in inputs:
            for event in inp.run():
                metrics.inc(f"{self.cfg.pipeline_id}.events_in")
                events = [event]
                for flt in filters:
                    next_events = []
                    for item in events:
                        next_events.extend(flt.process(item))
                    events = next_events
                    if not events:
                        break
                if not events:
                    metrics.inc(f"{self.cfg.pipeline_id}.events_dropped")
                    continue
                for out in outputs:
                    out.send(events)
                metrics.inc(f"{self.cfg.pipeline_id}.events_out", len(events))


class Engine:
    def __init__(self, config: AppConfig):
        self.config = config

    def run(self) -> None:
        for pipe in self.config.pipelines:
            PipelineRunner(pipe).run_once()
